#!/bin/zsh

source /etc/fdh/fdh.sh

TAG=`date +%s`
DAY=$argv[1]

if [ "x$DAY" != "x" ]; then
    WORKING_DIR="$NEWS_DIR/$DAY"
else
    WORKING_DIR="$NEWS_DIR"
fi
find $WORKING_DIR -type d > $TMPDIR/fdh.thumbgen.dirs.$TAG

rm -f "$TMPDIR/fdh.thumbgen.files.$TAG"
for i in `echo $WORKING_DIR/**/*(oc@) | sed -e 's| |~~|g' | sed -e 's|~~/| /|g'`; do
    i=`echo "$i" | sed -e 's|~~| |g'`
    echo "$i" >> $TMPDIR/fdh.thumbgen.files.$TAG
done

cat $TMPDIR/fdh.thumbgen.dirs.$TAG | sed -e "s|$NEWS_DIR|$THUMBDIR\/square|" > $TMPDIR/fdh.thumbgen.dirstocreate.$TAG
for i in `cat $TMPDIR/fdh.thumbgen.dirstocreate.$TAG`; do mkdir -p "$i"; done
rm -f $TMPDIR/fdh.thumbgen.dirstocreate.$TAG

cat $TMPDIR/fdh.thumbgen.dirs.$TAG | sed -e "s|$NEWS_DIR|$THUMBDIR\/mobile|" > $TMPDIR/fdh.thumbgen.dirstocreate.$TAG
for i in `cat $TMPDIR/fdh.thumbgen.dirstocreate.$TAG`; do mkdir -p "$i"; done
rm -f $TMPDIR/fdh.thumbgen.dirstocreate.$TAG

if [ "x$DAY" != "x" ]; then
    rm -f "$THUMBDIR/$DAY.files.tmp"
else
    rm -f "$THUMBDIR/*.files"
fi

for i in `cat $TMPDIR/fdh.thumbgen.files.$TAG | sed -e 's| |~~|g'`; do
    THUMBFILE=`echo "$i" |  sed -e "s|$NEWS_DIR|$THUMBDIR\/square|" | sed -e 's|~~| |g'`
    MOBILEFILE=`echo "$i" |  sed -e "s|$NEWS_DIR|$THUMBDIR\/mobile|" | sed -e 's|~~| |g'`

    DATE=`dirname "$FILE"`
    DATE=`basename "$DATE"`
    FILE=`echo "$i" | sed -e 's|~~| |g'`
    if [ ! -e "$THUMBFILE" ]; then
        convert -thumbnail "80x80" "$FILE" "$THUMBFILE"
    fi
    if [ ! -e "$MOBILEFILE" ]; then
        convert -resize "400x400" "$FILE" "$MOBILEFILE"
    fi
    echo `basename "$FILE"` >> "$THUMBDIR/$DATE.files.tmp"
done
mv "$THUMBDIR/$DATE.files.tmp" "$THUMBDIR/$DATE.files"

rm -f $TMPDIR/fdh.thumbgen.dirs.$TAG $TMPDIR/fdh.thumbgen.files.$TAG
