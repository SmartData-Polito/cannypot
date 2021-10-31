#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters. Usage:
create_vm.sh NAME MAC PASSWORD"
    exit 1
fi

NAME=$1
MAC=$2
PASSWORD=$3
MAC_NAME=$( echo $MAC | tr ":" "-")

NAME_FINAL=${NAME}-${MAC_NAME}

echo $NAME_FINAL

cat ./preseed.cfg | sed s/PASSWORD/$PASSWORD/g > /tmp/preseed.cfg

# Create dir if not exist
mkdir -p /mnt/vms

virt-install \
    --name $NAME_FINAL \
    --description $NAME_FINAL \
    --ram 2048 \
    --vcpus 1 \
    --disk path=/mnt/vms/$NAME_FINAL.img,size=15 \
    --os-type linux  \
    --os-variant ubuntu18.04 \
    --graphics none \
    --mac $MAC \
    --network network=explorernet \
    --location 'http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/' \
    --initrd-inject /tmp/preseed.cfg \
    --extra-args="ks=file:/preseed.cfg console=ttyS0"
