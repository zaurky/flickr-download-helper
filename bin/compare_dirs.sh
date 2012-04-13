#!/bin/sh

. /etc/fdh/fdh.sh

USERNAME=$1

#echo "please use : getAllUsername.sh $USERNAME"
#sleep 5

IDS=`grep "$USERNAME" $FILESDIR/contacts_rev_change_name | awk '{print $2}' | sort -u`
NAMES=`grep "$IDS" $FILESDIR/contacts_rev_change_name | sed -e "s/[><]\s$IDS\s//" | sort -u `
DIR="$FLICKRPHOTODIR$NAMES"
DIRNEW=`echo "$FLICKRPHOTODIR" | sed -e 's/\/$/.new\//'`
DIRNEW="$DIRNEW$NAMES"

find "$DIR" -type f -exec md5sum '{}' ';' > "$TMPDIR/md5sum1.$IDS"
find "$DIRNEW" -type f -exec md5sum '{}' ';' > "$TMPDIR/md5sum2.$IDS"


echo "
h1 = {}
for line in open('$TMPDIR/md5sum2.$IDS'):
    a = line.split(' ')
    k = a.pop(0)
    h1[k] = ' '.join(a).strip()

h2 = {}
for line in open('$TMPDIR/md5sum2.$IDS'):
    a = line.split(' ')
    k = a.pop(0)
    h2[k] = ' '.join(a).strip()

for k,v in h2.items():
    if k in h1:
        del h1[k]
print h1
	
" | python








