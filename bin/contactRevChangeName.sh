#!/bin/bash

. /etc/fdh/fdh.sh
FDHPATH=$FLICKRDIR

cat $FDHPATH/files/contacts_rev_name.new | sort > $FDHPATH/files/contacts_rev_name.old
$FDHPATH/bin/getContacts.py --gcf nsid,username | sort > $FDHPATH/files/contacts_rev_name.new

diff $FDHPATH/files/contacts_rev_name.old $FDHPATH/files/contacts_rev_name.new | grep ' ' > $FDHPATH/files/contacts_rev_name.diff
if [ `wc -l $FDHPATH/files/contacts_rev_name.diff | awk '{print $1}'` -ne 0 ]; then
    if [ -s $FDHPATH/files/contacts_rev_name.diff ]; then
        date >> $FDHPATH/files/contacts_rev_change_name
        cat $FDHPATH/files/contacts_rev_name.diff >> $FDHPATH/files/contacts_rev_change_name
    fi
fi
rm -f $FDHPATH/files/contacts_rev_name.diff $FDHPATH/files/contacts_rev_name.old

