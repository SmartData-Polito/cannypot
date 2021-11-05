import paramiko
import sys
import getopt
import csv
import os
import time


def produce_output(host, port, username, password, command):
    print("[DEBUG] Creating paramiko client")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for x in range(5):
        try:
            print("[DEBUG] Try connection")
            ssh.connect(hostname=host, port=port, username=username, password=password)
            break
        except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.AuthenticationException, paramiko.SSHException) as e:
            print("[DEBUG] Entered paramiko exception")
            time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    return stdout.read().decode('utf-8').strip('\n')


def get_args():
    hosts_filename = 'hosts.csv'
    cmds_dir = 'input'
    output_dir = None
    argument_list = sys.argv[1:]
    short_options = "h:o:c:"
    long_options = ["hosts=", "out_dir=", "cmd_dir="]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--hosts"):
            hosts_filename = current_value
        elif current_argument in ("-o", "--output"):
            output_dir = current_value
        elif current_argument in ("-c", "--commands"):
            cmds_dir = current_value
    return hosts_filename, output_dir, cmds_dir


def get_hosts_infos(filename):
    hosts = []
    with open(filename, 'r') as hosts_file:
        reader = csv.reader(hosts_file, delimiter=",")
        next(reader)
        for row in reader:
            host = dict()
            host['address'] = row[0]
            host['port'] = row[1]
            host['user'] = row[2]
            host['password'] = row[3]
            host['vm_name'] = row[4]
            hosts.append(host)
    return hosts


def get_cmds_list(cmds_filename):
    cmds = []
    with open(cmds_filename, 'r') as cmds_file:
        reader = csv.reader(cmds_file, delimiter=" ")
        for row in reader:
            if row:
                cmd = dict()
                cmd['cmd'] = row[0]
                cmd['args'] = row[1:]
                cmd['complete_cmd'] = " ".join(row)
                cmds.append(cmd)
        cmds_file.close()
    return cmds


def create_vm_snapshot(vm_name):
    print("[DEBUG] Creating snapshot")
    # TODO should delete snapshot if already exists
    #os.system("virsh snapshot-delete --domain {} --snapshotname {}".format(vm_name, vm_name+"_fresh1"))
    #os.system("virsh shutdown {}".format(vm_name))
    # TODO or should call restore_vm_state if some expection occurs BUT WHERE OCCURS
    os.system("virsh snapshot-create-as --domain {} --name {}".format(vm_name, vm_name+"_fresh1"))
    os.system("virsh start {}".format(vm_name))


def restore_vm_state(vm_name):
    print("[DEBUG] Restore vm state and delete snapshot")
    os.system("virsh shutdown {}".format(vm_name))
    os.system("virsh snapshot-revert --domain {}  --snapshotname {}".format(vm_name, vm_name+"_fresh1"))
    os.system("virsh snapshot-delete --domain {} --snapshotname {}".format(vm_name, vm_name+"_fresh1"))
