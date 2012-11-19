#!/usr/bin/python

from flickr_download_helper import Existing
from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.logger import Logger
from flickr_download_helper.api import API

config = OptConfigReader()
config.setup()

Logger().setup()
Logger().warn("#############################################################")
Logger().warn("Reloading user photo cache")

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

api = API()

contacts = api.getContactList()

for c in contacts:
    e = Existing(c['nsid'], c['username'])
    e.forceReload()
    e.backupToFile()
