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
from flickr_download_helper.api import getContactList, getStaticContactList, getUserGroups
from flickr_download_helper.logger import Logger
from flickr_download_helper.config import OPT, INS

def getContactPhotos(api, token):
    Logger().debug("Contact : %s"%OPT.user_id)
    try:
        ret, count = flickr_download_helper.main(api, token)
        if ret != 0:
            if ret == 4:
                # failed to find user, maybe next time!
                pass
            else:
                Logger().error("getting %s failed (1: %s)"%(OPT.user_id, ret))
        if OPT.smart and count == 0:
            if INS['failure_level'] == 0:
                Logger().info("stopping there, the most recent user to upload didn't upload anything (%s)"%OPT.user_id)
                return False
            INS['failure_level'] -= 1
    except Exception, e:
        Logger().print_tb(e)
        if hasattr(e, 'strerror') and e.strerror is not None and e.strerror != '':
            Logger().error("getting %s failed (2: %s)"%(OPT.user_id, e.strerror))
        elif hasattr(e, 'message') and e.message is not None and e.message != '':
            Logger().error("getting %s failed (3: %s)"%(OPT.user_id, e.message))
        else:
            Logger().error("getting %s failed %s"%(OPT.user_id, str(e)))
    return True

def getContactsPhotos(api, token):
    # get the list of favorites
    setattr(OPT, 'has_been_download', {})
    contacts = []
    no_static_contacts = False
    if OPT.smart:
        contacts = map(lambda nsid: {'nsid':nsid}, flickr_download_helper.getRecentlyUploadedContacts(api, token))
    elif len(OPT.contact_ids) > 0:
        contacts = map(lambda nsid: {'nsid':nsid}, OPT.contact_ids)
        no_static_contacts = True
    else:
        contacts = getContactList(api, token)
        # TODO should keep new added contacts
        if OPT.check_old_contacts:
            import pickle
            f = open(OPT.contact_to_remove, 'rb')
            to_remove = pickle.load(f)
            f.close()

            contacts = map(lambda c: c['nsid'], contacts)
            contacts = list(set(contacts) - set(to_remove))
            contacts = map(lambda c: {'nsid': c}, contacts)

    print len(contacts)
    INS['failure_level'] = 10

    static_ids = []
    contacts_ids = []
    if not no_static_contacts:
        contacts_ids = getStaticContactList()
        static_ids = list(contacts_ids)
        Logger().info("static contacts %s"%(str(contacts_ids)))
    for c in contacts:
        if OPT.only_collect is not None:
            if c['nsid'] in OPT.only_collect:
                contacts_ids.append(c['nsid'])
            else:
                continue
        if c['nsid'] != '52256782@N02': # TODO put the rejected in the conf file
            contacts_ids.append(c['nsid'])

    if OPT.scan_groups:
        INS['put_group_in_session'] = True
        groups = getUserGroups(api, token, OPT.my_id, page = 1)
        i = 0
        for group in groups:
            if group['nsid'] in OPT.skiped_group:
                continue
            Logger().warn("scan_group %d/%d"%(i, len(groups)))
            INS['groups'] = {}
            INS['temp_groups'] = {}
            OPT.group_id = group['nsid']
            for contacts_id in contacts_ids:
                OPT.user_id = contacts_id
                ret = getContactPhotos(api, token)
                if not ret: break
            del INS['groups']
            del INS['temp_groups']
            i += 1
    else:
        for contacts_id in contacts_ids:
            OPT.user_id = contacts_id
            ret = getContactPhotos(api, token)
            if not ret and contacts_id not in static_ids: break

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
        sys.exit(0)

if __name__ == "__main__":
    try:
        r = flickr_download_helper.main_init()
        if not isinstance(r, (list, tuple)):
            if r == 6:
                sys.exit(-4)
            sys.exit(-5)
        api, token = r
        Logger().debug("#######################################")
    except Exception, e:
        info = sys.exc_info()
        if OPT.debug:
            try:
                Logger().error(info[1])
                Logger().print_tb(info[2])
            except:
                try:
                    print info
                    print info[1]
                    traceback.print_tb(info[2])
                except:
                    sys.exit(-2)
        else:
            try:
                Logger().error(info[1])
            except:
                try:
                    print info[1]
                    traceback.print_tb(info[2])
                except:
                    sys.exit(-3)
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
