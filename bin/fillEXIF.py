#!/usr/bin/python

from flickr_download_helper.logger import Logger
from flickr_download_helper.exif import fillDir, fillFile
import os
import sys


attr = sys.argv[1]
Logger().debug("will work on %s"%attr)


if os.path.isdir(attr):
    f = fillDir()
    os.path.walk(attr, f.fillDir, [])
elif os.path.isfile(attr):
    fillFile(attr)
