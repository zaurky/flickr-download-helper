import Flickr.API
import urllib2
import httplib
import simplejson
import sys
import os

from flickr_download_helper.config import DEFAULT_PERPAGE, OPT
from flickr_download_helper.logger import Logger
from flickr_download_helper.utils import singleton
from flickr_download_helper.config import OptConfigReader, OptReader
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.token import initialisationFlickrApi


@singleton
class API(object):

    def __init__(self, read_command_line=True):
        config = OptConfigReader()
        config.setup()

        opt = OptReader()
        ret = opt.read(read_command_line)
        if read_command_line and ret:
            return ret

        Logger().setup()
        Logger().warn("##########################################################")
        Logger().warn("%s (running as %s)" % (" ".join(sys.argv), os.getpid()))
        Logger().debug("LANG is %s" % os.environ.get('LANG'))

        proxy = FDHProxySettings()
        proxy.setValues(OPT)
        proxy.activate()

        # init of the flickr api
        token = initialisationFlickrApi(OPT)
        if not isinstance(token, (list, tuple)) or len(token) != 2:
            if token != 6:
                Logger().error("Couldn't init flickr api")
                Logger().error(token)

            raise Exception("Couldn't init flickr api %s" % (token,))
        self.api, self.token = token

    def request(self, method, message, msg_params=None, **kargs):
        sign = kargs.pop('sign', True)
        if sign:
            kargs['auth_token'] = self.token

        if not msg_params:
            msg_params = []

        if 'content_type' in kargs:
            kargs['extras'] = 'media, url_sq, url_t, url_s, url_m, url_l, ' \
                'url_o, url_z, date_upload, owner_name, last_update'

        kargs.update({
            'method': 'flickr.%s' % method,
            'format': 'json',
            'nojsoncallback': 1,
            'per_page': kargs.get('per_page', DEFAULT_PERPAGE),
            'timeout': 10,
        })

        msg = 'error while getting ' + message + ' (%s)'

        # XXX this is debug
        kargs = dict(filter(lambda (key, val): val is not None, kargs.items()))

        request = Flickr.API.Request(**kargs)
        request_args = str(dict(filter(lambda (arg, value):
            arg not in ('auth_token', 'format', 'nojsoncallback', 'method'),
            request.args.items())))

        Logger().debug("calling %s(%s)" % (method, request_args))

        try:
            resp = self.api.execute_request(request, sign=True)
        except urllib2.HTTPError, err:
            if err.code == 500:
                # try again
                resp = self.api.execute_request(request, sign=True)
            else:
                raise
        except urllib2.URLError, err:
            if err.errno == 110: # Connection timed out
                # try again
                resp = self.api.execute_request(request, sign=True)
            else:
                raise
        except httplib.BadStatusLine:
            # try again, then fail
            try:
                resp = self.api.execute_request(request, sign=True)
            except:
                raise

        return self.parse_response(resp, msg, msg_params)

    def content_fix(self, obj):
        if type(obj) == dict:
            if '_content' in obj: return obj['_content']
            return dict(zip(obj.keys(), map(self.content_fix, obj.values())))
        elif isinstance(obj, (list, tuple)):
            return map(self.content_fix, obj)
        return obj

    def check_response(self, response, message, params):
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

    def parse_response(self, response, message, params):
        return self.content_fix(self.check_response(response, message, params))
