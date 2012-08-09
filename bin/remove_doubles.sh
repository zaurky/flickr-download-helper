#!/bin/sh

. /etc/fdh/fdh.sh

WHERE="$FLICKRPHOTODIR/$1"

echo $WHERE

echo "finding files (md5)"
find $WHERE -type f -exec md5sum '{}' ';' > $TMPDIR/doubles.md5sum

echo "sorting md5"
sort $TMPDIR/doubles.md5sum > $TMPDIR/doubles.md5sum.sort

echo "removing doubles"
python <<EOF
from os import unlink
f = open("/tmp/doubles.md5sum.sort")
h_md5 = {}
for line in f.readlines():
    line = line.strip()
    md5, file = line.split('  ', 1)
    if md5 in h_md5:
        unlink(h_md5[md5])
    h_md5[md5] = file
f.close()
EOF

rm -f $TMPDIR/doubles.md5sum $TMPDIR/doubles.md5sum.sort
