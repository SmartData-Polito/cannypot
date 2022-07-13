#!/bin/bash

COWRIE="tags/v2.3.0"

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 1 ]; then
    echo "Missing PREFIX parameter. Usage: install.sh PREFIX"
    exit 1
fi

# where things are installed
PREFIX=$1
if [ -d "$PREFIX" ]
then
    echo  "Removing " $PREFIX
    rm -rf $PREFIX
fi
mkdir -p $PREFIX

# Temp directory where we apply the patches
if [ -d "$DIR/build" ]
then
    echo  "Removing " $DIR/build
    rm -rf $DIR/build
fi
mkdir $DIR/build

echo "checking out cowrie base code"
cd $DIR/build
git clone https://github.com/cowrie/cowrie
cd $DIR/build/cowrie
git checkout $COWRIE 2>&1>/dev/null

cd $PREFIX
pip install virtualenv
virtualenv --python=python3 cannypot-env
source cannypot-env/bin/activate
pip install --upgrade pip
pip install --upgrade -r $DIR/requirements.txt

echo "computing patches"
# python $DIR/patch/compute_patches.py

echo "Apply patch"
# python patch/apply_patches.py  # apply (only if cannypot code changes or cowrie changes)
# python patch/compare_patches.py  # compare if necessary (testing purposes)
# python patch/copy_files.py  # copy (only if apply has been made)


cp -R $DIR/build/cowrie $PREFIX/cannypot
rm -rf $DIR/build
