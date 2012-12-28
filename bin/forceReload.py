#!/usr/bin/python

from flickr_download_helper import Existing
from flickr_download_helper.api import API


api = API()

contacts = api.getContactList()

for c in contacts:
    e = Existing(c['nsid'], c['username'])
    e.forceReload()
    e.backupToFile()
