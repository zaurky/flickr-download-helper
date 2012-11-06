#!/usr/bin/python

from flickr_download_helper.config import OPT, INS
from flickr_download_helper.logger import Logger

import flickr_download_helper
from flickr_download_helper.api import groupFromScratch, getUserGroups

import os
import shutil

api, token = flickr_download_helper.main_init(False)

INS['put_group_in_session'] = True
groups = getUserGroups(api, token, OPT.my_id, page = 1)
i = 0
for group in groups:
    group_id = group['nsid']
    if group_id in OPT.skiped_group:
        continue

    Logger().warn("scan_group %d/%d"%(i, len(groups)))
    groupFromScratch(api, token, group_id)
    filepath = "%s_0" % os.path.join(OPT.groups_full_content_dir, group_id)
    shutil.move(filepath, os.path.join(OPT.groups_full_content_dir, group_id))
