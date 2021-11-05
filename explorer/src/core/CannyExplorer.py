#!/usr/bin/python

from hosts import utils
from twisted.internet import reactor
from ssh.Transport import ClientTransport
from ssh.CannyClientFactory import CannyClientFactory
import os
import pathlib
from twisted.python import log
from twisted.internet import task
from config.ExplorerConfig import ExplorerConfig
from twisted.python.logfile import DailyLogFile
import time


class CannyExplorer:
    def __init__(self):
        self.hosts_filename = ExplorerConfig().get('fs', 'host_filename')
        self.output_dir = ExplorerConfig().get('fs', 'output_dir')
        pathlib.Path(self.output_dir).mkdir(exist_ok=True)
        self.cmds_dir = ExplorerConfig().get('fs', 'input_dir')
        pathlib.Path(self.cmds_dir).mkdir(exist_ok=True)
        print("[DEBUG] Obtain hosts info")
        self.hosts_list = utils.get_hosts_infos(self.hosts_filename)
        print("[DEBUG] Start looping call")
        self.loop = task.LoopingCall(self.get_file_fn)
        print("[DEBUG] Start loop")
        self.loop.start(ExplorerConfig().getint('functionality', 'loop_frequency'))
        print("[DEBUG] Finish loop")
        log_file = ExplorerConfig().get('log', 'explorer_log_file')
        log_dir = ExplorerConfig().get('log', 'explorer_log_dir')
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        # TODO strange date format: to fix logs (maybe without twisted rotation)
        log.startLogging(DailyLogFile.fromFullPath(log_file))
        print("[DEBUG] Started logging")
        # day = time.strftime("%Y%m%d")
        # log.startLogging(open(log_file + "." + day, 'w'))
        reactor.run()
        print("[DEBUG] Finish reactor run")

    def produce_outputs_for_file(self, filename):
        cmds = utils.get_cmds_list(self.cmds_dir + '/' + filename)
        os.remove(self.cmds_dir + '/' + filename)
        for host in self.hosts_list:
            print("[DEBUG] Create snapshot")
            utils.create_vm_snapshot(host['vm_name'])
            print("[DEBUG] Create CannyClientFactory")
            factory = CannyClientFactory(cmds=cmds, server=host['vm_name'], password=host['password'])
            factory.protocol = ClientTransport
            print("[DEBUG] Starting reactor connection TCP")
            reactor.connectTCP(host['address'], int(host['port']), factory)
            print("[DEBUG] Finish reactor connection TCP")

    def get_file_fn(self):
        if ExplorerConfig().getboolean('functionality', 'enable_explorer'):
            input_dir = ExplorerConfig().get('fs', 'input_dir')
            files_list = sorted(os.listdir(path=input_dir))
            if files_list:
                print("[DEBUG] Start producing outputs for", files_list[0])
                self.produce_outputs_for_file(files_list[0])


if __name__ == "__main__":
    CannyExplorer()
