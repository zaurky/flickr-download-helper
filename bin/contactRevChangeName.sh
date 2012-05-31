#!/bin/bash

. /etc/fdh/fdh.sh

cat $FLICKRDIR/files/contacts_rev_name.new | grep -v 'logging as' | sort > $FLICKRDIR/files/contacts_rev_name.old
$FLICKRBINDIR/getContacts.py --gcf nsid,username | grep -v 'logging as' | sort > $FLICKRDIR/files/contacts_rev_name.new

diff $FLICKRDIR/files/contacts_rev_name.old $FLICKRDIR/files/contacts_rev_name.new | grep ' ' > $FLICKRDIR/files/contacts_rev_name.diff
if [ `wc -l $FLICKRDIR/files/contacts_rev_name.diff | awk '{print $1}'` -ne 0 ]; then
    if [ -s $FLICKRDIR/files/contacts_rev_name.diff ]; then
        date >> $FLICKRDIR/files/contacts_rev_change_name
        cat $FLICKRDIR/files/contacts_rev_name.diff >> $FLICKRDIR/files/contacts_rev_change_name
    fi
fi
rm -f $FLICKRDIR/files/contacts_rev_name.diff $FLICKRDIR/files/contacts_rev_name.old

