from flickr_download_helper.config import OPT, OptConfigReader
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.logger import Logger
from flickr_download_helper.api import initialisationFlickrApi
from flickr_download_helper.api import *

config = OptConfigReader()
config.setup()

Logger().setup()
Logger().warn("####################################################################")

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

api, token = initialisationFlickrApi(OPT)

print """
contact_name = ''
contact = getUserFromAll(api, contact_name)
photos = getUserPhotos(api, token, contact['id'])
other = filter(lambda x: x['media'] != 'photo', photos)
v = other[0]
info = getPhotoInfo(api, token, v['id'])
size = getPhotoSize(api, token, v['id'])
"""
