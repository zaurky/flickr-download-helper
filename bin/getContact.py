#!/usr/bin/python

from flickr_download_helper.api import API
from flickr_download_helper.config import OPT


# init of the flickr api
api = API()


def encode(string):
    if not isinstance(string, (str, unicode)):
        return str(string)
    try:
        return string.encode('latin1')
    except:
        return string.encode('utf8')


line = []

c = api.getUserFromID(OPT.user_id, True)

if OPT.getContactFields:
    for field in OPT.getContactFields:
        if field in c:
            line.append(c[field].strip())


print "\t".join(map(encode, line))
