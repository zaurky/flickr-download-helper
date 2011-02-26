#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
import flickr_download_helper

config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()
Logger().warn("#############################################################")
Logger().warn("Getting contacts")

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

# init of the flickr api
api, token = flickr_download_helper.initialisationFlickrApi(OPT)

contacts = flickr_download_helper.getContactList(api, token)
print contacts

