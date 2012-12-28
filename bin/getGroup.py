#!/usr/bin/python

from flickr_download_helper.api import API
from flickr_download_helper.config import OPT


api = API(False)

if OPT.group_id:
    api.groupFromScratch(OPT.group_id)
