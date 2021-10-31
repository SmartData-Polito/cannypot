#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 1 ]; then
    echo "Missing PREFIX parameter. Usage: install_explorer.sh PREFIX"
    exit 1
fi

# where things are installed
PREFIX=$(realpath $1)
mkdir -p $PREFIX

cd $PREFIX

# Install libvirt and requirements
sudo apt install qemu-kvm libvirt-daemon-system
sudo apt install virtinst

# create a sample vm to demonstrate the Explorer
sudo /bin/bash $DIR/vm/create_net.sh
sudo /bin/bash $DIR/vm/create_vm.sh ubuntu 00:00:00:00:00:AA exppasswd $PREFIX

pip install virtualenv
virtualenv --python=python3 cannypot-env
source cannypot-env/bin/activate
pip install --upgrade pip
pip install --upgrade -r $DIR/requirements.txt
