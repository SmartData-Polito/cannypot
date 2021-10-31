# CannyPot

Medium-interaction SSH honeypot enhanced with Reinforcement Learning and an Explorer to increase the knowledge of the honeypot on-the-fly. The Explorer relies on real systems deployed at controlled environment to learn possible ways to respond to unknown commands.

The schema of CannyPot is depicted in the following figure:

![Schema](architecture.png 'Schema')

## Requirements

* Python 3
* pip (for Python 3)

The required python packages are then installed with pip.

## Installation

CannyPot is composed by two key parts:

1. [``Learner``](#learner)
2. [``Explorer``](#explorer)

In the following we report instructions to install the two components of CannyPot. Scripts in this repository deploy both components in a single machine for demonstration of the CannyPot capabilities. CannyPot is however designed to be deployed as a distributed system, with the Learner working as a front-end to receive attackers' attempts, and the Explorer operating in a backend (protected) environment to perform a deep analysis of the attackers' inputs.

## Learner

The Learner has been tested in Debian-like Linux (e.g., Ubuntu 20.04 or Debian 11). All the installation steps are performed by the script:

```
$ ./learner/install_learner.sh PATH
```

Some notices:

* The system will be deployed at `PATH`

* The Learner should be run as a virtual machine, as it is the front-end exposed to attackers.

* The Learner consists of extensions made over the `cowrie` honeypot [[https://github.com/cowrie/cowrie]]. Our additions to Cowrie code base are in the ``learner`` directory. They are copied over the Cowrie base by the installation script. Scripts to provide the exact changes can be found in the ``patch'' folder.

* See the Cowrie installation instructions for further details on how Cowrie is configured.

* To start CannyPot, run

```
cowrie-learner/bin/cowrie start
```

* To connect to the honeypot through ssh and send commands, type:

```
ssh root@localhost -p 2222
```

### CannyPot configurations

Inside `cowrie/etc/cowrie.cfg` you can find all variables to configure CannyPot to work in RL mode.

In particular:

* `reinforcement_mode = true` sets CannyPot on. Put false if you want the normal behavior of cowrie
* `reinforcement_state = single` to have CannyPot saving just the last command as state of RL. Possible options are: 'single', 'multiple', 'multiple_out'
* `num_entry_states = 1` to select how many last n commands to consider for RL state. Single should be 1, multiple and multiple_out are set to 3 by default

## Explorer

The Explorer must be run as **root**. It is recommended to run the Explorer in a different machine than the Learner. The Explore requires Libvirt to run the backend systems as virtual machines. Thus running the Explorer itself in a VM will result in a slow environment.

### Installation

Run:

```
$./explorer/install_explorer.sh PATH
```

This script:
1. Builds a sample VM as backend system (inside `PATH`)
2. Deploys the Explorer at `PATH`

Other backend systems can be provided manually (instructions below).

The Explorer must be started manually. Run:

```
python explorer/CannyExplorer.py
```

### Building Backend Systems

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


#### Run the explorer

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

