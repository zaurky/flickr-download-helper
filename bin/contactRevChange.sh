#!/bin/sh

. /etc/fdh/fdh.sh
FDHPATH=$FLICKRDIR

mv -f $FDHPATH/files/contacts_rev.new $FDHPATH/files/contacts_rev.old
$FDHPATH/bin/getContacts.py --gcf nsid,revcontact,revfriend,revfamily --acf > $FDHPATH/files/contacts_rev.new

diff $FDHPATH/files/contacts_rev.old $FDHPATH/files/contacts_rev.new | grep ' ' > $FDHPATH/files/contacts_rev.diff
if [ `wc -l $FDHPATH/files/contacts_rev.diff | awk '{print $1}'` -ne 0 ]; then
    if [ -s $FDHPATH/files/contacts_rev.diff ]; then
        for i in `cat $FDHPATH/files/contacts_rev.diff | grep '>' | awk '{print $2}'`; do
            $FDHPATH/bin/fdh.py -d -r --nick $i
        done
        date >> $FDHPATH/files/contacts_rev_change
        cat $FDHPATH/files/contacts_rev.diff >> $FDHPATH/files/contacts_rev_change
    fi
fi
rm -f $FDHPATH/files/contacts_rev.diff $FDHPATH/files/contacts_rev.old

