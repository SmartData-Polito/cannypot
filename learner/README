# Learner

The Learner has been tested in Debian-like Linux (e.g., Ubuntu 20.04 or Debian 11). All the installation steps are performed by the script:

```
$ ./learner/install_learner.sh PATH
```

Some notices:

* The system will be deployed at `PATH`

* The Learner should be run as a virtual machine, as it is the front-end exposed to attackers.

* The Learner consists of extensions made over the `cowrie` honeypot [[https://github.com/cowrie/cowrie]]. Our additions to Cowrie code base are in the ``learner`` directory. They are copied over the Cowrie base by the installation script. Scripts to provide the exact changes can be found in the ``patch'' folder.

* The learner should be installed and run as a normal user (not root)

```
sudo adduser --disabled-password cowrie
```

* See the Cowrie installation instructions for further details on how Cowrie is configured.

* To start CannyPot, run

```
PATH/cowrie/bin/cowrie start
```

* To connect to the honeypot through ssh and send commands, type:

```
ssh root@localhost -p 2222
```

## CannyPot configurations

### RL mode

Inside `PATH/cowrie/etc/cowrie.cfg` you can find all variables to configure CannyPot to work in RL mode.

In particular:

* `reinforcement_mode = true` sets CannyPot on. Put false if you want the normal behavior of cowrie
* `reinforcement_state = single` to have CannyPot saving just the last command as state of RL. Possible options are: 'single', 'multiple', 'multiple_out'
* `num_entry_states = 1` to select how many last n commands to consider for RL state. Single should be 1, multiple and multiple_out are set to 3 by default

### Foreground mode

To run learner in foreground mode, inside ``PATH/cowrie/bin/cowrie`` add:

```
COWRIE_STDOUT=yes
```
