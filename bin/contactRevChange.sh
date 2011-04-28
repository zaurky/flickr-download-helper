#!/bin/sh

. /etc/fdh/fdh.sh
FDHPATH=$FLICKRDIR

LOCKFILE=$TMPDIR/contactRevChange.sh.lock

if [ -f "$LOCKFILE" ]; then
    exit
fi

touch "$LOCKFILE"

cat $FDHPATH/files/contacts_rev.new | sort > $FDHPATH/files/contacts_rev.old
$FDHPATH/bin/getContacts.py --gcf nsid,revcontact,revfriend,revfamily --acf | sort > $FDHPATH/files/contacts_rev.new

if [ ! -s $FDHPATH/files/contacts_rev.new ]; then
    mv $FDHPATH/files/contacts_rev.old $FDHPATH/files/contacts_rev.new
    rm -f "$LOCKFILE"
    exit
fi

diff $FDHPATH/files/contacts_rev.old $FDHPATH/files/contacts_rev.new | grep ' ' > $FDHPATH/files/contacts_rev.diff
if [ `wc -l $FDHPATH/files/contacts_rev.diff | awk '{print $1}'` -ne 0 ]; then
    if [ -s $FDHPATH/files/contacts_rev.diff ]; then
        for i in `cat $FDHPATH/files/contacts_rev.diff | grep '>' | awk '{print $2}'`; do
            $FDHPATH/bin/fdh.py -d -r --nick $i --sbp
            $FDHPATH/bin/fdh.py -d -r --nick $i
            $FDHPATH/bin/fdh.py -d -r --nick $i --tfg
        done
        date >> $FDHPATH/files/contacts_rev_change
        cat $FDHPATH/files/contacts_rev.diff >> $FDHPATH/files/contacts_rev_change
    fi
fi
rm -f $FDHPATH/files/contacts_rev.diff $FDHPATH/files/contacts_rev.old

rm -f "$LOCKFILE"
