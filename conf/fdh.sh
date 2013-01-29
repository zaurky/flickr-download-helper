FLICKRDIR="/root/fdh"
FLICKRBINDIR="$FLICKRDIR/bin/"
FLICKRPHOTODIR="/mnt/flickr/photo/"

NEWS_DIR="/mnt/flickr/news/daily"
THUMBDIR="/mnt/flickr/thumb"
CACHEDIR="/usr/share/fdh"
MOUNTEDON='/mnt'
FILESDIR="$FLICKRDIR/files"
FILESDIR="$FLICKRDIR/files"
LOGFILE="$FLICKRDIR/log/fdh.log"

DAILYTFG="$FILESDIR/daily.tfg"

DOWNLOADS_FILE="$FILESDIR/downloads"
ONLYCOLLECT="$FILESDIR/only_collect"
ONLYCOLLECTEMERGENCY="$ONLYCOLLECT.emergency"
EMERGENCYFLAG="$FILESDIR/emergency.flag"
MINSIZE=250000

TMPDIR='/tmp'

MAIL=""
MAILCACHE="$CACHEDIR/mails"
DAILYNEWSURL="http://"

RSYNCCOMMAND='rsync'
RSYNCOPTIONS=" -avz"
RSYNCSSH='ssh -i ~/.ssh/id_dsa'
RSYNCSOURCE="user@machine:/path/"
RSYNCDEST="$FLICKRPHOTODIR"

# DISABLE='yes'
