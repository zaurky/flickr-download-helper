#!/usr/bin/python

from flickr_download_helper.api import API
import flickr_download_helper


api = API(False)

photo_id = '5084025880'

def display(w):
    print "%s:%s => %s" % (w['tagspace'], w['label'], w['raw'])


exif = api.getPhotoExif(api, token, photo_id)
print exif



