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

class CannyExplorer:

    def __init__(self):

        root_path = os.path.abspath(os.path.dirname(__file__))

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
        self.file_queue = defer.DeferredQueue()
        for input in os.listdir(path=self.input_dir):
            self.file_queue.put(input)

        # register to inotify to watch the folder for more files
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(filepath.FilePath(self.input_dir), callbacks=[self.notify])

        log.msg("explorer setup completed")
        reactor.run()

    def generic_error(self, err):
        log.msg(err)

    def process_file(self, file_path):
        log.msg("process_file")
        pass

        #cmds = utils.get_cmds_list(self.input_dir + '/' + filename)
        #for host in self.hosts_list:
            #if utils.create_vm_snapshot(host['vm_name'], log):
                #os.remove(self.input_dir + '/' + filename)

        #factory = CannyClientFactory(cmds=cmds, server=host['vm_name'], password=host['password'])
        #factory.protocol = ClientTransport
        #log.msg(host['vm_name'], " - connecting to backend on ", host['address'], host['port'])
        #reactor.connectTCP(host['address'], int(host['port']), factory)
        #log.msg(host['vm_name'], " - complete backend cycle")


    def notify(self, ignored, filepath, mask):
        if mask == 256:
            self.file_queue.put(filepath)
            log.msg("adding new file to processing queue %s " % filepath)


if __name__ == "__main__":
    CannyExplorer()
