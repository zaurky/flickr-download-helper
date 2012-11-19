#!/usr/bin/python

import os

from flickr_download_helper.config import OPT
from flickr_download_helper.api import API

api = API(False)

groups = api.getUserGroups(OPT.my_id, page = 1)

to_remove = []
for group in groups:
    total = api.countGroupPhotos(group['nsid'])
    gpath = os.path.join(OPT.groups_full_content_dir, group['nsid'])
    if not os.path.exists(gpath) and total > 20000:
        to_remove.append(group['nsid'])

print ':'.join(to_remove)

