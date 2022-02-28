#!/bin/bash

COWRIE="tags/v2.3.0"

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 1 ] && [ "$#" -ne 2 ]; then
    echo "Missing PREFIX parameter. Usage: install_learner.sh PREFIX REINSTALL"
    echo "REINSTALL is optional and can be YES or NO. If YES reinstall learner even if already installed."
    exit 1
fi

REINSTALL=$2

# where things are installed
PREFIX=$(realpath $1)
mkdir -p $PREFIX

echo "checking out cowrie base code"
cd $PREFIX

# if learner is already installed within PREFIX/cowrie
# don't do anything
# but prompt rerun with parameter if you want to remove and reinstall learner

if [ -d "cowrie/" ] && echo "Directory cowrie/ exists."; then

    if [ "$REINSTALL" = "YES" ]; then
        # Remove old learner installation 
        # Typically inside PREFIX/cowrie
        rm -rf cowrie/
    else
        echo "Learner installation already exists in PREFIX/cowrie."
        echo "If you want to overwrite it run install_learner.sh PREFIX YES"
        exit 1
    fi
fi

git clone https://github.com/cowrie/cowrie
cd cowrie
git checkout $COWRIE 2>&1>/dev/null
cd -

pip3 install virtualenv
virtualenv --python=python3 cannypot-env
source cannypot-env/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade -r $DIR/requirements.txt

# Copy customized cowrie files as well as the learning
cp -R $DIR/* $PREFIX/cowrie/
