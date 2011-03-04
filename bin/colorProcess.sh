#!/bin/sh

. /etc/fdh/fdh.sh
$FLICKRDIR/bin/getProcessLogs.sh $1 | perl /root/bin/color.pl

