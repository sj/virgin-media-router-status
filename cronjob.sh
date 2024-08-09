#!/bin/bash
set -e

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR="`dirname "$SCRIPTPATH"`"

cd $SCRIPTDIR
./virgin-media-router-status.sh
./process-data.py
git commit -m "new data" data
git push
