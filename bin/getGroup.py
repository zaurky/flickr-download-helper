#!/usr/bin/python

from flickr_download_helper.api import API
from flickr_download_helper.config import OPT


if OPT.group_id:
    API(False).groupFromScratch(OPT.group_id)
