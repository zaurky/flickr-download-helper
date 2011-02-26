#!/usr/bin/python

"""
flickr_download_helper.py

This small program was developed to help retrieve full bunch of photos from flickr.

To have the description of the parameters, please read flickr_download_helper.config or start the program with the --help flag
"""

import sys
import time
import traceback
from twisted.internet import reactor
import flickr_download_helper
from flickr_download_helper.api import getContactList, getStaticContactList
from flickr_download_helper.logger import Logger
from flickr_download_helper.config import OPT

def getContactsPhotos(api, token):
    # get the list of favorites
    setattr(OPT, 'has_been_download', {})
    contacts = []
    if OPT.smart:
        contacts = map(lambda nsid: {'nsid':nsid}, flickr_download_helper.getRecentlyUploadedContacts(api, token))
    else:
        contacts = getContactList(api, token)
    failure_level = 10

    contacts_ids = getStaticContactList()
    Logger().info("static contacts %s"%(str(contacts_ids)))
    for c in contacts:
        contacts_ids.append(c['nsid'])

    for contacts_id in contacts_ids:
        Logger().debug("Contact : %s"%contacts_id)

        # modify OPT
        OPT.user_id = contacts_id
        try:
            ret, count = flickr_download_helper.main(api, token)
            if ret != 0:
                Logger().error("getting %s failed (1: %s)"%(OPT.user_id, ret))
            if OPT.smart and count == 0:
                if failure_level == 0:
                    # and OPT.user_id not in OPT.not_smart:
                    Logger().info("stopping there, the most recent user to upload didn't upload anything (%s)"%OPT.user_id)
                    break
                failure_level -= 1
        except Exception, e:
            Logger().print_tb(e)
            if hasattr(e, 'strerror'):
                Logger().error("getting %s failed (2: %s)"%(OPT.user_id, e.strerror))
            elif hasattr(e, 'message'):
                Logger().error("getting %s failed (3: %s)"%(OPT.user_id, e.message))
            else:
                Logger().error("getting %s failed"%(OPT.user_id))

    users = ', '.join(OPT.has_been_download.keys())

    totals = [0,0]
    for t in OPT.has_been_download.values():
        totals[0] += t[0]
        totals[1] += t[1]
    if totals[0] != 0:
        Logger().warn("got %i files (%i) for users : %s"%(totals[0], totals[1], users))
    else:
        Logger().warn("didn't download anything")

    Logger().debug("#######################################")
    if OPT.loop != None:
        OPT.since = int(time.time())
        reactor.callLater(OPT.loop, getContactsPhotos, api, token)
    else:
        reactor.stop()

if __name__ == "__main__":
    try:
        api, token = flickr_download_helper.main_init()
        Logger().debug("#######################################")
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

    OPT.url = None
    OPT.nick = None
    OPT.photoset_id = None
    OPT.collection_id = None
    OPT.photo_id_in_file = None
    OPT.tags = None
    OPT.username = None
    OPT.daily_in_dir = True

    reactor.callLater(1, getContactsPhotos, api, token)
    reactor.run()


