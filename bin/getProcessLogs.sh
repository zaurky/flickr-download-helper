#!/bin/bash

. /etc/fdh/fdh.sh

PROCESS_ID=$1
if [ "x$2" == "x" ]; then
    DATE=""
else
    DATE=".$2.0"
fi

ID=`grep "running as $PROCESS_ID" "$FLICKRDIR/log/fdh.log$DATE" | awk '{print $4}' | sed -e 's/://'`
grep $ID "$FLICKRDIR/log/fdh.log$DATE"

