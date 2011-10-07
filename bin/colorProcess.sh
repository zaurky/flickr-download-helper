#!/bin/bash

. /etc/fdh/fdh.sh
$FLICKRDIR/bin/getProcessLogs.sh $1 $2 | perl /root/bin/color.pl

