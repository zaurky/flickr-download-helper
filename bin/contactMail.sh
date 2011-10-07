#!/bin/bash

. /etc/fdh/fdh.sh

FDHPATH=$FLICKRDIR
LOG="$FDHPATH/log/fdh.log"
IDS=`cat $FDHPATH/files/id_to_mail`

DATE=`date --date="1 hour ago" +%Y-%m-%d`
HOUR=`date --date="1 hour ago" +%H`

BUFFER="$TMPDIR/log.buffer.$HOUR"
grep "$DATE $HOUR:" $DOWNLOADS_FILE > $BUFFER
#grep "$DATE $HOUR:" $LOG > $BUFFER

OUTPUT=''

for ID in $IDS; do
  NAME=`grep $ID $FDHPATH/files/contacts_rev_name.new | sed -e "s/^$ID\t//"`
  if [ "x$NAME" == "x" ]; then continue; fi
  LINE=`cat $BUFFER | grep "$NAME" | wc -l`
  if [ $LINE -gt 0 ]; then
    OUTPUT="$OUTPUT$ID $NAME\n"
  fi
done
OUTPUT=`echo -e "$OUTPUT" | sort -u`

SOMETHING=`echo -e "$OUTPUT" | wc -w`
if [ $SOMETHING -gt 0 ]; then
    if [ `echo -e "$OUTPUT" | wc -l` -eq 2 ]; then
        NAME=`echo -e "$OUTPUT" | sed -e 's/^[0-9@N]* //'`
        echo -e "$OUTPUT" | mail -s "FLICKR CHECK [$NAME]" "$MAIL"
    else
        echo -e "$OUTPUT" | mail -s "FLICKR CHECK" "$MAIL"
    fi
    echo -e "$OUTPUT" > $MAILCACHE/fdhmail.hourly.$DATE.$HOUR
fi
rm -f $BUFFER

