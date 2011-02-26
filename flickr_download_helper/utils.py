from flickr_download_helper.config import OPT
from flickr_download_helper.logger import Logger
import sys

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


