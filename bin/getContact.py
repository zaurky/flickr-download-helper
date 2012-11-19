#!/usr/bin/python

from flickr_download_helper.api import API
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
api = API()


def encode(string):
    if not isinstance(string, (str, unicode)): return str(string)
    try: return string.encode('latin1')
    except: return string.encode('utf8')

contact_id = OPT.user_id
line = []

c = api.getUserFromID(contact_id, True)

if OPT.getContactFields:
    for field in OPT.getContactFields:
        if field in c:
            line.append(c[field].strip())

print "\t".join(map(encode, line))
