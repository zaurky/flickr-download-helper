#!/bin/bash

. /etc/fdh/fdh.sh
FDHPATH=$FLICKRDIR

LOCKFILE=$TMPDIR/contactRevChange.sh.lock

if [ -f "$LOCKFILE" ]; then
    exit
fi

if [ "x$DISABLE" == "x" ]; then
    touch "$LOCKFILE"

    create_new()
    {
        $FDHPATH/bin/getContacts.py --gcf nsid,revcontact,revfriend,revfamily --acf | sort > $FDHPATH/files/contacts_rev.new 2> $FDHPATH/log/contactRevChange.stderr
    }

    cat $FDHPATH/files/contacts_rev.new | sort > $FDHPATH/files/contacts_rev.old
    create_new

    if [ ! -s $FDHPATH/files/contacts_rev.new ]; then
        mv $FDHPATH/files/contacts_rev.old $FDHPATH/files/contacts_rev.new
        rm -f "$LOCKFILE"
        exit
    fi

    if [ ! -s $FDHPATH/files/contacts_rev.old ]; then
        rm -f "$LOCKFILE"
        exit
    fi

    diff $FDHPATH/files/contacts_rev.old $FDHPATH/files/contacts_rev.new \
        | egrep -v '(logging as|process options)' | grep ' ' > $FDHPATH/files/contacts_rev.diff
    LENGTH=`wc -l $FDHPATH/files/contacts_rev.diff | awk '{print $1}'`
    while [ $LENGTH -gt 30 ]; do
        create_new
        diff $FDHPATH/files/contacts_rev.old $FDHPATH/files/contacts_rev.new | grep ' ' > $FDHPATH/files/contacts_rev.diff
        LENGTH=`wc -l $FDHPATH/files/contacts_rev.diff | awk '{print $1}'`
    done

    if [ $LENGTH -ne 0 ]; then
        if [ -s $FDHPATH/files/contacts_rev.diff ]; then
            for i in `cat $FDHPATH/files/contacts_rev.diff | grep '>' | awk '{print $2}'`; do
                echo "doing $i"
                $FDHPATH/bin/fdh.py -d -r --nick $i --sort_by_photoset
                $FDHPATH/bin/fdh.py -d -r --nick $i
                $FDHPATH/bin/fdh.py -d -r --nick $i --try_from_groups
    #	    $FDHPATH/bin/fdh.py -d -r --nick $i --scan_groups --group_from_cache
            done
            date >> $FDHPATH/files/contacts_rev_change
            cat $FDHPATH/files/contacts_rev.diff >> $FDHPATH/files/contacts_rev_change
        fi
    fi
    rm -f $FDHPATH/files/contacts_rev.diff $FDHPATH/files/contacts_rev.old

    rm -f "$LOCKFILE"
fi
