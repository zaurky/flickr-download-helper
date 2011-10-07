#!/bin/bash

. /etc/fdh/fdh.sh
FDHPATH=$FLICKRDIR

mv -f $FDHPATH/files/contacts.new $FDHPATH/files/contacts.old
$FDHPATH/bin/getContacts.py > $FDHPATH/files/contacts.new
diff $FDHPATH/files/contacts.old $FDHPATH/files/contacts.new | grep ' ' > $FDHPATH/files/contacts.diff
if [ `wc -l $FDHPATH/files/contacts.diff | awk '{print $1}'` -ne 0 ]; then
    if [ -s $FDHPATH/files/contacts.diff ]; then
        date >> $FDHPATH/files/contacts_change
        cat $FDHPATH/files/contacts.diff >> $FDHPATH/files/contacts_change
    fi
fi
rm -f $FDHPATH/files/contacts.diff $FDHPATH/files/contacts.old

