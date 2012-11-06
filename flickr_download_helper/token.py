from flickr_download_helper.logger import Logger
from flickr_download_helper.utils import readFile
import Flickr.API
import xml.etree.ElementTree
import simplejson
import urllib2


def saveToken(token, token_file):
    # put the token in the configuration directory
    f = open(token_file, 'w')
    f.write(token)
    f.close()


def checkToken(api, token):
    # if we have a token, we check it's still good and put it to None if it's no longer valid
    Logger().debug("debug: calling flickr.auth.checkToken")
    check_request = Flickr.API.Request(
        method='flickr.auth.checkToken', auth_token=token, timeout=60)
    check_rsp = api.execute_request(check_request)

    # if the request fail, that mean we need to generate the token again
    if check_rsp.code != 200:
        Logger().info("the token is no longer valid")
        token = None
    return token


def getToken(api, token_file):
    # get the auth frob
    Logger().debug("debug: calling flickr.auth.getFrob")
    frob_request = Flickr.API.Request(method='flickr.auth.getFrob', timeout=60)
    frob_rsp = api.execute_request(frob_request)

    if frob_rsp.code == 200:
        frob_rsp_et = xml.etree.ElementTree.parse(frob_rsp)
        if frob_rsp_et.getroot().get('stat') == 'ok':
            frob = frob_rsp_et.findtext('frob')
        else:
            raise Exception("get frob stat != OK")
    else:
        raise Exception("get frob http code != 200 (%s)" % (str(frob_rsp.code)))

    # flickr url to allow this application
    auth_url = api.get_authurl('read', frob=frob)

    # WARNING to what to do in non interactive mode
    Logger().info("auth me:  %s" % (auth_url))
    if raw_input("done [y]: ").lower() not in ('', 'y', 'Y'):
        sys.exit()

    # get the token
    Logger().debug("debug: calling flickr.auth.getToken")
    token_rsp = api.execute_request(Flickr.API.Request(
        method='flickr.auth.getToken', frob=frob, format='json',
        nojsoncallback=1, timeout=60
    ))

    if token_rsp.code == 200:
        token_rsp_json = simplejson.load(token_rsp)
        if token_rsp_json['stat'] == 'ok':
            token = str(token_rsp_json['auth']['token']['_content'])

            # put the token in the configuration directory
            saveToken(token, token_file)
        else:
            raise Exception("can't get the token! err = %s" % (str(token_rsp_json['message'])))
    else:
        raise Exception("can't get the token! err code = %s" % (str(token_rsp.code)))

    return token


def loadToken(api, token_file):
    token = None

    # try to read the token file
    token = readFile(token_file)

    # check if the token is still ok
    if token:
        token = checkToken(api, token)

    # if we don't have any token, we generate one
    if not token:
        token = getToken(api, token_file)

    return token


def initialisationFlickrApi(opt):
    # get the flickr api
    Logger().info("\n== get the flickr api")
    api = Flickr.API.API('af8eea5e1df718031d90e3f16d670e5d', '52e25a0bbd5a6be1')

    # get token
    Logger().info("\n== get token")
    try:
        token = loadToken(api, opt.token_file)
    except urllib2.URLError, e:
        if opt.proxy:
            Logger().warn("please check your proxy parameters (%s)" % e.reason[1])
        else:
            Logger().warn(e.reason[1])
        return 6

    return (api, token)
