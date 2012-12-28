#!/usr/bin/python
"""
Generate the cache of old contacts to be able to only look at active contacts.

"""


import pickle
from datetime import datetime, timedelta
from flickr_download_helper.config import OPT
from flickr_download_helper.api import API

api = API(False)
contacts = api.getContactList()
now = datetime.now()

to_remove = {}
deltas = {}


for delta in (30, 60, 90, 180):
    deltas[delta] = (now - timedelta(days=delta)).strftime('%s')


def has_photos(nsid, delta):
    """check that this contact has some photos since delta"""
    return len(api.getUserPhotos(nsid, delta, limit=2)) != 0


for contact in [contact['nsid'] for contact in contacts]:
    for delta in (180, 90, 60, 30):
        if not has_photos(contact, deltas[delta]):
            print "%s should remove : %s" % (delta, contact)
            to_remove.setdefault(delta, []).append(contact)
            break

remove = []
for delta in (180, 90, 60, 30):
    filename = getattr(OPT, 'contact_to_remove_%s' % delta)
    f = open(filename, 'wb')
    remove.extend(to_remove[delta])
    pickle.dump(remove, f)
    f.close()
