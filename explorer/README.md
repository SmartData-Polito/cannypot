# Explorer

The Explorer must be run as **root**. It is recommended to run the Explorer in a different machine than the Learner. The Explore requires Libvirt to run the backend systems as virtual machines. Thus running the Explorer itself in a VM will result in a slow environment.

## Installation

Run:

```
$./explorer/install_explorer.sh PATH INSTALL_VM
```

This script:
1. Builds a sample VM as backend system (inside `PATH`) if `INSTALL_VM` is equal to `YES`
2. Deploys the Explorer at `PATH`

Other backend systems can be provided manually (instructions below).

The Explorer can be started with:

```
PATH/explorer/bin/explorer.sh
```

## Building Backend Systems

Each VM you want to work with should be created ahead of time and added to the ``explorer/etc/hosts.csv`` file.
To create them, information can be found in the ``explorer/vm`` directory.

For the default behaviour, look at the `explorer/install_explorer.sh` script:

```
create_net.sh
create_vm.sh <name> <MAC> <password> <prefix>
```

These commands will create a virtual network called as defined inside ``explorer/vm/virsh.xml`` and a virtual machine inside it with ubuntu.

## Explorer configurations

All configuration files are specified into:

* `explorer/etc/explorer_config.cfg`
* `explorer/src/core/config/ExplorerConfig.py`

In particular, the Explorer processes commands, which are saved into the ``input`` directory, asks for commands to the backend system, and save the outputs inside the ``output`` directory. 
