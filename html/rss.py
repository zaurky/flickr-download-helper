#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.api import API

from flickr_download_helper.html_widget import FDH_page
import cgi

config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()

# init of the flickr api
api = API(False)

###########################################

form = cgi.FieldStorage()
if 'user_id' in form:
    user_id = form['user_id'].value
else:
    user_id = '53753127@N03'

user = api.getUserFromAll(user_id)
username = user['username']

page = FDH_page()
page.init(css = ('pouet.css'))


page.table(width='100%', height='80%')
page.tr(height='30px')
page.td()
page.a('contacts', href='http://www.flickr.com/people/%s/contacts/by-uploaded/'%username, target='_blank')
page.td.close()
page.td()
page.a('friends', href='http://www.flickr.com/people/%s/contacts/rev/'%username, target='_blank')
page.td.close()
page.td()

page.td.close()
page.tr.close()

page.tr(height='100%')
page.td(colspan='5', valign='top')
page.iframe(src='http://api.flickr.com/services/feeds/activity/all?user_id=%s&format=csv'%user_id, width='50%', height='50%')
page.iframe.close()
page.td.close()
page.td()


page.td.close()
page.tr.close()

page.table.close()


print page
