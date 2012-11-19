"""
all the flickr_download_helper functions
"""

from flickr_download_helper.config import OPT, INS, DEFAULT_PERPAGE
from flickr_download_helper.existing import Existing, FileWrite
from flickr_download_helper.existing import file_load, file_dump
from flickr_download_helper.logger import Logger
from flickr_download_helper.downloads_file import DownloadFile
from flickr_download_helper.utils import (waitFor, readFile, mkdir,
    downloadProtect, getThumbURL, getPhotoURL, getUserURL,
    selectSmallerPhotoSizeURL, selectBiggerPhotoSizeURL, selectMediaURL)
from flickr_download_helper import exif
import sys
import os
import re
import md5
import marshal
from datetime import datetime
from flickr_download_helper.flickr import API as Flickr


class API(object):
    _flickr = None

    def __init__(self, read_command_line=True):
        self._flickr = Flickr(read_command_line)

    def request(self, *attr, **kargs):
        return self._flickr.request(*attr, **kargs)

    # simple methods
    def getPhotoInfo(self, photo_id):
        rsp_json = self.request('photos.getInfo',
            "photo info for %s", [photo_id], photo_id=photo_id)
        return rsp_json['photo'] if rsp_json else None

    def getPhotosetInfos(self, photoset_id):
        rsp_json = self.request('photosets.getInfo',
            "photoset %s informations", [photoset_id], photoset_id=photoset_id)
        return rsp_json['photoset'] if rsp_json else None

    def getCollectionInfo(self, collection_id):
        rsp_json = self.request('collections.getInfo',
            "informations for collection %s", [collection_id],
            collection_id=collection_id)
        return rsp_json['collection'] if rsp_json else None

    def getUserFromID(self, user_id, sign=False):
        rsp_json = self.request('people.getInfo',
            "user informations for %s", [user_id], user_id=user_id, sign=sign)
        return rsp_json['person'] if rsp_json else None

    def getUserFromUsername(self, user_name):
        rsp_json = self.request('people.findByUsername',
            "user %s from username", [user_name], username=user_name,
            sign=False)
        return rsp_json['user'] if rsp_json else None

    def searchGroupByUrl(self, group_url):
        rsp_json = self.request('urls.lookupGroup',
            " info for group %s from url", [group_url], url=group_url,
            content_type=7)
        return rsp_json['group'] if rsp_json else []

    def getPhotoExif(self, photo_id):
        rsp_json = self.request('photos.getExif',
            "photo EXIF for %s", [photo_id], photo_id=photo_id)
        return rsp_json['photo']['exif'] if rsp_json else None

    def getPhotoSize(self, photo_id):
        rsp_json = self.request('photos.getSizes',
            "photo size for %s", [photo_id], photo_id=photo_id)
        return rsp_json['sizes']['size'] if rsp_json else None

    def getUserGroups(self, user_id, page=1):
        rsp_json = self.request('people.getPublicGroups',
            "user %s groups, page %i", [user_id, page],
            page=page, user_id=user_id, content_type=7, invitation_only=1)
        return rsp_json['groups']['group'] if rsp_json else []

    def countGroupPhotos(self, group_id):
        rsp_json = self.request('groups.pools.getPhotos',
            "photos from group %s", [group_id], per_page=1, group_id=group_id)
        return rsp_json['photos']['total'] if rsp_json else 0

    def getUserPhotosets(self, user_id):
        rsp_json = self.request('photosets.getList',
            "photosets for user %s", [user_id], user_id=user_id)
        return rsp_json['photosets']['photoset'] if rsp_json else None

    def getContactsLatestPhotos(self, page=1):
        rsp_json = self.request('photos.getContactsPhotos',
            'the contacts photos', page=page, count=50)
        return rsp_json['photos']['photo'] if rsp_json else []

    def getCollectionPhotosets(self, collection_id, user_id):
        rsp_json = self.request('collections.getTree',
            "photosets for user (%s) collection %s", [user_id, collection_id],
            collection_id=collection_id, user_id=user_id, content_type=7)

        if rsp_json:
            return rsp_json['collections']['collection'][0]['set']

    # loop methods
    def _loop(self, func, path, *attr, **kargs):
        ret = []
        path.reverse()
        page = kargs.pop('page', 1)

        while page < 500:
            kargs['page'] = page
            rsp_json = func(*attr, **kargs)
            if not rsp_json:
                break

            l_path = list(path)
            while l_path:
                rsp_json = rsp_json.get(l_path.pop(), {})

            if not rsp_json:
                break

            ret.extend(rsp_json)
            page += 1

        return ret

    def _getPhotosetPhotos(self, photoset_id, page):
        rsp_json = self.request('photosets.getPhotos',
            "photos from %s photoset, page %i", [photoset_id, page],
            page=page, per_page=DEFAULT_PERPAGE, photoset_id=photoset_id,
            content_type=7)
        return rsp_json or []

    def getPhotosetPhotos(self, photoset_id, page=1):
        return self._loop(self._getPhotosetPhotos,
            ['photoset', 'photo'], photoset_id, page=page)

    def _getUserLastPhotos(self, user_id, since, page):
        rsp_json = self.request('photos.recentlyUpdated',
            "last %s's photos page %i", [user_id, page], page=page,
            per_page=DEFAULT_PERPAGE, user_id=user_id, content_type=7,
            min_date=since)
        return rsp_json or []

    def getUserLastPhotos(self, user_id, since, page=1):
        return self._loop(self._getUserLastPhotos,
            ['photos', 'photo'], user_id, since, page=page)

    def _getPhotosByTag(self, user_id, tags, page):
        rsp_json = self.request('photos.search', "searched photos",
            user_id=user_id, tags=tags, content_type=7, page=page)
        return rsp_json or []

    def getPhotosByTag(self, user_id, tags, page=1):
        return self._loop(self._getPhotosByTag,
            ['photos', 'photo'], user_id, tags, page=page)

    def _searchPhotos(self, user_id, search, page):
        rsp_json = self.request('photos.search', "searched photos",
            user_id=user_id, text=search, content_type=7, page=page)
        return rsp_json or []

    def searchPhotos(self, user_id, search, page=1):
        return self._loop(self._searchPhotos,
            ['photos', 'photo'], user_id, search, page=page)

    def _getContactList(self, page):
        rsp_json = self.request('contacts.getList',
            'the contact list', page=page, sort='time')
        return rsp_json or []

    def getContactList(self, page=1):
        return self._loop(self._getContactList,
            ['contacts', 'contact'], page=page)

    def _getUserFavorites(self, user_id, min_fave_date, page):
        rsp_json = self.request('favorites.getList', '%s favorites',
            [user_id], user_id=user_id, page=page, content_type=7,
            min_fave_date=min_fave_date)
        return rsp_json or []

    def getUserFavorites(self, user_id, min_fave_date=None, page=1):
        return self._loop(self._getUserFavorites,
            ['photos', 'photo'], user_id, min_fave_date, page=page)

    # complicated stuff
    def getGroupPhotosFromScratch(self, group_id, batch=0, page_in_batch=100,
            per_page=500):
        Logger().info("getGroupPhotosFromScratch %s %s" % (group_id, batch))

        content = []
        for spage in range(1, page_in_batch + 1):
            page = spage + batch * page_in_batch
            rsp_json = self.request('groups.pools.getPhotos',
                "photos from group %s, page %i", [group_id, page],
                page=page, per_page=per_page, group_id=group_id, content_type=7)

            if not rsp_json: break

            content.extend(rsp_json['photos']['photo'])

            if page * per_page > int(rsp_json['photos']['total']): break

        return content

    def groupFromScratch(self, group_id):
        rsp_json = self.request('groups.pools.getPhotos',
            "photos from group %s", [group_id], per_page=1, group_id=group_id)
        total = int(rsp_json['photos']['total'])

        Logger().info("groupFromScratch %s %s" % (group_id, total))

        def _get_path(batch):
            return os.path.join(OPT.groups_full_content_dir,
                "%s_%s" % (group_id, batch))

        page_in_batch = 100
        per_page = 500
        maxbatch = 1 + total / (page_in_batch * per_page)

        for batch in range(0, maxbatch):
            content = self.getGroupPhotosFromScratch(group_id, batch,
                page_in_batch, per_page)

            file_dump(_get_path(batch), content)


####


def getPhotoInfo(_, _, photo_id):
    return API().getPhotoInfo(photo_id)


def getPhotosetInfos(_, _, photoset_id):
    return API().getPhotosetInfos(photoset_id)


def getCollectionInfo(_, _, collection_id):
    return API().getCollectionInfo(collection_id)


def getUserFromID(_, user_id, sign=False):
    return API().getUserFromID(user_id, sign)


def getUserFromUsername(_, user_name):
    return API().getUserFromUsername(user_name)


def searchGroupByUrl(_, _, group_url):
    return API().searchGroupByUrl(group_url)


def getPhotoExif(_, _, photo_id):
    return API().getPhotoExif(photo_id)


def getPhotoSize(_, _, photo_id):
    return API().getPhotoSize(photo_id)


def getUserGroups(_, _, user_id, page=1):
    return API().getUserGroups(user_id, page)


def countGroupPhotos(_, _, group_id):
    return API().countGroupPhotos(group_id)


def getUserPhotosets(_, _, user_id):
    return API().getUserPhotosets(user_id)


def getContactsLatestPhotos(_, _, page=1):
    return API().getContactsLatestPhotos(page)


def getCollectionPhotosets(_, _, collection_id, user_id):
    return API().getCollectionPhotosets(collection_id, user_id)


def getPhotosetPhotos(_, _, photoset_id, page=1):
    return API().getPhotosetPhotos(photoset_id, page)


def getUserLastPhotos(_, _, user_id, since, page=1):
    return API().getUserLastPhotos(user_id, since, page)


def getPhotosByTag(_, _, user_id, tags, page=1):
    return API().getPhotosByTag(user_id, tags, page)


def searchPhotos(_, _, user_id, search, page=1):
    return API().searchPhotos(user_id, search, page)


def getContactList(_, _, page=1):
    return API().getContactList(page)


def getUserFavorites(_, _, user_id, page=1, one_shot=False,
        per_page=DEFAULT_PERPAGE, min_fave_date=None):
    return API().getUserFavorites(user_id, page, one_shot, per_page,
        min_fave_date)


def getGroupPhotosFromScratch(_, _, group_id, batch=0, page_in_batch=100,
        per_page=500):
    return API().getGroupPhotosFromScratch(group_id, batch, page_in_batch, per_page)


def groupFromScratch(_, _, group_id):
    return API().groupFromScratch(group_id)


### TODO integrate that in API class
def getGroupPhotos(api, token, group_id, page=1, user_id=None, per_page=None):
    if not user_id and INS.get('put_group_in_session'):
        group_data = INS['groups'].get(group_id)
        if group_data:
            return group_data

    Logger().info("getGroupPhotos %s %s %s" % (group_id, page, user_id))

    gpath = os.path.join(OPT.groups_full_content_dir, group_id)
    if not user_id and OPT.group_from_cache:
        if os.path.exists(gpath):
            l_photos = file_load(gpath)
            if l_photos:
                Logger().debug("%s loaded from cache" % group_id)

                if INS.get('put_group_in_session'):
                    INS['groups'][group_id] = l_photos

                return l_photos

    if not per_page:
        if not user_id and INS.get('put_group_in_session') and \
                not OPT.group_from_cache:
            per_page = DEFAULT_PERPAGE
        else:
            per_page = 500

    rsp_json = Flickr().request('groups.pools.getPhotos',
        "photos from group %s for user %s, page %i", [group_id, user_id, page],
        page=page, per_page=per_page, group_id=group_id, user_id=user_id,
        content_type=7)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    g_size = int(rsp_json['photos']['total'])
    total = len(content) + (page - 1) * per_page

    Logger().debug("%s has %d results" % (group_id, g_size))

    def _cache_group(group_id, content, gpath=gpath):
        if not user_id:
            if INS.get('put_group_in_session'):
                INS['groups'][group_id] = content

            INS.get('temp_groups', {}).pop(group_id)
            file_dump(gpath, content)
        return content

    temp_groups_key = "%s%s" % (group_id, user_id or '')
    l_photos = INS.get('temp_groups', {}).get(temp_groups_key, [])

    if not user_id and not l_photos and os.path.exists(gpath):
        Logger().debug("load file %s" % gpath)
        l_photos = file_load(gpath) or []

    if len(l_photos) >= g_size:
        return _cache_group(group_id, l_photos)

    ids = map(lambda x: x['id'], l_photos)
    for i in content:
        if i['id'] not in ids:
            l_photos.append(i)

    # remove duplicates on id
    l_photos = dict(map(lambda x: (x['id'], x), l_photos)).values()

    Logger().debug("getGroupPhotos %d %d %d" % (
        len(l_photos), g_size, len(content)))

    if len(l_photos) >= g_size or len(content) == 0:
        return _cache_group(group_id, l_photos)

    content = l_photos
    total = len(l_photos)

    if total < g_size:
        if g_size - total < 500:
            per_page = DEFAULT_PERPAGE

        INS['temp_groups'][temp_groups_key] = content
        content = getGroupPhotos(api, token, group_id, page + 1, user_id,
            per_page=per_page)

    return content


def getUserPhotos(api, token, user_id, min_upload_date=None, page=1,
        limit=None):
    per_page = DEFAULT_PERPAGE if not limit else limit

    kargs = {
        'page': page,
        'per_page': per_page,
        'user_id': user_id,
        'content_type': 7,
    }

    if min_upload_date:
        kargs['min_upload_date'] = min_upload_date

    rsp_json = Flickr().request('people.getPhotos',
        "%s's photos page %i", [user_id, page], **kargs)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    total = int(rsp_json['photos']['total'])

    if limit:
        return content

    if len(content) + (page - 1) * per_page != total:
        content.extend(getUserPhotos(api, token, user_id, min_upload_date,
            page + 1))

    return content


def getPhotoURLFlickr(api, token, photos, fast_photo_url, thumb=False):
    urls = {}
    length = len(photos)

    for (counter, photo) in enumerate(photos):
        if thumb:
            url = photo.get('url_sq')
        elif not thumb:
            url = photo.get('url_o', photo.get('url_l', photo.get('url_m')))

        if not url:
            Logger().info("%i/%i get photo size" % (counter + 1, length))

            if fast_photo_url and photo.get('media', 'photo') == 'photo':
                url = getThumbURL(photo) if thumb else getPhotoURL(photo)
            else:
                sizes = getPhotoSize(api, token, photo['id'])
                if not sizes:
                    Logger().error("can't get photo size for %s (the photo " \
                        "is not going to be retrieve)" % photo['id'])
                    continue

                if thumb:
                    url = selectSmallerPhotoSizeURL(sizes)
                else:
                    if photo.get('media', 'photo') != 'photo':
                        url = selectMediaURL(sizes, photo['media'])
                        Logger().info("Get the video %s" % (url))
                        DownloadFile().write("%s video %s" % (
                            str(datetime.now()), url))
                    elif 'video' in photo:
                        Logger().info("Get the video %s" % (
                            photo['urls']['url'][0]))
                        url = selectBiggerPhotoSizeURL(sizes)
                        DownloadFile().write("%s video %s" % (
                            str(datetime.now()), url))
                    else:
                        url = selectBiggerPhotoSizeURL(sizes)

        urls[photo['id']] = url

    return urls


def searchGroup(api, token, group_name):
    return searchGroupByUrl(api, token,
        'http://www.flickr.com/groups/%s' % group_name)


def getUserFromUrl(api, url):
    rsp_json = Flickr().request('urls.lookupUser',
        "lookup for user url %s", [url], url=url, sign=False)
    return rsp_json['user'] if rsp_json else {}


def getUserFromNick(api, nick):
    try:
        return getUserFromUrl(api, getUserURL(nick))
    except Exception, e:
        Logger().error("while looking up for user %s (%s)" % (nick, e.message))


def getUserFromAll(api, u_string):
    for func in (
                getUserFromUrl, getUserFromNick,
                getUserFromUsername, getUserFromID,
            ):
        user = func(api, u_string)
        if user: return user


def getUser(api, token):
    Logger().info("\n== get user_id")

    if not OPT.user_id:
        if OPT.url:
            return getUserFromUrl(api, OPT.url)
        elif OPT.nick:
            return getUserFromNick(api, OPT.nick)
        elif OPT.username:
            return getUserFromUsername(api, OPT.username)
        else:
            Logger().error("can't get any user_id")
    elif OPT.user_hash.get(OPT.user_id):
        return OPT.user_hash[OPT.user_id]
    else:
        return getUserFromID(api, OPT.user_id)


def downloadPhotoFromURL(url, filename, existing=None, check_exists=False,
        info=None):

    if not check_exists and os.path.exists(filename):
        Logger().info("%s exists" % info['id'])
        return 0

    if os.path.exists(filename) and info and existing and \
            not existing.isYounger(info['id'], info['lastupdate']):
        Logger().info("%s exists" % info['id'])
        return 0

    content = downloadProtect(url)

    if not content: return 0

    old_filename = filename
    possible_files = [filename]
    if os.path.exists(filename):
        index = 0
        while os.path.exists(filename):
            index += 1
            fname = re.split('\.', filename)
            if index == 1:
                fname.insert(len(fname) - 1, str(index))
            else:
                fname[len(fname) - 2] = str(index)

            filename = '.'.join(fname)
            possible_files.append(filename)

        possible_files.pop()

    FileWrite().write(filename, content, existing)

    if info:
        try:
            exif.fillFile(None, None, filename, info=info)
        except Exception, err:
            Logger().warn("Failed to put exif")
            Logger().warn(err)

    if check_exists and old_filename != filename:
        fhandle = open(filename, 'rb')
        content = fhandle.read()
        fhandle.close()

        new_len = len(content)
        new_md5 = md5.new(content).digest()

        possible_files.reverse()
        for old_filename in possible_files:
            # read old content
            fhandle = open(old_filename, 'rb')
            old_content = fhandle.read()
            fhandle.close()

            if len(old_content) == new_len:
                # get md5
                old_md5 = md5.new(old_content).digest()
                if old_md5 == new_md5:
                    # if the 2 files are the same
                    Logger().debug("addFile %s == %s" % \
                        (old_filename, filename))
                    os.unlink(filename)
                    return 0
                else:
                    Logger().debug("addFile %s != %s (md5)" % \
                        (old_filename, filename))
            else:
                Logger().debug("addFile %s (%s) != %s (%s) len" % \
                    (old_filename, len(old_content), filename, new_len))

    if OPT.new_in_dir and not isinstance(OPT.new_in_dir, bool):
        link_dest = os.path.join(OPT.new_in_dir, os.path.basename(filename))

        if not os.path.exists(link_dest):
            try:
                os.symlink(filename, link_dest)
            except Exception, err:
                Logger().error(err)

    if OPT.daily_in_dir and not isinstance(OPT.daily_in_dir, bool):
        link_dest = os.path.join(
            OPT.daily_in_dir,
            '_'.join([
                os.path.basename(os.path.dirname(filename)),
                os.path.basename(filename),
            ]))

        if not os.path.exists(link_dest):
            try:
                os.symlink(filename, link_dest)
            except Exception, err:
                Logger().error(err)

    return len(content)


def backupUser(user_id, photos, backup_dir):
    fhandle = open(os.path.join(backup_dir, user_id), 'wb')
    marshal.dump(photos, fhandle)
    fhandle.close()


def restoreUser(user_id, backup_dir):
    filepath = os.path.join(backup_dir, user_id)
    if os.path.exists(filepath):
        fhandle = open(filepath, 'rb')
        ret = marshal.load(fhandle)
        fhandle.close()
    else:
        Logger().error("while restoring %s (file not found)" % user_id)
        return
    return ret


def _mkdir_photoset(destination):
    mkdir(os.path.dirname(destination))
    mkdir(destination)


def getPhotoset(opt, api, token, user_name, photoset_id, photoset_name,
            user_id, existing=None):
        photo_id2destination = {}
        if not existing:
            existing = Existing(user_id, user_name)

        photoset_name = photoset_name.replace('/', '')
        destination = os.path.join(opt.photo_dir, user_name, photoset_name)

        # prepare the photo directory
        Logger().info("\n== prepare the photo directory")
        try:
            _mkdir_photoset(destination)
        except OSError, err:
            errors = {
                28: "there is not enough space to continue, " \
                    "please delete some files and try again",
                13: "you dont have the permissions to access %s" % \
                    destination,
            }
            if err.errno in errors:
                if waitFor(errors[err.errno]):
                    _mkdir_photoset(destination)
                else:
                    raise
            else:
                Logger().error("while doing stuffs in %s" % destination)
                info = sys.exc_info()
                Logger().error(str(err))
                Logger().print_tb(info[2])
                raise

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
        return filter(lambda line: '@' in line, content.split('\n'))

    return []
