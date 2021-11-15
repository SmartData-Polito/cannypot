#!/usr/bin/python

import os
import time
import pathlib
from hosts import utils

from ssh.Transport import ClientTransport
from config.ExplorerConfig import ExplorerConfig
from ssh.CannyClientFactory import CannyClientFactory

from twisted.python import log
from twisted.python.logfile import DailyLogFile
from twisted.python import filepath

from twisted.internet import task
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import inotify

from twisted.protocols import basic
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

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
        self.hosts_list = utils.get_hosts_infos(backend_conf)

        # config the input / output folders
        self.output_dir = root_path + "/" + ExplorerConfig().get('backend', 'output_dir')
        self.input_dir = root_path + "/" + ExplorerConfig().get('backend', 'input_dir')
        pathlib.Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.input_dir).mkdir(parents=True, exist_ok=True)

        # load all files already in the input folder

        for filename in os.listdir(path=self.input_dir):
            log.msg("adding new file to processing queue %s " % filename)
            self.paths.append(filename)

        # register to inotify to watch the folder for more files
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(filepath.FilePath(self.input_dir), callbacks=[self.notify])

        log.msg("explorer setup completed")
        reactor.callLater(10, self.process_file)
        reactor.addSystemEventTrigger('before', 'shutdown', self.shutdown_process)
        reactor.run()

    def generic_error(self, err):
        log.msg(err)

    def notify(self, ignored, filename, mask):
        if mask == 256:
            self.paths.append(filename)
            reactor.callLater(0, self.process_file)

    def shutdown_process(self):
        log.msg("explorer is shutting down (wait)")


    def process_file(self):
        if self.paths and reactor.running:
            # Get the first path from the queue
            filename = self.paths[0]

            log.msg("processing %s queue size %d" % (str(filename), len(self.paths)))

            for host in self.hosts_list:
                if utils.create_vm_snapshot(host['vm_name'], log):
                    os.remove(self.input_dir + '/' + filename)

            #factory = CannyClientFactory(cmds=cmds, server=host['vm_name'], password=host['password'])
            #factory.protocol = ClientTransport
            #log.msg(host['vm_name'], " - connecting to backend on ", host['address'], host['port'])
            #reactor.connectTCP(host['address'], int(host['port']), factory)
            #log.msg(host['vm_name'], " - complete backend cycle")

            del self.paths[0]
            log.msg("finished %s queue size %d" % (str(filename), len(self.paths)))

            # Schedule this function to do more work, if there's still work
            # to be done.
            if self.paths:
                reactor.callLater(0, self.process_file)

if __name__ == "__main__":
    CannyExplorer()
