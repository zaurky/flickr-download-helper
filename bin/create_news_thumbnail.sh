#!/bin/zsh

NEWS_DIR="/home/olivier/.flickr_download_helper/news/daily"
THUMBDIR="/media/MEDIA/olivier/thumb"
TMPDIR='/tmp'

find $NEWS_DIR -type d > $TMPDIR/fdh.thumbgen.dirs
rm -f "$TMPDIR/fdh.thumbgen.files"
for i in `echo $NEWS_DIR/**/*(oc@)`; do
    echo "$i" >> $TMPDIR/fdh.thumbgen.files
done
#echo $NEWS_DIR/**/*(oc.)  > $TMPDIR/fdh.thumbgen.files
# find $NEWS_DIR -type l > $TMPDIR/fdh.thumbgen.files

cat $TMPDIR/fdh.thumbgen.dirs | sed -e "s|$NEWS_DIR|$THUMBDIR\/square|" > $TMPDIR/fdh.thumbgen.dirstocreate
for i in `cat $TMPDIR/fdh.thumbgen.dirstocreate`; do mkdir -p "$i"; done
rm -f $TMPDIR/fdh.thumbgen.dirstocreate

cat $TMPDIR/fdh.thumbgen.dirs | sed -e "s|$NEWS_DIR|$THUMBDIR\/mobile|" > $TMPDIR/fdh.thumbgen.dirstocreate
for i in `cat $TMPDIR/fdh.thumbgen.dirstocreate`; do mkdir -p "$i"; done
rm -f $TMPDIR/fdh.thumbgen.dirstocreate

rm -f "$THUMBDIR/*.files"

for i in `cat $TMPDIR/fdh.thumbgen.files | sed -e 's| |##|g'`; do
    THUMBFILE=`echo "$i" |  sed -e "s|$NEWS_DIR|$THUMBDIR\/square|" | sed -e 's|##| |g'`
    MOBILEFILE=`echo "$i" |  sed -e "s|$NEWS_DIR|$THUMBDIR\/mobile|" | sed -e 's|##| |g'`

    DATE=`dirname "$FILE"`
    DATE=`basename "$DATE"`
    FILE=`echo "$i" | sed -e 's|##| |g'`
    if [ ! -e "$THUMBFILE" ]; then
        convert -thumbnail "80x80" "$FILE" "$THUMBFILE"
    fi
    if [ ! -e "$MOBILEFILE" ]; then
        convert -resize "800x800" "$FILE" "$MOBILEFILE"
    fi
    echo `basename "$FILE"` >> "$THUMBDIR/$DATE.files"
done
