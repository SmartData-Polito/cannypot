# Install libvirt and run create_vm.sh to create all default vms
# And add files to hosts.csv and frontends.csv or viceversa
# something about MAC addresses
sudo apt update
sudo apt install qemu-kvm libvirt-daemon-system
sudo apt install virtinst
sudo adduser cowrie libvirt

cd explorer/vm

/bin/bash create_net.sh
/bin/bash create_vm.sh ubuntu 00:00:00:00:00:AA ubuntu

cd ../..

virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate

pip install --upgrade pip
pip install --upgrade -r explorer/requirements.txt
