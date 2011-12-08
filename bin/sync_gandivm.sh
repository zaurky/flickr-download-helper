#!/bin/bash

. /etc/fdh/fdh.sh

RSYNC=`which $RSYNCCOMMAND`

echo $RSYNC $RSYNCOPTIONS -e "$RSYNCSSH" $RSYNCSOURCE "$RSYNCDEST"

