#!/usr/bin/python

"""
This small program can be used to sort a flickr dir depending on flickr folders.
"""

import sys
import os
import os.path
import shutil
import traceback
import flickr_download_helper
from flickr_download_helper.logger import Logger
from flickr_download_helper.api import getUser, getUserPhotosets, getPhotoset
from flickr_download_helper.config import OPT
from flickr_download_helper.existing import Existing

if __name__ == "__main__":
    try:
        api, token = flickr_download_helper.main_init()

        user = getUser(api, token)
        user_id = user['id']

        Logger().info("\n== getting user (%s) photoset" % user_id)
        OPT.sort_by_user = True
        photosets = getUserPhotosets(api, token, user_id)

        existing = Existing(user_id, user['username'])
        photo_dir = os.path.join(OPT.photo_dir, user['username'])
        files = os.listdir(photo_dir)
        cache = dict(map(lambda p: (p.split('_')[0], os.path.join(photo_dir, p)), files))

        for photoset in photosets:
            Logger().info("\n== getting photoset %s" % photoset['title'])
            l_urls, l_photo_id2destination, destination, l_infos = getPhotoset(OPT, api, token, user['username'], photoset['id'], photoset['title'], user_id, existing)

            for id in l_photo_id2destination:
                if id in cache and os.path.exists(cache[id]):
                    shutil.move(cache[id], destination)

        Logger().info("\n== reloading existings")
        existing.forceReload()

        Logger().info("\n== saving existings")
        existing.backupToFile()

    except Exception, e:
        info = sys.exc_info()
        if OPT.debug:
            try:
                Logger().error(info[1])
                Logger().print_tb(info[2])
            except:
                print info
                print info[1]
                traceback.print_tb(info[2])
        else:
            try:
                Logger().error(info[1])
            except:
                print info[1]
                traceback.print_tb(info[2])
        sys.exit(-1)
