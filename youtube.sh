#!/bin/bash

source config.sh

echo "Playing $1"
tail -f $input_fifo | $omx $(youtube-dl --max-quality 35 -g $1)
exit 0
