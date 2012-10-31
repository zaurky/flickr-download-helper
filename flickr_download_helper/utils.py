from flickr_download_helper.config import OPT
from flickr_download_helper.logger import Logger
import sys
import re
import os


#################### UTILITIES
def waitFor(message, *attr):
    if not OPT.interactive:
        return False

    try:
        Logger().info(message % attr)
    except TypeError, e:
        info = sys.exc_info()
        Logger().error("this is a development bug, please report this traceback")
        Logger().print_tb(info[2])
        return False

    Logger().prompt("do you want to try again [y/n]")
    line = sys.stdin.readline()
    line = line.rstrip()
    if line.lower() == 'y' or line.lower() == 'yes':
        return True
    return False


def extends(orig, ext):
    if type(orig) != dict or type(ext) != dict:
        raise Exception('extends only work with 2 dict!')
    for k in ext:
        if k in orig and orig[k] != ext[k]:
            Logger().warn("key %s is in the two dict but don't have the same value" % k)
        else:
            orig[k] = ext[k]
    return orig


def get_video(file):
    if not os.path.exists(file):
        return False
    file = open(file, 'rb')
    for line in file.readlines():
        m = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Get the video (http://www.flickr.com/photos/[^\/]+/\d+/)', line)
        if m is not None:
            print m.group(2)
    file.close()
    return True


def readFile(filename):
    if os.path.exists(filename):
        f = open(filename, "rb")
        ret = f.read()
        f.close()
        return ret
    else:
        Logger().error("file not found %s" % filename)
    return None
