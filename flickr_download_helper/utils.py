from flickr_download_helper.config import OPT
from flickr_download_helper.logger import Logger
import urllib2
import sys
import re
import os


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
        return None

    try:
        return urllib2.urlopen(url).read()
    except urllib2.URLError, e:
        return downloadProtect(url, nb_tries-1)
    except Exception, e:
        Logger().error("while downloading the file from %s (e: %s)" % (url, str(e)))
