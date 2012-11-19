#!/usr/bin/python

import pickle
from datetime import datetime, timedelta
from flickr_download_helper.config import OPT
from flickr_download_helper.api import API

api = API(False)
contacts = api.getContactList()

to_remove_30 = []
to_remove_60 = []
to_remove_90 = []
to_remove_180 = []

def has_photos(nsid, delta):
    return len(api.getUserPhotos(nsid,
        (datetime.now() - timedelta(days=delta)).strftime('%s'), limit=2)) != 0


for c in contacts:
    if has_photos(c['nsid'], 180):
        if has_photos(c['nsid'], 90):
            if has_photos(c['nsid'], 60):
                if has_photos(c['nsid'], 30):
                    print "keep : %s" % (c['nsid'])
                else:
                   print "30 should remove : %s" % (c['nsid'])
                   to_remove_30.append(c['nsid'])
            else:
                print "60 should remove : %s" % (c['nsid'])
                to_remove_60.append(c['nsid'])
        else:
            print "90 should remove : %s" % (c['nsid'])
            to_remove_90.append(c['nsid'])
    else:
        print "should remove : %s" % (c['nsid'])
        to_remove_180.append(c['nsid'])


f = open(OPT.contact_to_remove_180, 'wb')
pickle.dump(to_remove_180, f)
f.close()

to_remove_180.extend(to_remove_90)
f = open(OPT.contact_to_remove_90, 'wb')
pickle.dump(to_remove_180, f)
f.close()

to_remove_180.extend(to_remove_60)
f = open(OPT.contact_to_remove_60, 'wb')
pickle.dump(to_remove_180, f)
f.close()

to_remove_180.extend(to_remove_30)
f = open(OPT.contact_to_remove_30, 'wb')
pickle.dump(to_remove_180, f)
f.close()
