#!/bin/sh

. /etc/fdh/fdh.sh

LOG="$FDHPATH/log/fdh.log"
IDS=`cat $FDHPATH/files/id_to_mail`

HOUR=`date +%H`
BUFFER="$TMPDIR/log.buffer.$HOUR"
grep $HOUR $LOG > $BUFFER

OUTPUT=''

for ID in $IDS; do
  NAME=`cat $BUFFER | grep "Existing initialising with $ID" | sed -e "s/.*$ID //" | head -n 1`
  if [ "x$NAME" == "x" ]; then continue; fi
  LINE=`cat $BUFFER | grep "$NAME" | grep ' for users :' | wc -l`
  if [ $LINE -gt 0 ]; then
      OUTPUT="$OUTPUT$ID $NAME\n"
  fi
done

SOMETHING=`echo -e "$OUTPUT" | wc -l`
if [ $SOMETHING -gt 0 ]; then
    echo -e "$OUTPUT" | mail -s "FLICKR CHECK" "$MAIL"
fi
rm -f $BUFFER

