#!/bin/bash

COWRIE="tags/v2.3.0"

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 1 ]; then
    echo "Missing PREFIX parameter. Usage: install_learner.sh PREFIX"
    exit 1
fi

# where things are installed
PREFIX=$(realpath $1)
mkdir -p $PREFIX

# TODO if prefix already exists and the learner is already installed
#      ask if you want to remove and reinstall or block the installation

echo "checking out cowrie base code"
cd $PREFIX
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
