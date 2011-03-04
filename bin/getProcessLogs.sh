#!/bin/sh

. /etc/fdh/fdh.sh

PROCESS_ID=$1

ID=`grep "running as $PROCESS_ID" "$FLICKRDIR/log/fdh.log" | awk '{print $4}' | sed -e 's/://'`
grep $ID "$FLICKRDIR/log/fdh.log"

