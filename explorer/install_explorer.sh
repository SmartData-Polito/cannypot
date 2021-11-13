#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 1 ] && [ "$#" -ne 2 ]; then
    echo "Missing parameters. Usage: install_explorer.sh PREFIX INSTALL_VM"
    echo "INSTALL_VM can be YES or NO (default). Install a sample VM in the backend."
    exit 1
fi

VMINSTALL=$2

# where things are installed
PREFIX=$(realpath $1)
mkdir -p $PREFIX
cd $PREFIX

if [ "$VMINSTALL" = "YES" ]; then

    # Install libvirt and requirements
    sudo apt install qemu-kvm libvirt-daemon-system
    sudo apt install virtinst

    sudo sed -i 's/#user = "root"/user = "root"/' /etc/libvirt/qemu.conf
    sudo sed -i 's/#group = "root"/group = "root"/' /etc/libvirt/qemu.conf

    # create a sample vm to demonstrate the Explorer
    sudo /bin/bash $DIR/vm/create_net.sh
    sudo /bin/bash $DIR/vm/create_vm.sh ubuntu 00:00:00:00:00:AA exppasswd $PREFIX

fi

# pip install virtualenv
# virtualenv --python=python3 cannypot-env
# source cannypot-env/bin/activate
# pip install --upgrade pip
# pip install --upgrade -r $DIR/requirements.txt

# copy explorer files
mkdir -p $PREFIX/explorer
cp -r $DIR/etc $DIR/src/* $DIR/bin $PREFIX/explorer
