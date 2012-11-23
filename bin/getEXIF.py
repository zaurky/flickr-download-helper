#!/usr/bin/python

from flickr_download_helper.exif import getGeneralInfo
import sys
import os

attr = sys.argv[1]
if not os.path.exists(attr):
    print "file %s don't exists" % (attr)

if not os.path.isfile(attr):
    print "%s is not a file" % (attr)

ret = getGeneralInfo(attr)

print "User Comment "
print ret['Exif.Photo.UserComment']
