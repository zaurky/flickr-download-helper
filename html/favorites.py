#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
# from flickr_download_helper.api import initialisationFlickrApi # , getContactList, getUserFavorites
from flickr_download_helper.backup import FavoritesBackup
from flickr_download_helper.web_api import PhotoManager, PF
from flickr_download_helper.local_proxy import LocalProxy

from flickr_download_helper.html_widget import FDH_page
import urllib
import cgi

config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

form = cgi.FieldStorage()

page_num = 0
perpage = 25
user_id = ''

if 'page_num' in form: page_num = int(form['page_num'].value)
if 'perpage' in form: perpage = int(form['perpage'].value)
if 'user_id' in form: user_id = form['user_id'].value

###########################################
def display_photo(page, photo):
    id = photo['id']
    user_id = photo['contact']['nsid']
    username = '' # photo['contact']['username'].decode('utf-8')

    url = photo['url_s']
    if 'url_l' in photo: url = photo['url_l']
    elif 'url_m' in photo: url = photo['url_m']

    style = 'border: solid red 0px;'
    if 'state' in photo:
        if photo['state'] == PF.MARKED:
            style = 'border: solid red 1px'

    page.a(href=url, target='_blank', onMouseover="showmenu(event, '%s', '180px', '%s');"%(id, url), onMouseout="delayhidemenu()")
    page.img(src=photo['url_sq'], alt="%s (%s) : %s"%(username, user_id, id), style=style)
    # page.img(src='proxy.py?%s'%urllib.urlencode({"url":photo['url_sq']}), alt="%s (%s) : %s"%(username, user_id, id), style=style)
    page.a.close()

###########################################
page = FDH_page()
page.init(css = ('/styles/favorites.css'), header="Favorites (page %i)"%page_num)
page.script('', src='/javascript/menu2.js', type='text/javascript')
page.script('', src='/javascript/ajax.js', type='text/javascript')

manager = PhotoManager(FavoritesBackup())
photos = manager.getPhotos()

page.div()

if page_num != 0:
    page.a("Previous", href='favorites.py?%s'%urllib.urlencode({ 'page_num':page_num-1, 'perpage':perpage, 'user_id':user_id }))

if (page_num+1)*perpage < len(photos):
    page.a("Next", href='favorites.py?%s'%urllib.urlencode({ 'page_num':page_num+1, 'perpage':perpage, 'user_id':user_id }))

page.a("Export", href="favorites_action.py?action=export")

page.div.close()

lproxy = LocalProxy()
photos = lproxy.modifyProxyPhotos(photos[page_num*perpage:(page_num+1)*perpage], 'url_sq')

for photo in photos: #photos[page_num*perpage:(page_num+1)*perpage]:
    display_photo(page, photo)

print page

###############################################
#    page.a(
#            href="image.py?%s"%(urllib.urlencode({
#                "src":url,
#                "username":username,
#                "user_id":user_id,
#                "photo_id":id
#            })),
#            target='_blank',
#            style='border: solid red 0px;'
#        )

