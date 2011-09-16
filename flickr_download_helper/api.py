"""
all the flickr_download_helper functions
"""

from flickr_download_helper.config import OPT, INS
from flickr_download_helper.existing import Existing, FileWrite
from flickr_download_helper.existing import file_load, file_dump
from flickr_download_helper.logger import Logger
from flickr_download_helper.downloads_file import DownloadFile
from flickr_download_helper.utils import waitFor
from flickr_download_helper import exif
import Flickr.API
import xml.etree.ElementTree
import sys
# import traceback
import os
import re
import md5
import marshal
import simplejson
import urllib2
import httplib
import datetime

def saveToken(token, token_file):
    # put the token in the configuration directory
    f = open(token_file, 'w')
    f.write(token)
    f.close()

def checkToken(api, token):
    # if we have a token, we check it's still good and put it to None if it's no longer valid
    Logger().debug("debug: calling %s"%('flickr.auth.checkToken'))
    check_request = Flickr.API.Request(method='flickr.auth.checkToken', auth_token=token)
    check_rsp = api.execute_request(check_request)
    # if the request fail, that mean we need to generate the token again
    if check_rsp.code != 200:
        Logger().info("the token is no longer valid")
        token = None
    return token

def getToken(api, token_file):
    # get the auth frob
    Logger().debug("debug: calling %s"%('flickr.auth.getFrob'))
    frob_request = Flickr.API.Request(method='flickr.auth.getFrob')
    frob_rsp = api.execute_request(frob_request)
    if frob_rsp.code == 200:
        frob_rsp_et = xml.etree.ElementTree.parse(frob_rsp)
        if frob_rsp_et.getroot().get('stat') == 'ok':
            frob = frob_rsp_et.findtext('frob')
        else:
            raise Exception("get frob stat != OK")
    else:
        raise Exception("get frob http code != 200 (%s)"%(str(frob_rsp.code)))

    # flickr url to allow this application
    auth_url = api.get_authurl('read', frob=frob)
    # WARNING to what to do in non interactive mode
    Logger().info("auth me:  %s" % (auth_url))
    input = raw_input("done [y]: ")
    if input.lower() not in ('', 'y', 'Y'):
        sys.exit()

    # get the token
    Logger().debug("debug: calling %s"%('flickr.auth.getToken'))
    token_rsp = api.execute_request(Flickr.API.Request(
        method='flickr.auth.getToken', frob=frob, format='json', nojsoncallback=1)
    )
    if token_rsp.code == 200:
        token_rsp_json = simplejson.load(token_rsp)
        if token_rsp_json['stat'] == 'ok':
            token = str(token_rsp_json['auth']['token']['_content'])

            # put the token in the configuration directory
            saveToken(token, token_file)
        else:
            raise Exception("can't get the token! err = %s"%(str(token_rsp_json['message'])))
    else:
        raise Exception("can't get the token! err code = %s"%(str(token_rsp.code)))
    return token

def loadToken(api, token_file):
    token = None

    # try to read the token file
    token = readFile(token_file)

    # check if the token is still ok
    if token: token = checkToken(api, token)

    # if we don't have any token, we generate one
    if token == None: token = getToken(api, token_file)

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
        if opt.proxy: Logger().warn("please check your proxy parameters (%s)"%e.reason[1])
        else: Logger().warn(e.reason[1])
        return 6

    return (api, token)

###########################################################
def getThumbURL(photo, format = 's'):
    return "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg"%(photo['farm'], photo['server'], photo['id'], photo['secret'], format)

def getPhotoURL(photo, format = 'b'):
    return "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg"%(photo['farm'], photo['server'], photo['id'], photo['secret'], format)

def getUserURL(nick):
    return "http://www.flickr.com/photos/%s"%(nick)

def getVideoURL(photo):
    print photo
    print photo['owner']
    return "http://www.flickr.com/photos/%s/%s/play/orig/%s/"%(photo['owner'], photo['id'], photo['secret'])

def contentFix(obj):
    if type(obj) == dict:
        if '_content' in obj: return obj['_content']
        for k in obj:
            obj[k] = contentFix(obj[k])
        return obj
    elif type(obj) == list or type(obj) == tuple:
        ret = []
        for o in obj:
            ret.append(contentFix(o))
        return ret
    else:
        return obj

def method_info(api, token, method_name):
    rsp_json = json_request(api, token, 'flickr.reflection.getMethodInfo', "error while getting method info for %s (%s)", [method_name], method_name=method_name)
    if not rsp_json: return None
    return rsp_json

def reflect(api, token):
    request = Flickr.API.Request(method='flickr.reflection.getMethods', auth_token=token, format='json', nojsoncallback=1)
    try:
        response = api.execute_request(request, sign=True)
    except urllib2.HTTPError, e:
        if e.code == 500:
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except urllib2.URLError, e:
        if e.errno == 110: # Connection timed out
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except httplib.BadStatusLine, e:
        # try again, then fail
        try:
            response = api.execute_request(request, sign=True)
        except:
            return None
    rsp_json = checkResponse(response, "Error while reflecting (%s)", [])
    rsp_json = contentFix(rsp_json)
    return rsp_json['methods']['method']

def json_request2(api, token, method, **kargs):
    message = '%s'
    if 'message' in kargs:
        message = kargs['message']
    message_params = []
    if 'message_params' in kargs:
        message_params = kargs['message_params']

    if 'content_type' in kargs:
        kargs['extras'] = 'media, url_sq, url_t, url_s, url_m, url_l, url_o, url_z, date_upload, owner_name, last_update'

    if not token:
        request = Flickr.API.Request(method=method, format='json', nojsoncallback=1, **kargs)
    else:
        request = Flickr.API.Request(method=method, auth_token=token, format='json', nojsoncallback=1, **kargs)

    request_args = request.args.copy()
    for i in ('auth_token', 'format', 'nojsoncallback', 'method'):
        if i in request_args:
            request_args.pop(i)
    Logger().debug("debug: calling %s %s"%(method, str(request_args)))
    try:
        response = api.execute_request(request, sign=True)
    except urllib2.HTTPError, e:
        if e.code == 500:
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except urllib2.URLError, e:
        if e.errno == 110: # Connection timed out
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except httplib.BadStatusLine, e:
        # try again, then fail
        try:
            response = api.execute_request(request, sign=True)
        except:
            return None
    rsp_json = checkResponse(response, message, message_params)
    return contentFix(rsp_json)

def json_request3(api, token, method, message, message_params, **kargs):
    return json_request2(api, token, method, message=message, message_params=message_params, **kargs)

def json_request(api, token, method, message, message_params, photo_id=None, page=None, per_page=None, user_id=None, photoset_id=None, username=None, collection_id=None, content_type=None, min_date=None, tags=None, count=None, min_upload_date=None, min_fave_date=None, group_id=None, url=None, method_name=None, invitation_only=None):
    if per_page is None:
        per_page = 100
    if not token:
        request = Flickr.API.Request(method=method, format='json', nojsoncallback=1, photo_id=photo_id, page=page, per_page=per_page, user_id=user_id, photoset_id=photoset_id, username=username, collection_id=collection_id, content_type=content_type, min_date=min_date, tags=tags, count=count, min_upload_date=min_upload_date, min_fave_date=min_fave_date, group_id=group_id, url=url, method_name=method_name, invitation_only=invitation_only)
    else:
        request = Flickr.API.Request(method=method, auth_token=token, format='json', nojsoncallback=1, photo_id=photo_id, page=page, per_page=per_page, user_id=user_id, photoset_id=photoset_id, username=username, collection_id=collection_id, content_type=content_type, min_date=min_date, tags=tags, count=count, min_upload_date=min_upload_date, min_fave_date=min_fave_date, group_id=group_id, url=url, method_name=method_name, invitation_only=invitation_only)
    # that's kind of ugly....
    if not photo_id: request.args.pop('photo_id')
    if not page: request.args.pop('page')
    if not per_page: request.args.pop('per_page')
    if not user_id: request.args.pop('user_id')
    if not username: request.args.pop('username')
    if not photoset_id: request.args.pop('photoset_id')
    if not collection_id:request.args.pop('collection_id')
    if not min_date:request.args.pop('min_date')
    if not min_upload_date:request.args.pop('min_upload_date')
    if not tags:request.args.pop('tags')
    if not count:request.args.pop('count')
    if not min_fave_date:request.args.pop('min_fave_date')
    if not group_id:request.args.pop('group_id')
    if not url:request.args.pop('url')
    if not method_name:request.args.pop('method_name')
    if not invitation_only:request.args.pop('invitation_only')
    if not content_type:
        request.args.pop('content_type')
    else:
        request.args['extras'] = 'media, url_sq, url_t, url_s, url_m, url_l, url_o, url_z, date_upload, owner_name, last_update'
    request_args = request.args.copy()
    for i in ('auth_token', 'format', 'nojsoncallback', 'method'):
        if i in request_args:
            request_args.pop(i)
    Logger().debug("debug: calling %s %s"%(method, str(request_args)))
    try:
        response = api.execute_request(request, sign=True)
    except urllib2.HTTPError, e:
        if e.code == 500:
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except urllib2.URLError, e:
        if e.errno == 110: # Connection timed out
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except httplib.BadStatusLine, e:
        # try again, then fail
        try:
            response = api.execute_request(request, sign=True)
        except:
            return None
    rsp_json = checkResponse(response, message, message_params)
    return contentFix(rsp_json)

def checkResponse(response, message, params):
    if response.code != 200:
        params.append("error: %i"%response.code)
        Logger().warn(message % tuple(params))
        return None

    rsp_json = simplejson.load(response)
    if rsp_json['stat'] != 'ok':
        params.append(rsp_json['message'])
        Logger().warn(params)
        Logger().warn(message % tuple(params))
        return None

    return rsp_json

def getPhotoExif(api, token, photo_id):
    rsp_json = json_request(api, token, 'flickr.photos.getExif', "error while getting photo EXIF for  %s (%s)", [photo_id], photo_id=photo_id)
    if not rsp_json: return None

    return rsp_json['photo']['exif']

def getPhotoSize(api, token, photo_id):
    rsp_json = json_request(api, token, 'flickr.photos.getSizes', "error while getting photo size for %s (%s)", [photo_id], photo_id=photo_id)
    if not rsp_json: return None

    return rsp_json['sizes']['size']

def getPhotoInfo(api, token, photo_id):
    rsp_json = json_request(api, token, 'flickr.photos.getInfo', "error while getting photo info for %s (%s)", [photo_id], photo_id=photo_id)
    if not rsp_json: return None

    return rsp_json['photo']

def getPhotosetPhotos(api, token, photoset_id, page = 1):
    rsp_json = json_request(api, token, 'flickr.photosets.getPhotos', "error while getting photos from %s photoset, page %i (%s)", [photoset_id, page], page=page, per_page=100, photoset_id=photoset_id, content_type=7)
    if not rsp_json: return []

    content = rsp_json['photoset']['photo']
    if int(len(content) + (page-1)*100) != int(rsp_json['photoset']['total']):
        next = getPhotosetPhotos(api, token, photoset_id, page+1)
        content.extend(next)
    return content

def getGroupPhotos(api, token, group_id, page = 1, user_id = None, per_page = 500):
    if user_id is None and INS.has_key('put_group_in_session') and INS['put_group_in_session']:
        if INS['groups'].has_key(group_id):
            return INS['groups'][group_id]

    gpath = os.path.join(OPT.groups_full_content_dir, group_id)
    if user_id is None and OPT.group_from_cache:
        if os.path.exists(gpath):
            l_photos = file_load(gpath)
            if l_photos is not None:
                if INS.has_key('put_group_in_session') and INS['put_group_in_session']:
                    INS['groups'][group_id] = l_photos
                return l_photos

    if user_id is None and INS.has_key('put_group_in_session') and INS['put_group_in_session']:
        per_page = 100

    rsp_json = json_request(api, token, 'flickr.groups.pools.getPhotos', "error while getting photos from group %s for user %s, page %i (%s)", [group_id, user_id, page], page=page, per_page=per_page, group_id = group_id, user_id = user_id, content_type=7)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    total = int(len(content) + (page-1)*per_page)
    g_size = int(rsp_json['photos']['total'])

    def _cache_group(group_id, content, gpath=gpath):
        if user_id is None:
            if INS.has_key('put_group_in_session') and INS['put_group_in_session']:
                INS['groups'][group_id] = content
            if INS.has_key('temp_groups') and INS['temp_groups'].has_key(group_id):
                del INS['temp_groups'][group_id]
            file_dump(gpath, content)
        return content

    l_photos = []
    if user_id is None:
        if INS.has_key('temp_groups') and INS['temp_groups'].has_key(group_id):
            l_photos = INS['temp_groups'][group_id]
        elif os.path.exists(gpath):
            l_photos = file_load(gpath)
            if l_photos is None:
                l_photos = []

    if len(l_photos) >= g_size:
        return _cache_group(group_id, l_photos)

    ids = map(lambda x: x['id'], l_photos)
    for i in content:
        if i['id'] not in l_photos:
            l_photos.append(i)

    if len(l_photos) >= g_size:
        return _cache_group(group_id, l_photos)

    content = l_photos
    total = len(l_photos)

    if len(l_photos) < g_size:
        INS['temp_groups'][group_id] = content
        content = getGroupPhotos(api, token, group_id, page+1, user_id, per_page=per_page)

    return content

def searchGroup(api, token, group_name):
    group_url = 'http://www.flickr.com/groups/%s'%group_name
    rsp_json = json_request(api, token, 'flickr.urls.lookupGroup', "error while searching for group %s (%s)", [group_name], url = group_url, content_type=7)
    if not rsp_json: return []

    content = rsp_json['group']
    return content

def getUserGroups(api, token, user_id, page = 1):
    rsp_json = json_request(api, token, 'flickr.people.getPublicGroups', "error while getting user %s groups, page %i (%s)", [user_id, page], page=page, user_id=user_id, content_type=7, invitation_only=1)
    if not rsp_json: return []

    content = rsp_json['groups']['group']
    return content

def getUserPhotos(api, token, user_id, min_upload_date = None, page = 1):
    rsp_json = json_request(api, token, 'flickr.people.getPhotos', "error while getting %s's photos page %i (%s)", [user_id, page], page=page, per_page=100, user_id=user_id, content_type=7, min_upload_date=min_upload_date)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    if int(len(content) + (page-1)*100) != int(rsp_json['photos']['total']):
        next = getUserPhotos(api, token, user_id, min_upload_date, page+1)
        content.extend(next)
    return content

def getUserLastPhotos(api, token, user_id, since, page = 1):
    rsp_json = json_request(api, token, 'flickr.photos.recentlyUpdated', "error while getting last %s's photos page %i (%s)", [user_id, page], page=page, per_page=100, user_id=user_id, content_type=7, min_date=since)
    if not rsp_json: return []
    content = rsp_json['photos']['photo']
    if int(len(content) + (page-1)*100) != int(rsp_json['photos']['total']):
        next = getUserPhotos(api, token, user_id, page+1)
        content.extend(next)
    return content

def selectSmallerPhotoSizeURL(sizes):
    for s in ['Thumbnail', 'Square', 'Medium', 'Large', 'Original']:
        for size in sizes:
            if size['label'] == s:
                return size['source']
    return None

def selectBiggerPhotoSizeURL(sizes):
    for s in ['Original', 'Large', 'Medium', 'Square', 'Thumbnail']:
        for size in sizes:
            if size['label'] == s:
                return size['source']
    return None

def selectMediaURL(sizes, media_type):
    for size in sizes:
        if size['media'] == media_type:
            return size['url']

def getPhotoURLFlickr(api, token, photos, fast_photo_url, thumb = False):
    urls = {}
    i = 1
    length = len(photos)
    for photo in photos:
        if thumb and 'url_sq' in photo:
            url = photo['url_sq']
        elif not thumb and 'url_o' in photo:
            url = photo['url_o']
        elif not thumb and 'url_l' in photo:
            url = photo['url_l']
        elif not thumb and 'url_m' in photo:
            url = photo['url_m']
        else:
            Logger().info("%i/%i get photo size"%(i, length))
            if fast_photo_url and ('media' in photo and photo['media'] == 'photo' or 'media' not in photo):
                if thumb:
                    url = getThumbURL(photo)
                else:
                    url = getPhotoURL(photo)
            else:
                sizes = getPhotoSize(api, token, photo['id'])
                if sizes == None:
                    Logger().error("can't get photo size for %s (the photo is not going to be retrieve)"%photo['id'])
                    continue
                if thumb:
                    url = selectSmallerPhotoSizeURL(sizes)
                else:
                    if 'media' in photo and photo['media'] != 'photo':
                        url = selectMediaURL(sizes, photo['media'])
                        Logger().info("Get the video %s"%(url))
                        DownloadFile().write("%s video %s"%(str(datetime.datetime.now()), url))
                        #url = getVideoURL(photo)
                        #Logger().info("Download %s"%(url))
                    elif 'video' in photo:
                        Logger().info("Get the video %s"%(photo['urls']['url'][0]))
                        url = selectBiggerPhotoSizeURL(sizes)
                        DownloadFile().write("%s video %s"%(str(datetime.datetime.now()), url))
                    else:
                        url = selectBiggerPhotoSizeURL(sizes)
        urls[photo['id']] = url
        i += 1
    return urls

def searchPhotos(api, token, params, page=1):
    request = Flickr.API.Request(method='flickr.photos.search', auth_token=token, format='json', nojsoncallback=1, per_page=100, page=page)
    for p in params:
        request.args[p] = params[p]
    try:
        response = api.execute_request(request, sign=True)
    except urllib2.HTTPError, e:
        if e.code == 500:
            # try again
            response = api.execute_request(request, sign=True)
        else:
            raise e
    except httplib.BadStatusLine, e:
        # try again, then fail
        try:
            response = api.execute_request(request, sign=True)
        except:
            return None
    rsp_json = checkResponse(response, "%s", [])
    ret = contentFix(rsp_json)
    content = ret['photos']['photo']
    if int(len(ret) + (page-1)*100) != int(rsp_json['photos']['total']):
        next = searchPhotos(api, token, params, page+1)
        content.extend(next)
    return content

def getPhotosByTag(api, token, user_id, tags, page=1):
    rsp_json = json_request(api, token, 'flickr.photos.search', "error while searching photos (%s)", [], user_id=user_id, tags=tags, content_type=7, page=page)
    if not rsp_json: return None

    content = rsp_json['photos']['photo']
    if int(len(content) + (page-1)*100) != int(rsp_json['photos']['total']):
        next = getPhotosByTag(api, token, user_id, tags, page+1)
        content.extend(next)
    return content

def getContactPhotos(api, token, page = 1):
    rsp_json = json_request(api, token, 'flickr.photos.getContactsPhotos', "error while getting contact photos (%s)", [], page=page, count=50)
    if not rsp_json: return None

    return rsp_json['photos']['photo']

def getPhotosetInfos(api, token, photoset_id):
    rsp_json = json_request(api, token, 'flickr.photosets.getInfo', "error while getting photoset %s informations (%s)", [photoset_id], photoset_id=photoset_id)
    if not rsp_json: return None

    return rsp_json['photoset']

def getUserPhotosets(api, token, user_id):
    rsp_json = json_request(api, token, 'flickr.photosets.getList', "error while getting photosets for user %s (%s)", [user_id], user_id=user_id)
    if not rsp_json: return None

    return rsp_json['photosets']['photoset']

def getCollectionInfo(api, token, collection_id):
    rsp_json = json_request(api, token, 'flickr.collections.getInfo', "error while getting informations for collection %s (%s)", [collection_id], collection_id=collection_id)
    if not rsp_json: return None

    return rsp_json['collection']

def getCollectionPhotosets(api, token, collection_id, user_id):
    rsp_json = json_request(api, token, 'flickr.collections.getTree', "error while getting photosets for user (%s) collection %s (%s)", [user_id, collection_id], collection_id=collection_id, user_id=user_id, content_type=7)
    if not rsp_json: return None

    return rsp_json['collections']['collection'][0]['set']

def getContactList(api, token, page = 1):
    rsp_json = json_request(api, token, 'flickr.contacts.getList', 'error while getting the contact list (%s)', [], page=page)
    if not rsp_json: return []

    if 'contact' not in rsp_json['contacts']: return []
    content = rsp_json['contacts']['contact']
    if int(len(content) + (page-1)*100) != int(rsp_json['contacts']['total']):
        next = getContactList(api, token, page+1)
        content.extend(next)
    return content

def getUserFavorites(api, token, user_id, page = 1, one_shot = False, per_page = 100, min_fave_date = None):
    rsp_json = json_request(api, token, 'flickr.favorites.getList', 'error while getting %s favorites (%s)', [user_id], user_id=user_id, page=page, content_type=7, per_page=per_page, min_fave_date=min_fave_date)
    if not rsp_json: return []
    content = rsp_json['photos']['photo']
    if not one_shot:
        while (len(content) < int(rsp_json['photos']['total'])):
            if len(content) < int(rsp_json['photos']['total']) - per_page:
                page += 1
                next = getUserFavorites(api, token, user_id, page, min_fave_date=min_fave_date, one_shot=True)
                content.extend(next)
            else:
                break
    return content

def getContactsPhotos(api, token):
    rsp_json = json_request(api, token, 'flickr.photos.getContactsPhotos', 'error while getting the contacts photos (%s)', [])
    if not rsp_json: return []

    return rsp_json['photos']['photo']

def getUserFromID(api, user_id, token = None):
    rsp_json = json_request(api, token, 'flickr.people.getInfo', "error while getting user informations for %s (%s)", [user_id], user_id=user_id)
    if not rsp_json: return None

    return rsp_json['person']

def getUserFromUsername(api, user_name):
    rsp_json = json_request(api, None, 'flickr.people.findByUsername', "erro while getting user %s from username (%s)", [user_name], username=user_name)
    if not rsp_json: return None

    return rsp_json['user']

def getUserFromUrl(api, url, from_nick = False):
    Logger().debug("debug: calling %s"%('flickr.urls.lookupUser'))
    request = Flickr.API.Request(method='flickr.urls.lookupUser', url=url, format='json', nojsoncallback=1)
    response = api.execute_request(request, sign=True)
    if response.code != 200:
        if from_nick:
            raise Exception('error: %s' % str(response.code))
        else:
            Logger().error("while looking up for url %s (error: %s)"%(url, str(response.code)))
            return None

    rsp_json = simplejson.load(response)
    if rsp_json['stat'] != 'ok':
        if from_nick:
            raise Exception(rsp_json['message'])
        else:
            Logger().error("while looking up for url %s (%s)"%(url, rsp_json['message']))
            return None

    user = rsp_json['user']
    return contentFix(user)

def getUserFromNick(api, nick):
    url = getUserURL(nick)
    try:
        return getUserFromUrl(api, url)
    except Exception, e:
        Logger().error("while looking up for user %s (%s)" % (nick, e.message))
        return None

def getUserFromAll(api, u_string):
    user = getUserFromUrl(api, u_string)
    if user: return user
    user = getUserFromNick(api,u_string)
    if user: return user
    user = getUserFromUsername(api, u_string)
    if user: return user
    user = getUserFromID(api, u_string)
    if user: return user
    return None

def readFile(filename):
    if os.path.exists(filename):
        f = open(filename, "rb")
        ret = f.read()
        f.close()
        return ret
    else:
        Logger().error("file not found %s"%filename)
    return None

def downloadPhotoFromURL(url, filename, existing = None, check_exists = False, info = None):
    if not check_exists and os.path.exists(filename):
        Logger().info("%s exists"%info['id'])
        return 0

    if os.path.exists(filename) and info and existing and not existing.isYounger(info['id'], info['lastupdate']):
        Logger().info("%s exists"%info['id'])
        return 0

    content = None
    try:
        content = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        # try a second time and then fail
        Logger().warn("downloading file %s failed %s"%(url, str(e.message)))
        Logger().warn("second try to get the file %s"%url)
        try:
            content = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            Logger().error("while downloading the file from %s (httpe: %s)"%(url, str(e.message)))
        except Exception, e:
            Logger().error("while downloading the file from %s (e: %s)"%(url, str(e)))

    if content == None: return 0

    old_filename = filename
    possible_files = [filename]
    if os.path.exists(filename):
        index = 0
        while os.path.exists(filename):
            index += 1
            f = re.split('\.', filename)
            if index == 1:
                f.insert(len(f)-1, str(index))
            else:
                f[len(f)-2] = str(index)
            filename = '.'.join(f)
            possible_files.append(filename)
        possible_files.pop()

    FileWrite().write(filename, content, existing)
    if info:
        exif.fillFile(None, None, filename, info = info)

    if check_exists and old_filename != filename:
        f = open(filename, 'rb')
        content = f.read()
        f.close()

        new_len = len(content)
        new_md5 = md5.new(content).digest()

        possible_files.reverse()
        for old_filename in possible_files:
            # read old content
            f = open(old_filename, 'rb')
            old_content = f.read()
            f.close()

            if len(old_content) == new_len:
                # get md5
                old_md5 = md5.new(old_content).digest()
                if old_md5 == new_md5:
                    # if the 2 files are the same
                    Logger().debug("addFile %s (%s) == %s (%s)" % \
                        (old_filename, old_md5, filename, new_md5))
                    os.unlink(filename)
                    return 0

    if OPT.new_in_dir and type(OPT.new_in_dir) != bool:
        link_dest = os.path.join(OPT.new_in_dir, os.path.basename(filename))
        if not os.path.exists(link_dest):
            try:
                os.symlink(filename, link_dest)
            except Exception, e:
                Logger().error(e)
    if OPT.daily_in_dir and type(OPT.daily_in_dir) != bool:
        link_dest = os.path.join(OPT.daily_in_dir, '_'.join([os.path.basename(os.path.dirname(filename)), os.path.basename(filename)]))
        if not os.path.exists(link_dest):
            try:
                os.symlink(filename, link_dest)
            except Exception, e:
                Logger().error(e)

    return len(content)

def downloadPhotoFromID(id, filename):
    raise Exception("need to be done %s"%('downloadPhotoFromID'))

def backupUser(user_id, photos, backup_dir):
    f = open(os.path.join(backup_dir, user_id), 'wb')
    marshal.dump(photos, f)
    f.close()

def restoreUser(user_id, backup_dir):
    filepath = os.path.join(backup_dir, user_id)
    if os.path.exists(filepath):
        f = open(filepath, 'rb')
        ret = marshal.load(f)
        f.close()
    else:
        Logger().error("while restoring %s (file not found)" % user_id)
        ret = None
    return ret

def getAllPreviousUsers(backup_dir):
    ret = []
    for root, dir, files in os.walk(backup_dir):
        ret.extend(files)
    return ret

def getPhotoset(opt, api, token, user_name, photoset_id, photoset_name, user_id, existing = None):
        photo_id2destination = {}
        if existing == None:
            existing = Existing(user_id, user_name)
        # prepare the photo directory
        Logger().info("\n== prepare the photo directory")
        try:
            destination = os.path.join(opt.photo_dir, user_name)
            try:
                if opt.retrieve and not os.path.exists(destination): os.mkdir(destination)
            except Exception, e:
                Logger().warn(destination)
                raise e
            if "/" in photoset_name: photoset_name = photoset_name.replace('/', '')
            destination = os.path.join(destination, photoset_name)
            try:
                if opt.retrieve and not os.path.exists(destination): os.mkdir(destination)
            except Exception, e:
                Logger().warn(destination)
                raise e
        except OSError, e:
            if e.errno == 28:
                ret = waitFor("there is not enough space to continue, please delete some files and try again")
                if ret:
                    destination = os.path.join(opt.photo_dir, user_name)
                    if opt.retrieve and not os.path.exists(destination): os.mkdir(destination)
                    destination = os.path.join(destination, photoset_name)
                    if opt.retrieve and not os.path.exists(destination): os.mkdir(destination)
                else:
                    raise e
            elif e.errno == 13:
                ret = waitFor("you dont have the permissions to access %s", destination)
                if ret:
                    destination = os.path.join(opt.photo_dir, user_name)
                    if opt.retrieve and not os.path.exists(destination): os.mkdir(destination)
                    destination = os.path.join(destination, photoset_name)
                    if opt.retrieve and not os.path.exists(destination): os.mkdir(destination)
                else:
                    raise e
            else:
                Logger().error("while doing stuffs in %s"%destination)
                info = sys.exc_info()
                Logger().error(str(e))
                Logger().print_tb(info[2])
                raise e

        photos = getPhotosetPhotos(api, token, photoset_id)
        for photo in photos:
            photo_id2destination[photo['id']] = destination
        total = len(photos)
        photos = existing.grepPhotosDontExists(photos)
        total_after_filter = len(photos)
        if total != total_after_filter:
            Logger().info("filter %d photos" % (total - total_after_filter))

        infos = {}
        for photo in photos: infos[photo['id']] = photo
        urls = getPhotoURLFlickr(api, token, photos, opt.fast_photo_url)
        return (urls, photo_id2destination, destination, infos)


def getStaticContactList():
    contacts_to_get_too = os.path.join(OPT.files_dir, 'contacts_to_get_too')
    if os.path.exists(contacts_to_get_too):
        content = readFile(contacts_to_get_too)
        ret = []
        for line in content.split("\n"):
            if "@" in line:
                ret.append(line)
        return ret
    return []
