from flickr_download_helper.config import OPT
from flickr_download_helper.logger import Logger
import urllib2
import sys
import re
import os

SIZES = ['Thumbnail', 'Square', 'Medium', 'Large', 'Original']
INV_SIZES = list(SIZES)
INV_SIZES.reverse()


#################### UTILITIES
def waitFor(message, *attr):
    if not OPT.interactive:
        return False

    try:
        Logger().info(message % attr)
    except TypeError:
        info = sys.exc_info()
        Logger().error(
            "this is a development bug, please report this traceback")
        Logger().print_tb(info[2])
        return False

    Logger().prompt("do you want to try again [y/n]")
    return sys.stdin.readline().rstrip().lower() in ('y', 'yes')


def extends(orig, ext):
    if not (isinstance(orig, dict) and isinstance(ext, dict)):
        raise Exception('extends only work with 2 dict!')

    for k in ext:
        if k in orig and orig[k] != ext[k]:
            Logger().warn(
                "key %s is in the two dict but don't have the same value" % k)
        else:
            orig[k] = ext[k]
    return orig


def get_video(filename):
    if not os.path.exists(filename):
        return False

    f = open(filename, 'rb')
    for line in f.readlines():
        m = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?" \
            "Get the video (http://www.flickr.com/photos/[^\/]+/\d+/)', line)
        if m:
            print m.group(2)

    f.close()
    return True


def _getPicUrl(photo, size):
    return "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" % (
        photo['farm'], photo['server'], photo['id'], photo['secret'], size)


def getThumbURL(photo):
    return _getPicUrl(photo, 's')


def getPhotoURL(photo):
    return _getPicUrl(photo, 'b')


def getUserURL(nick):
    return "http://www.flickr.com/photos/%s" % (nick)


def getVideoURL(photo):
    return "http://www.flickr.com/photos/%s/%s/play/orig/%s/" % (
        photo['owner'], photo['id'], photo['secret'])


def _selectPhotoSizeURL(sizes, order):
    for s in order:
        for size in sizes:
            if size['label'] == s:
                return size['source']


def selectSmallerPhotoSizeURL(sizes):
    return _selectPhotoSizeURL(sizes, SIZES)


def selectBiggerPhotoSizeURL(sizes):
    return _selectPhotoSizeURL(sizes, INV_SIZES)


def selectMediaURL(sizes, media_type):
    for size in sizes:
        if size['media'] == media_type:
            return size['url']


def readFile(filename):
    if os.path.exists(filename):
        f = open(filename, "rb")
        ret = f.read()
        f.close()
        return ret
    else:
        Logger().error("file not found %s" % filename)


def mkdir(destination):
    try:
        if OPT.retrieve and not os.path.exists(destination):
            os.mkdir(destination)
    except:
        Logger().warn(destination)
        raise


def downloadProtect(url, nb_tries=5):
    if nb_tries <= 0:
        return

    try:
        return urllib2.urlopen(url).read()
    except urllib2.URLError, e:
        return downloadProtect(url, nb_tries-1)
    except Exception, e:
        Logger().error("while downloading the file from %s (e: %s)" % (url, str(e)))
