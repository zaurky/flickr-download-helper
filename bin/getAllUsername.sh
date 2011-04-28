#!/bin/sh

. /etc/fdh/fdh.sh

USERNAME=$1

IDS=`grep "$USERNAME" $FILESDIR/contacts_rev_change_name | awk '{print $2}' | sort -u`

for ID in $IDS; do
  echo "###############"
  echo $ID
  echo "###############"

  NAMES=`grep "$ID" $FILESDIR/contacts_rev_change_name | sed -e "s/[><]\s$ID\s//" | sort -u | sed -e 's/ /œœ/g'`
  for NAME in $NAMES; do
    NAME=`echo "$NAME" | sed -e 's/œœ/ /g'`
    COUNT=`find "$FLICKRPHOTODIR/$NAME" -type f | wc -l`
    echo -e "$NAME\t\t$COUNT"
  done
done

