#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings

from flickr_download_helper.html_widget import FDH_page
import cgi

config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()


def display():
    form = cgi.FieldStorage()

    page = FDH_page()
    page.init(css = ('/styles/image.css'))
    page.script(src='/javascript/popupmenu.js', type='text/javascript')
    page.script.close()
    page.script(src='/javascript/image_menu.js', type='text/javascript')
    page.script.close()

    try:
        src = form['src'].value
        username = ''
        if 'username' in form:
            username = form['username'].value
        user_id = form['user_id'].value
        photo_id = form['photo_id'].value

        page.img(src=src, id=photo_id)
        page.script('setMenu("%s");'%(photo_id), type="text/javascript")

        return page
    except Exception, e:
        page.p(e.message)
        return page

###########################################

print display()


