import utils
import json
import paramiko
import os
import time

from config.ExplorerConfig import ExplorerConfig


class Explorer:
    def __init__(self):
        self.hosts_filename = ExplorerConfig().get('fs', 'host_filename')
        self.output_dir = ExplorerConfig().get('fs', 'output_dit')
        self.cmds_dir = ExplorerConfig().get('fs', 'input_dir')
        self.hosts_list = utils.get_hosts_infos(self.hosts_filename)
        self.counter = 0

    def produce_outputs_for_file(self, filename):
        cmds_filename = filename
        cmds = utils.get_cmds_list(self.cmds_dir + cmds_filename)
        print(cmds)
        output_list = {}
        # Prepare outputs data structure
        for cmd in cmds:
            output_list[cmd['complete_cmd']] = dict()
            output_list[cmd['complete_cmd']]['command'] = cmd['cmd']
            output_list[cmd['complete_cmd']]['args'] = cmd['args']
            output_list[cmd['complete_cmd']]['outputs'] = []

        # Produce outputs
        for host in self.hosts_list:
            utils.create_vm_snapshot(host['vm_name'])
            for cmd in cmds:
                output = utils.produce_output(host['address'], host['port'],
                                              host['user'], host['password'], cmd['complete_cmd'])
                output_list[cmd['complete_cmd']]['outputs'].append(output)
            utils.restore_vm_state(host['vm_name'])

        # Write outputs json
        if self.output_dir is not None:
            suffix = ExplorerConfig().get('file_transfer', 'new_outputs_suffix')

            output_filename = self.output_dir + suffix + str(self.counter)+'.json'
            print(list(output_list.values()))
            with open(output_filename, 'w') as output_file:
                json.dump(list(output_list.values()), output_file, indent=2)

    def get_file_fn(self):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        files_list = []
        try:
            # TODO Should move strings to external config file!
            # How this should work???
            ssh.connect(hostname=ExplorerConfig().get('cowrie', 'hostname'), username=ExplorerConfig().get('cowrie', 'hostname'), password=ExplorerConfig().get('cowrie', 'password'), timeout=2)
            ftp = ssh.open_sftp()
            # TODO this could throw error because paths may be incorrect (/ or not /?)
            new_commands_path = ExplorerConfig().get('file_transfer', 'new_commands_path')
            new_outputs_path = ExplorerConfig().get('file_transfer', 'new_outputs_path')

            files_list = sorted(ftp.listdir(path=new_commands_path))
            if files_list[:-1]:
                for file in files_list[:-1]:
                    input_dir = ExplorerConfig().get('fs', 'input_dir')
                    output_dir = ExplorerConfig().get('fs', 'output_dir')

                    ftp.get(new_commands_path + file, input_dir + file)
                    ftp.remove(new_commands_path + file)
                    self.produce_outputs_for_file(file)

                    suffix = ExplorerConfig().get('file_transfer', 'new_outputs_suffix')

                    ftp.put(output_dir+suffix+str(self.counter)+'.json',
                            new_outputs_path+suffix+str(self.counter)+'.json')
                    os.remove(output_dir+suffix+str(self.counter)+'.json')
                    self.counter += 1
            ftp.close()
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException) as e:
            return files_list

    def run(self):
        while True:
            self.get_file_fn()
            time.sleep(5)


if __name__ == '__main__':
    print('--------- Starting explorers process ---------')
    w = Explorer()
    w.run()
