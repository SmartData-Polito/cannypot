#!/usr/bin/env python3

import os
import time
import pathlib
from vms import manager

import configparser

from twisted.python import log
from twisted.python.logfile import DailyLogFile
from twisted.python import filepath

from twisted.internet import task
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import inotify

from ssh.Transport import ClientTransport
from ssh.CannyClientFactory import CannyClientFactory

class CannyExplorer:

    def __init__(self):

        self.working = 0

        root_path = os.path.abspath(os.path.dirname(__file__))
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.config.read(root_path + "/etc/explorer.cfg")

        # paths to be processed
        self.paths = []

        # initialize the log system
        log_dir = root_path + "/" + self.config.get('log', 'explorer_log_dir')
        log_file = log_dir + self.config.get('log', 'explorer_log_file')
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        log.startLogging(DailyLogFile.fromFullPath(log_file))

        # read the list of backend hosts
        backend_conf = self.config.get('backend', 'hosts')
        self.hosts_list = manager.get_hosts_infos(root_path + "/" + backend_conf, log)

        # config the input / output folders
        self.config.output_dir = root_path + "/" + self.config.get('backend', 'output_dir')
        self.config.input_dir = root_path + "/" + self.config.get('backend', 'input_dir')
        self.config.json_dir = root_path + "/" + self.config.get('backend', 'json_dir')
        pathlib.Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.config.input_dir).mkdir(parents=True, exist_ok=True)

        # load all files already in the input folder

        for filename in os.listdir(path=self.config.input_dir):
            log.msg("[explorer] adding new file to processing queue %s " % filename)
            self.paths.append(filepath.FilePath(self.config.input_dir + filename))

        # register to inotify to watch the folder for more files
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(filepath.FilePath(self.config.input_dir), callbacks=[self.notify])

        log.msg("[explorer] setup complete")
        reactor.callLater(2, self.process_file)
        reactor.addSystemEventTrigger('before', 'persist', self.shutdown_process)
        reactor.run(installSignalHandlers=True)

    def generic_error(self, err):
        log.msg(err)

    def notify(self, ignored, filename, mask):
        if mask == 256:
            self.paths.append(filename)
            reactor.callLater(0, self.process_file)

    def shutdown_process(self):
        log.msg("[explorer] shutting down")
        for host in self.hosts_list:
            manager.shutoff_vm(host['vm_name'], host['domain'], log)

    def vm_complete(self, host, domain):
        #if host['bootfreq'] == host['session_counter']:
            # shut the VM down
        manager.shutoff_vm(host['vm_name'], domain, log)
            #host['session_counter'] = 0
        #else:
            #host['session_counter'] = host['session_counter'] + 1

        self.working -= 1

        log.msg("[%s] complete backend cycle on [%s:%s]" % (host['vm_name'], host['address'], host['port']))

        if not self.working:
            # we come here when all VMS are done
            # thus after rejoin we delete the file and move on
            del self.paths[0]
            log.msg("[explorer] finished %s queue size %d" % (self.filename, len(self.paths)))

            # remove the input file
            os.remove(self.filename)
            log.msg("removing %s " % self.filename)

            # Schedule to process the next file
            if self.paths:
                reactor.callLater(0, self.process_file)

    def process_file(self):
        if self.paths and not self.working:
            # Get the first path from the queue
            self.filename = self.paths[0].path
            cmds = manager.get_cmds_list(self.filename)
            if not cmds:
                log.msg("%s input commands empty" % (self.filename))

                # remove the invalid file
                del self.paths[0]
                os.remove(self.filename)
                log.msg("removing %s " % self.filename)

                reactor.callLater(0, self.process_file)
                return

            log.msg("[explorer] processing %s queue size %d" % (self.filename, len(self.paths)))

            for host in self.hosts_list:
                #if not host['domain'] or host['bootfreq'] == host['session_counter']:
                domain = manager.create_vm_snapshot(host, self.filename, log, reactor)
                host['domain'] = domain

                if host['domain']:
                    self.working += 1
                    factory = CannyClientFactory(host, host['domain'], cmds, log, self)
                    factory.protocol = ClientTransport
                    log.msg("[%s] connecting to backend on [%s:%s]" % (host['vm_name'], host['address'], host['port']))
                    reactor.connectTCP(host['address'], int(host['port']), factory)
                else:
                    # if only some machines fail we keep going anyway
                    log.err("[%s] fail to create a VM [%s:%s]" % (host['vm_name'], host['address'], host['port']))

            # we could not start a single VM retry in 60s
            if not self.working:
                log.msg("failed to run all VMs - will retry in 60s")
                reactor.callLater(60, self.process_file)

if __name__ == "__main__":
    cannypot = CannyExplorer()
