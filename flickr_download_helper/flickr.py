import Flickr.API
import urllib2
import httplib
import simplejson

from flickr_download_helper.config import DEFAULT_PERPAGE
from flickr_download_helper.logger import Logger


def json_request(api, token, method, message, msg_params=[], **kargs):
    if token:
        kargs['auth_token'] = token

    if 'content_type' in kargs:
        kargs['extras'] = 'media, url_sq, url_t, url_s, url_m, url_l, url_o, url_z, date_upload, owner_name, last_update'

    kargs.update({
        'method': 'flickr.%s' % method,
        'format': 'json',
        'nojsoncallback': 1,
        'per_page': kargs.get('per_page', DEFAULT_PERPAGE),
        'timeout': 10,
    })

    msg = 'error while getting ' + message + ' (%s)'

    # XXX this is debug
    kargs = dict(filter(lambda (k,v): v is not None, kargs.items()))

    request = Flickr.API.Request(**kargs)
    request_args = str(dict(filter(lambda (arg, value):
        arg not in ('auth_token', 'format', 'nojsoncallback', 'method'),
        request.args.items())))

    Logger().debug("calling %s(%s)" % (method, request_args))

    try:
        resp = api.execute_request(request, sign=True)
    except urllib2.HTTPError, e:
        if e.code == 500:
            # try again
            resp = api.execute_request(request, sign=True)
        else:
            raise
    except urllib2.URLError, e:
        if e.errno == 110: # Connection timed out
            # try again
            resp = api.execute_request(request, sign=True)
        else:
            raise
    except httplib.BadStatusLine, e:
        # try again, then fail
        try:
            resp = api.execute_request(request, sign=True)
        except:
            raise

    return parseResponse(resp, msg, msg_params)


def contentFix(obj):
    if type(obj) == dict:
        if '_content' in obj: return obj['_content']
        return dict(zip(obj.keys(), map(contentFix, obj.values())))
    elif isinstance(obj, (list, tuple)):
        return map(contentFix, obj)
    return obj


def checkResponse(response, message, params):
    if response.code != 200:
        params.append("error: %i" % response.code)
        Logger().warn(message % tuple(params))
        return

    rsp_json = simplejson.load(response)
    if rsp_json['stat'] != 'ok':
        params.append(rsp_json['message'])
        Logger().warn(message % tuple(params))
        return

    return rsp_json


def parseResponse(response, message, params):
    return contentFix(checkResponse(response, message, params))
