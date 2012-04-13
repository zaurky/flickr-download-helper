#!/usr/bin/python

from flickr_download_helper import main_init
from flickr_download_helper.api import groupFromScratch
from flickr_download_helper.config import OPT


api, token = main_init(False)

if OPT.group_id:
    groupFromScratch(api, token, OPT.group_id)

