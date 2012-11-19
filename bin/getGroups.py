#!/usr/bin/python

from flickr_download_helper.config import OPT, INS
from flickr_download_helper.logger import Logger

from flickr_download_helper.api import API

import os
import shutil

api = API(False)

INS['put_group_in_session'] = True
groups = api.getUserGroups(OPT.my_id, page = 1)
i = 0
for group in groups:
    group_id = group['nsid']
    if group_id in OPT.skiped_group:
        continue

    Logger().warn("scan_group %d/%d"%(i, len(groups)))
    api.groupFromScratch(group_id)
    filepath = "%s_0" % os.path.join(OPT.groups_full_content_dir, group_id)
    shutil.move(filepath, os.path.join(OPT.groups_full_content_dir, group_id))
