#!/usr/bin/python

from flickr_download_helper.api import initialisationFlickrApi
from flickr_download_helper import getRecentlyUploadedContacts
from flickr_download_helper.config import OptConfigReader, OPT, OptReader
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
import os

config = OptConfigReader()
config.setup()

opt = OptReader()
ret = opt.read('getContacts.py')


## start the logger
Logger().setup()
Logger().warn("#############################################################")
Logger().warn("Getting contacts (running as %s)"%(os.getpid()))

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

# init of the flickr api
api, token = initialisationFlickrApi(OPT)

owners = getRecentlyUploadedContacts(api, token)

print "\n".join(owners)

