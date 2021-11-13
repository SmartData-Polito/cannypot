#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters. Usage:
create_vm.sh NAME MAC PASSWORD PATH"
    exit 1
fi

NAME=$1
MAC=$2
PASSWORD=$3
INSTPATH=$4

rm -rf /tmp/preseed.cfg
cat $DIR/preseed.cfg | sed s/PASSWORD/$PASSWORD/g > /tmp/preseed.cfg

virt-install \
    --name $NAME \
    --description $NAME \
    --ram 2048 \
    --vcpus 1 \
    --disk path=$INSTPATH/$NAME.img,size=15 \
    --os-type linux  \
    --os-variant ubuntu18.04 \
    --graphics none \
    --mac $MAC \
    --network network=honeynet \
    --location 'http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/' \
    --initrd-inject /tmp/preseed.cfg \
    --extra-args="ks=file:/preseed.cfg console=ttyS0"
