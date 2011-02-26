#!/usr/bin/python

from flickr_download_helper.api import getPhotoExif
import flickr_download_helper


api, token = flickr_download_helper.main_init(False)
print api
print token

photo_id = '5084025880'

def display(w):
    print "%s:%s => %s" % (w['tagspace'], w['label'], w['raw'])


exif = getPhotoExif(api, token, photo_id)
print exif



