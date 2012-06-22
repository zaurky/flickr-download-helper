#!/usr/bin/python

from flickr_download_helper.config import OPT, INS
from flickr_download_helper.logger import Logger

import flickr_download_helper
from flickr_download_helper.api import groupFromScratch, getUserGroups

api, token = flickr_download_helper.main_init(False)

INS['put_group_in_session'] = True
groups = getUserGroups(api, token, OPT.my_id, page = 1)
i = 0
for group in groups:
    if group['nsid'] in OPT.skiped_group:
        continue
    Logger().warn("scan_group %d/%d"%(i, len(groups)))
    groupFromScratch(api, token, group['nsid'])
