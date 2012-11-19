#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.api import API

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
api = API()

contacts = api.getContactList()
print contacts
