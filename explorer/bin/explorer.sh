#!/bin/bash

DEFAULT_VIRTUAL_ENV=cannypot-env

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR=$(realpath $DIR/../../)

source $ROOTDIR/$DEFAULT_VIRTUAL_ENV/bin/activate
$ROOTDIR/explorer/CannyExplorer.py
