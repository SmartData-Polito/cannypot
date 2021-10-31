# Explorer

For now this part should be run as **root**.

## Quickstart

Run the ``explorer/install.sh`` script:

```
/bin/bash explorer/install.sh
```

This script executes all the instructions explained in details in the next paragraphs:
1. Build the VMs for the controlled backend system
2. Run the explorer

When the script ends, you can run the explorer as:

```
python explorer/CannyExplorer.py
```

## Build the VMs for the controlled backend system

The explorer part processes commands, which are saved into the ``input`` directory (the path can be specified inside the `explorer/etc/explorer_config.cfg` file).
To do so, it asks for commands to other machines, relying on ``libvirt`` and ``qemu``. 

Therefore, a user from the sudo group, such as root, should install libvirt and add the user cowrie to it.
*Note that members of the sudo group are added automatically, but `cowrie` user is not, so we need to add him manually:*

```
sudo apt update
sudo apt install qemu-kvm libvirt-daemon-system
sudo apt install virtinst
sudo adduser cowrie libvirt
```

Each VM you want to work with should be created ahead of time and added to the ``explorer/etc/hosts.csv`` file, which is has 1 entry by default (ubuntu).
Inside ``explorer/vm`` all code and specifications for the vm can be found and modified if necessary. For the default behaviour, you can run from root:

```
/bin/bash create_net.sh
/bin/bash create_vm.sh ubuntu 00:00:00:00:00:AA ubuntu
```

These commands will create a virtual network called **explorernet** and a virtual machine inside it with ubuntu.


## Run the explorer

*If you want you can use the same virtual environment as the one used for the cowrie-learner: **cowrie-env**.
For using it, just remember to activate it:*.

```
virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate
```

To run the explorer locally (from ``cannypot`` directory) you should first install the requirements.

```
pip install --upgrade pip
pip install --upgrade -r explorer/requirements.txt
```

Then, you should be sure that all paths are as expected inside `explorer/etc/explorer_config.cfg` and
that the `explorer/config/ExplorerConfig.py` maps the correct configuration file .cfg (check the complete path).

To work, the explorer relies on the controlled backend system, which is composed of different virtual machines.
See the next section to know how to create them.
Once you have at least one active vm, you can run the explorer locally through:

```
python explorer/CannyExplorer.py
```
