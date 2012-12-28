#!/usr/bin/python

from flickr_download_helper.api import API
from flickr_download_helper import getRecentlyUploadedContacts


# initi flickr api
api = API(False)

print "\n".join(getRecentlyUploadedContacts())
