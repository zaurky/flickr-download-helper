#!/usr/bin/python

# from flickr_download_helper.api import getPhotoInfo
from flickr_download_helper.logger import Logger
# from flickr_download_helper.exif import fillDir, writeMetadata, contains, putGeneralInfo, fillFile
from flickr_download_helper.exif import fillDir, fillFile
import flickr_download_helper
# import pyexiv2
import os
import sys

api, token = flickr_download_helper.main_init(False)

attr = sys.argv[1]
Logger().debug("will work on %s"%attr)
if os.path.isdir(attr):
    f = fillDir(api, token)
    os.path.walk(attr, f.fillDir, [api, token])
elif os.path.isfile(attr):
    fillFile(api, token, attr)

