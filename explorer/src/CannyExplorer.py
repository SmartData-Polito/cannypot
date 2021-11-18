#!/usr/bin/python

import os
import time
import pathlib
from hosts import utils

from config.ExplorerConfig import ExplorerConfig

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

        root_path = os.path.abspath(os.path.dirname(__file__))

        # paths to be processed
        self.paths = []

        # initialize the log system
        log_dir = root_path + "/" + ExplorerConfig().get('log', 'explorer_log_dir')
        log_file = log_dir + ExplorerConfig().get('log', 'explorer_log_file')
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        log.startLogging(DailyLogFile.fromFullPath(log_file))

        # read the list of backend hosts
        backend_conf = ExplorerConfig().get('backend', 'hosts')
        self.hosts_list = utils.get_hosts_infos(backend_conf, log)

        # config the input / output folders
        self.output_dir = root_path + "/" + ExplorerConfig().get('backend', 'output_dir')
        self.input_dir = root_path + "/" + ExplorerConfig().get('backend', 'input_dir')
        pathlib.Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.input_dir).mkdir(parents=True, exist_ok=True)

        # load all files already in the input folder

        for filename in os.listdir(path=self.input_dir):
            log.msg("[explorer] adding new file to processing queue %s " % filename)
            self.paths.append(filepath.FilePath(self.input_dir + filename))

        # register to inotify to watch the folder for more files
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(filepath.FilePath(self.input_dir), callbacks=[self.notify])

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

    def process_file(self):
        if self.paths:
            # Get the first path from the queue
            filename = self.paths[0].path

            log.msg("[explorer] processing %s queue size %d" % (filename, len(self.paths)))

            #TODO: here we make N parallel clients asynchronously
            for host in self.hosts_list:
                #domain = utils.create_vm_snapshot(host, filename, log, reactor)
                #if domain:
                factory = CannyClientFactory(host, utils.get_cmds_list(filename), log)
                factory.protocol = ClientTransport
                log.msg("[%s] connecting to backend on [%s:%s]" %(host['vm_name'], host['address'], host['port']))
                reactor.connectTCP(host['address'], int(host['port']), factory)
                log.msg("[%s] complete backend cycle on [%s:%s]" %(host['vm_name'], host['address'], host['port']))
                #if False:
                    # shut the VM down
                    #utils.shutoff_vm(host['vm_name'], domain, log)
                    #os.remove(filename)
                    #log.msg("removing %s " % filename)

            #TODO: join all clients, stop factory and delete file.

            del self.paths[0]
            log.msg("[explorer] finished %s queue size %d" % (filename, len(self.paths)))

            # Schedule this function to do more work
            if self.paths:
                reactor.callLater(0, self.process_file)

if __name__ == "__main__":
    cannypot = CannyExplorer()
