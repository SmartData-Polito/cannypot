from config.ExplorerConfig import ExplorerConfig
import csv
import paramiko
import pathlib
import os
import hashlib
import time
import shutil
from datetime import datetime

'''
Sequence of operations:

- download list of machines to connect to
- try to connect
- download through ftp the list of unknown sequences file
- delete files that are equal
- move the distinct files into input directory of explorer

- take directory from the output directory of explorer
- create temp directories for the transfer, limiting the number of outputs and putting together equal outputs
- move all directories and save the commands already elaborated
- give privileges to the moved directories
'''


def get_frontends_list():
    machines_file = ExplorerConfig().get('file_transfer', 'frontends_file')
    frontends = []
    with open(machines_file, 'r') as file:
        reader = csv.reader(file, delimiter=",")
        next(reader)
        for row in reader:
            host = dict()
            host['address'] = row[0]
            host['port'] = row[1]
            host['user'] = row[2]
            host['password'] = row[3]
            frontends.append(host)
    return frontends


def download_unknown_cmds_file(frontends_list):
    new_commands_directory = ExplorerConfig().get('file_transfer', 'new_commands_path')
    tmp_input_dir = ExplorerConfig().get('file_transfer', 'tmp_input_dir')
    pathlib.Path(tmp_input_dir).mkdir(exist_ok=True)
    for frontend in frontends_list:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        frontend_machine_ip = frontend['address']
        frontend_port = frontend['port']
        frontend_host = frontend['user']
        frontend_password = frontend['password']
        try:
            ssh.connect(hostname=frontend_machine_ip, port=frontend_port, username=frontend_host,
                        password=frontend_password, timeout=2)
            print('Connected to {} \n'.format(frontend_machine_ip))
            write_log('Connected to {}'.format(frontend_machine_ip))
            ftp = ssh.open_sftp()
            files_list = sorted(ftp.listdir(path=new_commands_directory))
            for file in files_list[:-1]:
                ftp.get(new_commands_directory + file, tmp_input_dir + file)
                ftp.remove(new_commands_directory + file)
                print('Downloaded file {} from {}'.format(file, frontend_machine_ip))
                write_log('Downloaded file {} from {}'.format(file, frontend_machine_ip))
            ftp.close()
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException) as e:
            print('Error in downloading files: {}'.format(e))
            write_log('Error in downloading files: {}'.format(e))
        finally:
            ftp.close()
            ssh.close()


def filter_and_move_files():
    tmp_input_dir = ExplorerConfig().get('file_transfer', 'tmp_input_dir')
    backend_input_dir = ExplorerConfig().get('fs', 'input_dir')
    distinct_files = list()
    print('Filter equal files and move into {}'.format(backend_input_dir))
    write_log('Filter equal files and move into {}'.format(backend_input_dir))
    for file in os.listdir(tmp_input_dir):
        with open(tmp_input_dir + file, 'rb') as file_to_read:
            fd = file_to_read.read()
            file_to_read.close()
        hash = hashlib.md5(fd).hexdigest()
        if hash in distinct_files:
            print('File {} with hash {} duplicated'.format(file, hash))
            write_log('File {} with hash {} duplicated'.format(file, hash))
            os.remove(tmp_input_dir + file)
        else:
            distinct_files.append(hash)
            print('File {} with hash {} non duplicated'.format(file, hash))
            write_log('File {} with hash {} non duplicated'.format(file, hash))
            os.rename(tmp_input_dir + file, backend_input_dir + 'aaa' + file)
            # TODO remove aaa


def upload_outputs_to_frontend(frontends_list):
    frontend_new_outputs_dir = ExplorerConfig().get('file_transfer', 'new_outputs_path')
    backend_output_dir = ExplorerConfig().get('fs', 'output_dir')
    backend_backups_dir = ExplorerConfig().get('file_transfer', 'backup_outputs_dir')

    dir_list = os.listdir(backend_output_dir)
    filtered_dir_list = [d for d in dir_list if time.time() - os.path.getmtime(backend_output_dir + d) > 60 * 3]
    for frontend in frontends_list:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        frontend_machine_ip = frontend['address']
        frontend_port = frontend['port']
        frontend_host = frontend['user']
        frontend_password = frontend['password']
        print('Send new outputs to {}'.format(frontend_machine_ip))
        write_log('Send new outputs to {}'.format(frontend_machine_ip))
        try:
            ssh.connect(hostname=frontend_machine_ip, port=frontend_port, username=frontend_host,
                        password=frontend_password, timeout=2)
            ftp = ssh.open_sftp()
            for direc in filtered_dir_list:
                if os.listdir(backend_output_dir + direc):
                    ftp.mkdir(frontend_new_outputs_dir + direc)
                    ftp.chmod(frontend_new_outputs_dir + direc, 0o777)
                    for file in os.listdir(backend_output_dir + direc):
                        ftp.put(backend_output_dir + direc + '/' + file, frontend_new_outputs_dir + direc + '/' + file)
                        print('Send files {} to {}:{}'.format(file, frontend_machine_ip,
                                                             frontend_new_outputs_dir + '/' + direc))
                        write_log('Send files {} to {}:{}'.format(file, frontend_machine_ip,
                                                                 frontend_new_outputs_dir + '/' + direc))
                        ftp.chmod(frontend_new_outputs_dir + direc + '/' + file, 0o777)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException) as e:
            print('Error in uploading files: {}'.format(e))
            write_log('Error in uploading files: {}'.format(e))
        finally:
            ftp.close()
            ssh.close()
    for d in filtered_dir_list:
        if os.listdir(backend_output_dir + d):
            os.rename(backend_output_dir + d, backend_backups_dir + d)
        else:
            shutil.rmtree(backend_output_dir + d)


def write_log(message):
    file_log = ExplorerConfig().get('file_transfer', 'log_file')
    with open(file_log, 'a') as file:
        now = datetime.now()
        line = now.strftime("%Y%m%d %H:%M:%S") + ' - ' + message + '\n'
        file.writelines(line)
        file.close()


def Main():
    write_log('Starting file transfer service.')
    print('Starting file transfer service.')
    frontends_list = get_frontends_list()
    download_unknown_cmds_file(frontends_list)
    filter_and_move_files()

    upload_outputs_to_frontend(frontends_list)
    write_log('Finished file transfer routine')
    print('Finished file transfer routine')


if __name__ == '__main__':
    Main()
