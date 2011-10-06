#!/bin/bash

. /etc/fdh/fdh.sh

set -x

RSYNC=`which $RSYNCCOMMAND`

$RSYNC $RSYNCOPTIONS -e "$RSYNCSSH" $RSYNCSOURCE "$RSYNCDEST"

