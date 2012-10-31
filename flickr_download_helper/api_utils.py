from flickr_download_helper.api import json_request, checkResponse, contentFix
import Flickr.API
import urllib2
import httplib


def method_info(api, token, method_name):
    rsp_json = json_request(api, token, 'flickr.reflection.getMethodInfo', "error while getting method info for %s (%s)", [method_name], method_name=method_name)
    return rsp_json if rsp_json else None


def reflect(api, token):
    request = Flickr.API.Request(method='flickr.reflection.getMethods', auth_token=token, format='json', nojsoncallback=1)
    try:
        response = api.execute_request(request, sign=True, timeout=60)
    except urllib2.HTTPError, e:
        if e.code == 500:
            # try again
            response = api.execute_request(request, sign=True, timeout=60)
        else:
            raise e
    except urllib2.URLError, e:
        if e.errno == 110: # Connection timed out
            # try again
            response = api.execute_request(request, sign=True, timeout=60)
        else:
            raise e
    except httplib.BadStatusLine, e:
        # try again, then fail
        try:
            response = api.execute_request(request, sign=True, timeout=60)
        except:
            return None

    rsp_json = checkResponse(response, "Error while reflecting (%s)", [])
    rsp_json = contentFix(rsp_json)
    return rsp_json['methods']['method']
