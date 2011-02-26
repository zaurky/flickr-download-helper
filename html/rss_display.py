#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper import getUserFromID, initialisationFlickrApi, checkResponse

from flickr_download_helper.html_widget import FDH_page
import cgi

from Flickr.API import Request
import urllib2
# import httplib
import simplejson

config = OptConfigReader()
config.setup()

## start the logger
Logger().setup()

proxy = FDHProxySettings()
proxy.setValues(OPT)
proxy.activate()

# init of the flickr api
api, token = initialisationFlickrApi(OPT)

###########################################

form = cgi.FieldStorage()
if 'user_id' in form:
    user_id = form['user_id'].value
else:
    user_id = '53753127@N03'

user = getUserFromID(api, user_id)
username = user['username']

page = FDH_page()
page.init(css = ('pouet.css'))

page.h3("Welcome %s"%username)

import md5
def signature(api, arguments):
    return md5.md5(api.secret + arguments.replace('=', '').replace('&', '')).hexdigest()


args = {
    'user_id':user_id,
    'format':'json',
    'nojsoncallback':'1',
    'auth_token':token,
    'api_key':api.key
}
#url = 'http://api.flickr.com/services/feeds/activity/all' #?user_id=%s&format=csv'%user_id
#url = 'http://api.flickr.com/services/feeds/activity/all?user_id=%s&format=json&auth_token=%s&nojsoncallback=1&secret=%s'%(user_id, token, api.secret)
#arguments = 'user_id=%s&format=json&nojsoncallback=1&auth_token=%s&api_key=%s'%(user_id, token, api.key)
# sign = signature(api, arguments)
# Sign args as they are now, except photo
args_to_sign = {}
for (k,v) in args.items():
    if k not in ('photo'):
        args_to_sign[k] = v

args['api_sig'] = api._sign_args(args_to_sign)


#sign = request.args['api_sig'] = self._sign_args(args_to_sign)
# url = 'http://api.flickr.com/services/feeds/activity/all?%s&api_sig=%s'%(arguments, 'api_sign')
args_str = '&'.join(map(lambda (k,v): '%s=%s'%(k,v) , args.items()))
url = 'http://api.flickr.com/services/feeds/activity/all?%s' % args_str
#      'http://api.flickr.com/services/feeds/groups_pool.gne'

print page
try:
    request = Request(url) # , auth_token=token, nojsoncallback=1, user_id=user_id, format='json')
    print url
    print request.get_method()
    response = api.execute_request(request, sign=True)
#    content = api.execute_request(request).read()
    rsp_json = checkResponse(response, "can't get the rss stream for user %s", [user_id])
except urllib2.HTTPError, e:
    print e
    print dir(e)
    for i in ('args', 'close', 'code', 'errno', 'filename', 'fileno', 'fp', 'geturl', 'hdrs', 'headers', 'info', 'message', 'msg', 'next', 'read', 'readline', 'readlines', 'strerror', 'url'):
        print getattr(e, i)
    print e.message
    # try a second time and then fail
#    try:
#        content = urllib2.urlopen(url).read()
#    except Exception, e:
#        raise e


#rsp_json = simplejson.load(content)
print rsp_json





