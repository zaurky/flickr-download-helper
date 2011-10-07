#!/bin/bash

. /etc/fdh/fdh.sh

LOG="$FLICKRDIR/log/fdh.log"
DATE=`date +%Y%m%d`
SUF="0"

while [ -f "$LOG.$DATE.$SUF" ]; do
    let SUF=$SUF+1
done

mv "$LOG" "$LOG.$DATE.$SUF"

touch "$LOG"
chmod 666 "$LOG"

