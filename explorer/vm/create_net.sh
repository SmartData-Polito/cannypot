#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# virtual backend network
NETNAME=$(cat $DIR/virsh.xml | grep -oPm1 "(?<=<name>)[^<]+")

# stop virtual machines and destroy the virtual network
VMS=$( virsh list | tail -n +3 | head -n -1 | awk '{ print $2; }' )
for m in $VMS ; do
    virsh shutdown "$m"
done
echo "deleting network" $NETNAME
virsh net-destroy $NETNAME && true

# start services relying on iptables
systemctl restart libvirtd

# recreate the virtual network and restart the VMs
virsh net-define $DIR/virsh.xml
virsh net-start $NETNAME
virsh net-autostart $NETNAME

for m in $VMS ; do
    virsh start "$m"
done
