from flickr_download_helper.config import OPT, OptConfigReader
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.logger import Logger
from flickr_download_helper.api import *
import flickr_download_helper.api


api = API(False)


print "#" * 80 + "\n"
print "\t" + "\n\t".join(filter(lambda func:
    'get' in func or 'search' in func,
    dir(flickr_download_helper.api)
))

print "\t" + "\n\tapi.".join(filter(lambda func:
    func.startswith('get') or func.startswith('search'),
    dir(api)
))

print "\n" + "#" * 80
print """
contact_name = ''
contact = api.getUserFromAll(contact_name)
photos = api.getUserPhotos(contact['id'])

other = filter(lambda x: x['media'] != 'photo', photos)

photo = photos[0]
info = api.getPhotoInfo(photo['id'])
size = api.getPhotoSize(photo['id'])
"""
print "\n" + "#" * 80


me = OPT.my_id
