#!/bin/bash

OUTDIR="/home/bas/virgin-media-router-status/data"
STATUS_URL="http://192.168.100.1/getRouterStatus"

stamp=`date --iso-8601=seconds`
outfile="$OUTDIR/virgin-media-router-status-$stamp.json"

wget -O "$outfile" "$STATUS_URL"
