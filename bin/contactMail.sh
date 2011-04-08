#!/bin/sh

. /etc/fdh/fdh.sh

FDHPATH=$FLICKRDIR
LOG="$FDHPATH/log/fdh.log"
IDS=`cat $FDHPATH/files/id_to_mail`

DATE=`date +%Y-%m-%d`
HOUR=`date +%H`
BUFFER="$TMPDIR/log.buffer.$HOUR"
grep "$DATE $HOUR:" $LOG > $BUFFER

OUTPUT=''

for ID in $IDS; do
  NAME=`cat $BUFFER | grep "Existing initialising with $ID" | sed -e "s/.*$ID //" | head -n 1`
  if [ "x$NAME" == "x" ]; then continue; fi
  LINE=`cat $BUFFER | grep "$NAME" | grep ' for users :' | wc -l`
  if [ $LINE -gt 0 ]; then
      OUTPUT="$OUTPUT$ID $NAME\n"
  fi
done

SOMETHING=`echo -e "$OUTPUT" | wc -w`
if [ $SOMETHING -gt 0 ]; then
    if [ `echo -e $OUTPUT | wc -l` -eq 2 ]; then
        NAME=`echo -e $OUTPUT | sed -e 's/^[0-9@N]* //'`
        echo -e "$OUTPUT" | mail -s "FLICKR CHECK [$NAME]" "$MAIL"
    else
        echo -e "$OUTPUT" | mail -s "FLICKR CHECK" "$MAIL"
    fi
    echo -e "$OUTPUT" > $MAILCACHE/fdhmail.hourly.$DATE.$HOUR
fi
rm -f $BUFFER

