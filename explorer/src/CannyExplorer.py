#!/usr/bin/python

import os
import time
import pathlib
from hosts import utils
from config.ExplorerConfig import ExplorerConfig
from ssh.Transport import ClientTransport
from ssh.CannyClientFactory import CannyClientFactory
from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor
from twisted.python.logfile import DailyLogFile

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
        pathlib.Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.input_dir = root_path + "/" + ExplorerConfig().get('backend', 'input_dir')
        pathlib.Path(self.input_dir).mkdir(parents=True, exist_ok=True)

        self.loop = task.LoopingCall(self.get_file_fn)
        self.loop.start(ExplorerConfig().getint('general', 'loop_frequency'))

        log.msg("Explorer setup completed")

        reactor.run()

    def produce_outputs_for_file(self, filename):
        cmds = utils.get_cmds_list(self.input_dir + '/' + filename)
        for host in self.hosts_list:
            utils.create_vm_snapshot(host['vm_name'], log)
            continue


            factory = CannyClientFactory(cmds=cmds, server=host['vm_name'], password=host['password'])
            factory.protocol = ClientTransport
            log.msg(host['vm_name'], " - connecting to backend on ", host['address'], host['port'])
            reactor.connectTCP(host['address'], int(host['port']), factory)
            log.msg(host['vm_name'], " - complete backend cycle")
        os.remove(self.input_dir + '/' + filename)

    def get_file_fn(self):
        log.msg("starting an explorer cycle")
        if ExplorerConfig().getboolean('general', 'enable_explorer'):
            files_list = sorted(os.listdir(path=self.input_dir))
            if files_list:
                log.msg("start producing outputs for file: ", files_list[0])
                self.produce_outputs_for_file(files_list[0])
        log.msg("complete an explorer cycle")

if __name__ == "__main__":
    CannyExplorer()
