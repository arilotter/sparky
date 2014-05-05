#!/bin/bash
source config.sh

echo "Playing $1"

echo 'Starting btcat...'
./btcat "$1" 0 >"$torrent_fifo" &

echo 'Starting omxplayer'
tail -f $input_fifo | $omx $torrent_fifo
exit 0
