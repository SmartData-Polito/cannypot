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

        # initialize the log system

        self.hosts_filename = ExplorerConfig().get('fs', 'host_filename')
        self.output_dir = ExplorerConfig().get('fs', 'output_dir')
        pathlib.Path(self.output_dir).mkdir(exist_ok=True)
        self.cmds_dir = ExplorerConfig().get('fs', 'input_dir')
        pathlib.Path(self.cmds_dir).mkdir(exist_ok=True)
        print("[DEBUG] 11. Obtain hosts info")
        self.hosts_list = utils.get_hosts_infos(self.hosts_filename)
        print("[DEBUG] 22. Start looping call")
        self.loop = task.LoopingCall(self.get_file_fn)
        print("[DEBUG] 33. Start loop")
        self.loop.start(ExplorerConfig().getint('functionality', 'loop_frequency'))
        print("[DEBUG] 44. Finish loop")
        log_file = ExplorerConfig().get('log', 'explorer_log_file')
        log_dir = ExplorerConfig().get('log', 'explorer_log_dir')
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        # TODO strange date format: to fix logs (maybe without twisted rotation)
        log.startLogging(DailyLogFile.fromFullPath(log_file))
        print("[DEBUG] 55. Started logging")
        # day = time.strftime("%Y%m%d")
        # log.startLogging(open(log_file + "." + day, 'w'))
        reactor.run()
        print("[DEBUG] 66. Finish reactor run")

    def produce_outputs_for_file(self, filename):
        cmds = utils.get_cmds_list(self.cmds_dir + '/' + filename)
        os.remove(self.cmds_dir + '/' + filename)
        for host in self.hosts_list:
            print("[DEBUG] 1. Create snapshot")
            utils.create_vm_snapshot(host['vm_name'])
            print("[DEBUG] HOST VM NAME", host['vm_name'])
            print("[DEBUG] HOST PASSWORD", host['password'])
            print("[DEBUG] 2. Create CannyClientFactory")
            factory = CannyClientFactory(cmds=cmds, server=host['vm_name'], password=host['password'])
            factory.protocol = ClientTransport
            print("[DEBUG] 3. Starting reactor connection TCP")
            reactor.connectTCP(host['address'], int(host['port']), factory)
            print("[DEBUG] 4. Finish reactor connection TCP")

    def get_file_fn(self):
        if ExplorerConfig().getboolean('functionality', 'enable_explorer'):
            input_dir = ExplorerConfig().get('fs', 'input_dir')
            files_list = sorted(os.listdir(path=input_dir))
            if files_list:
                print("[DEBUG] Start producing outputs for", files_list[0])
                self.produce_outputs_for_file(files_list[0])


if __name__ == "__main__":
    CannyExplorer()
