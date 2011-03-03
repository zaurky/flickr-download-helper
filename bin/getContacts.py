#!/usr/bin/python

from flickr_download_helper.api import getContactList, initialisationFlickrApi, getUserFromID
from flickr_download_helper.config import OptConfigReader, OPT, OptReader
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings

config = OptConfigReader()
config.setup()

opt = OptReader()
ret = opt.read('getContacts.py')


## start the logger
Logger().setup()
Logger().warn("#############################################################")
Logger().warn("Getting contacts")

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

# init of the flickr api
api, token = initialisationFlickrApi(OPT)


contacts = getContactList(api, token)
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
            print u"\t".join(map(unicode, line))
        except:
            print line

