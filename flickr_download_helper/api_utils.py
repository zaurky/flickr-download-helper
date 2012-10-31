from flickr_download_helper.api import json_request, checkResponse, contentFix
import Flickr.API
import urllib2
import httplib


def method_info(api, token, method_name):
    rsp_json = json_request(api, token, 'flickr.reflection.getMethodInfo', "error while getting method info for %s (%s)", [method_name], method_name=method_name)
    return rsp_json if rsp_json else None


def reflect(api, token):
    request = Flickr.API.Request(method='flickr.reflection.getMethods', auth_token=token, format='json', nojsoncallback=1)
    kargs = {'sign': True, 'timeout': 60}
    try:
        response = api.execute_request(request, **kargs)
    except urllib2.HTTPError, e:
        if e.code == 500:
            response = api.execute_request(request, **kargs)
        else:
            raise
    except urllib2.URLError, e:
        if e.errno == 110: # Connection timed out
            response = api.execute_request(request, **kargs)
        else:
            raise
    except httplib.BadStatusLine, e:
        try:
            response = api.execute_request(request, **kargs)
        except:
            return None

    rsp_json = contentFix(checkResponse(response, "Error while reflecting (%s)", [])
    return rsp_json['methods']['method']
