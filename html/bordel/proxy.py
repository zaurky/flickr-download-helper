#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.api import initialisationFlickrApi, downloadPhotoFromURL
# from flickr_download_helper.backup import FavoritesBackup
# from flickr_download_helper.web_api import PhotoManager, PF

from flickr_download_helper.html_widget import FDH_page, Redirect_Page
import urllib
import cgi
import os


########################################################################################
# setting up all proxy stuffs

config = OptConfigReader()
config.setup()

Logger().setup()
#os.close(sys.stdout.fileno())
#os.close(sys.stderr.fileno())

Logger().warn("####################################################################")

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()
########################################################################################

page = FDH_page()
page.init(header="Proxy redirect")

home_path = '/var/www/cgi-bin/html/'
web_path = 'http://%s/' % '192.168.100.176'

def convert2path(url):
    path = url.replace('http://', os.path.sep.join((home_path, 'proxy/')))
    url = url.replace('http://', os.path.sep.join((web_path, 'proxy/')))
    return (path, url)


form = cgi.FieldStorage()

if 'url' in form:
    # api, token = initialisationFlickrApi(OPT)

    orig_url = form['url'].value
    path, url = convert2path(orig_url)
    redirect = Redirect_Page(url)
    if not os.path.exists(path):
        Logger().debug("%s dont exists, downloading it into %s"%(orig_url, path))
        downloadPhotoFromURL(orig_url, path)

    print redirect

else:
    print page
