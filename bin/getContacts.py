#!/usr/bin/python

from flickr_download_helper.api import getContactList, initialisationFlickrApi, getUserFromID
from flickr_download_helper.config import OptConfigReader, OPT, OptReader
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
import os

config = OptConfigReader()
config.setup()

opt = OptReader()
ret = opt.read('getContacts.py')


## start the logger
Logger().setup()
Logger().warn("#############################################################")
Logger().warn("Getting contacts (running as %s)"%(os.getpid()))

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

# init of the flickr api
api, token = initialisationFlickrApi(OPT)


def encode(string):
    if not isinstance(string, (str, unicode)): return str(string)
    try: return string.encode('latin1')
    except: return string.encode('utf8')

contacts = getContactList(api, token)

if OPT.check_old_contacts:
    import pickle
    f = open(OPT.contact_to_remove, 'rb')
    to_remove = pickle.load(f)
    f.close()

    contacts = map(lambda c: c['nsid'], contacts)
    contacts = list(set(contacts) - set(to_remove))
    contacts = map(lambda c: {'nsid': c}, contacts)

for c in contacts:
    line = []
    user = None
    if OPT.advContactFields:
        try:
            user = getUserFromID(api, c['nsid'], token)
        except:
            # second try
            user = getUserFromID(api, c['nsid'], token)
    for field in OPT.getContactFields:
        if field in c: line.append(c[field].strip())
        elif user and field in user:
            if hasattr(user[field], 'strip'):
                line.append(user[field].strip())
            else:
                line.append(user[field])


    if len(line) == 0:
        print c['nsid']
    else:
        try:
            print "\t".join(map(encode, line))
        except:
            print line

