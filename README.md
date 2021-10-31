# CannyPot

Medium-interaction SSH honeypot enhanced with Reinforcement Learning and an Explorer to increase the knowledge of the honeypot on-the-fly. The Explorer relies on real systems deployed at controlled environment to learn possible ways to respond to unknown commands.

The schema of CannyPot is depicted in the following figure:

![Schema](architecture.png 'Schema')

## requirements

* Python 3
* pip (for Python 3)

The required python packages are then installed with pip.

## Installation

CannyPot is composed by two key parts:

1. [``Learner``](#learner)
2. [``Explorer``](#explorer)

In the following we report instructions to install the two components of CannyPot. Scripts in this repository deploy both components in a single machine for demonstration of the CannyPot capabilities. CannyPot is however designed to be deployed as a distributed system, with the Learner working as a front-end to receive attackers' attempts, and the Explorer operating in a backend (protected) environment to perform a deep analysis of the attackers' inputs.

### Learner

The Learner has been tested in Debian-like Linux (e.g., Ubuntu 20.04 or Debian 11). All the installation steps are performed by the script:

```
$ ./install_learner.sh
```

Some notices:

* The Learner should be run as a virtual machine, as it is the front-end exposed to attackers.

* The Learner consists of extensions made over the `cowrie` honeypot [[https://github.com/cowrie/cowrie]]. Our additions to Cowrie code base are in the ``learner`` directory. They are applied to the Cowrie base by the installation script, thus patching the code to include the CannyPot RL capabilities.

* The script creates a new user account (default `cowrie`). The Learner runs as the given user.

*

#### Quickstart



To run cowrie locally (from ``cannypot`` directory), you can follow the instructions inside ``cowrie-learner/INSTALL.rst``.
In summary, first you have to create a virtual environment (with conda or virtualenv), activate it and install the requirements:

```
virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install --upgrade -r cowrie-learner/requirements.txt
```

Make sure that in the file ``cowrie-learner/bin/cowrie`` these lines are present (note that the virtual env can also be set to venv or whatever name if necessary):

```
DEFAULT_VIRTUAL_ENV=cowrie-env
COWRIE_STDOUT=yes
```

Now, you are ready to run the honeypot!

```
cowrie-learner/bin/cowrie start
```

To connect to the honeypot through ssh and send commands, type:
```
ssh root@localhost -p 2222
```

See next section to know how to use **reinforcement learning** mode!

#### Cannypot configurations

Inside `cowrie-learner/etc/cowrie.cfg` you can find all variables to configure to work in rl mode.

In particular:

* `reinforcement_mode = true` to work with cowrie+rl. Put false if you want the normal behaviour of cowrie
* `reinforcement_state = single` to have cannypot saving just the last command as state of rl. Possible options are: 'single', 'multiple', 'multiple_out'
* `num_entry_states = 1` to select how many last n commands to consider for rl state. Single should be 1, multiple and multiple_out are set to 3 by default


#### Improvements to cowrie

With respect to cowrie (you can download the zip of this version at [cowrie-fee98d47d3042136951105297e62f919b39d7494](https://github.com/cowrie/cowrie/tree/fee98d47d3042136951105297e62f919b39d7494)), the following parts have been added to perform learning:

* `learner/src/cowrie/learning` directory contains the complete learning algorithm structure
* `learner/etc/cowrie.cfg` contains configuration to use cowrie as learning
* `learner/etc/userdb.txt` credentials to log into the honeypot
* `learner/bin/clear_status` script to remove files for learning statistics

Also, some parts of cowrie (inside learner directory) have been modified, such as:

* src/cowrie/ssh/factory.py
* src/cowrie/shell/avatar.py
* src/cowrie/shell/honeypot.py
* src/cowrie/shell/protocol.py

* src/twisted/plugins/cowrie_plugin.py
* src/cowrie/core/realm.py

* etc/cowrie.cfg.dist
* etc/.gitignore

* var/lib/cowrie/tty/.gitignore

* README.rst
* docs/README.rst
* requirements.txt

All these improvements are stored inside the ``learner`` directory, and are applied to cowrie and saved into the ``cowrie-learner`` directory.

### Explorer part

For now this part should be run as **root**.

#### Quickstart

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

#### Build the VMs for the controlled backend system

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


### Update cowrie-learner

To update the cowrie-learner to the newest cowrie version, you need to download this new version and merge it with the code inside the ``learner`` directory.
To do so we provide the patch code inside the ``patch`` directory.

The ``patch`` directory contains scripts to patch new versions of cowrie with the reinforcement learning part, which is stored inside the ``learner/patches`` directory and to copy other files (regarding RL algorithms) inside cowrie.
Once you pull this project from github, if cowrie has a new version you can automatically download the updated version of cowrie, add the RL part and run it!
This procedure can be done running the ``install_new_cowrie.sh`` shell script:

```
/bin/bash install_new_cowrie.sh
```

In this script, by default, these flags must have the following values:

```
flag_compute_patch=false
flag_patch=true
flag_clean=true
```

We hardcoded the tested version we used. If you want, you can comment this lines inside ``install_new_cowrie.sh`` and stick to the newest version:

```
# Checkout the version we used
# If you want to use the newest cowrie version, comment from HERE
cd cowrie
git checkout fee98d47d3042136951105297e62f919b39d7494
cd ..
# To HERE
```

-> TODO need to update patches with this version and THEN change the version and the checkout line into:
git checkout tags/v2.3.0

#### Additional information

If needed, inside ``patch/config.py`` the following directories for performing patching are specified:

* ``patch_dir_name``: where patch files are stored (*patch files*)
* ``original_dir_name``: original directory of the cowrie version on which modifications were made (*original cowrie*)
* ``latest_dir_name``: latest directory of the cowrie-learner (*cowrie-learner = original cowrie + modifications*)
* ``to_copy_dir_name``: file from which copy files from the learner to cowrie-learner (*learner = modifications*)
* ``target_dir_name``: new directory to which patches should be applied to obtain an updated version of the cowrie-learner (*updated cowrie*)
* ``patched_file_dir_name``: where the new patched files should be saved (*updated cowrie + modifications*)

These paths should not be changed unless strictly necessary.


## Notes

You can manage independently what is inside `cowrie-learner` and `explorer` directories. They can be opened and managed as two independent Python projects.

TODO need to define the usage of etc/frontends.csv file.
TODO make explorer work not with root (and also vms).
