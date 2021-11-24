import paramiko
import sys
import getopt
import csv
import os
import time
import libvirt

def get_hosts_infos(filename, log):
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
            log.msg("registering backend: ", host['vm_name'], host['address'], host['port'])
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

def shutoff_vm(vm_name, dom, log):
    i = 0
    try:
        while dom.isActive():
            if i == 0:
                log.msg(vm_name, "domain active, shutting it down")
                dom.shutdown()
            elif i == 60:
                log.msg(vm_name, "forcing shutdown after 60s")
                dom.destroy()
            time.sleep(1)
            i += 1
    except libvirt.libvirtError as e:
        log.err(repr(e))
        return None

def create_vm_snapshot(host, filename, log, reactor):
    log.msg(host['vm_name'], "creating backend snapshot")

    # connect to virsh backend
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        log.err(repr(e))
        return None

    dom = None
    try:
        dom = conn.lookupByName(host['vm_name'])
    except libvirt.libvirtError as e:
        log.err(repr(e))
        return None

    # shut the VM down if it remained active during last cycle
    shutoff_vm(host['vm_name'], dom, log)


    # check if current snapshot exists and creates one otherwise
    try:
        snap = dom.snapshotLookupByName("clean_vm_state")
        log.msg(host['vm_name'], "has a clean_vm_state snapshot - reverting")

        # reverse to the clean snapshot
        dom.revertToSnapshot(snap)

    except libvirt.libvirtError as e:
        log.msg(host['vm_name'], "has not a clean_vm_state snapshot")
        SNAPSHOT_XML_TEMPLATE = """<domainsnapshot>
                                      <name>{snapshot_name}</name>
                                    </domainsnapshot>
                                """
        dom.snapshotCreateXML(
          SNAPSHOT_XML_TEMPLATE.format(snapshot_name="clean_vm_state"),
                  libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC
        )
        snap = dom.snapshotLookupByName("clean_vm_state")

    #TODO: start domain. Preparing first the exceptions
    return dom

