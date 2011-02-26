#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.backup import FavoritesBackup
from flickr_download_helper.web_api import PhotoManager

import cgi

config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

form = cgi.FieldStorage()

photo_id = None
action = None

if 'photo_id' in form: photo_id = form['photo_id'].value
if 'action' in form: action = form['action'].value

###########################################
manager = PhotoManager(FavoritesBackup())

if action == 'mark' and photo_id != None:
    Logger().debug("marking %s"%photo_id)
    manager.markPhoto(photo_id)

if action == 'delete' and photo_id != None:
    Logger().debug("deleting %s"%photo_id)
    manager.removePhoto(photo_id)

if action == 'export':
    Logger().debug("exporting the list of photos")
    photos_id = map(lambda p:p['id'], manager.getPhotos())
    print "Content-type: text/txt\n\n"
    print "\n".join(photos_id)

