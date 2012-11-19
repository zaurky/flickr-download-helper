#!/usr/bin/python

#import markup
import cgi

from flickr_download_helper.api import API
from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.existing import Existing
from flickr_download_helper.html_widget import FDH_page

page = FDH_page()
page.init(css = ('pouet.css'))

form = cgi.FieldStorage()
user = None
if 'user' in form: user = form['user'].value

## Load configuration from file
config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()

###########################

# init of the flickr api
api = API()

if user:
    user = api.getUserFromAll()
    page.h3(user['username'], onclick='alert("'+user['id']+'");')
    page.a('rss', href='rss.py?user_id=%s'%(user['id']),)
    page.br()
    photos = api.getUserPhotos(user['id'])
    existing = Existing().grepPhotosExists(photos)
    existing_ids = map(lambda e:e['id'], existing)
    urls = api.getPhotoURLFlickr(photos, True, True)
    for id in urls:
        if id in existing_ids:
            style = 'border:1px red solid;'
        else:
            style = 'border:1px blue solid;'
        page.img(src=urls[id], width=100, height=80, alt=id, onclick='alert("'+id+'");', style=style)
else:
    page.h3("showing last photos of your contacts")

#     params = {"contacts":"ff", "min_upload_date":"1287399869", "extra":"url_sq"}
#     photos = api.searchPhotos(params)
    photos = api.getContactsLatestPhotos()
    p = {}
    for photo in photos:
        p[photo['id']] = photo['owner']
    urls = api.getPhotoURLFlickr(photos, True, True)

    for id in urls:
        page.img(src=urls[id], width=100, height=80, alt=id, onclick='alert("user: '+p[id]+'; image: '+id+'");')

print page


