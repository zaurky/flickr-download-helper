"""
all the flickr_download_helper functions
"""

from flickr_download_helper.config import OPT, INS, DEFAULT_PERPAGE
from flickr_download_helper.existing import Existing, FileWrite
from flickr_download_helper.existing import file_load, file_dump
from flickr_download_helper.token import initialisationFlickrApi
from flickr_download_helper.logger import Logger
from flickr_download_helper.downloads_file import DownloadFile
from flickr_download_helper.utils import (waitFor, readFile, mkdir,
    downloadProtect, getThumbURL, getPhotoURL, getUserURL,
    selectSmallerPhotoSizeURL, selectBiggerPhotoSizeURL, selectMediaURL)
from flickr_download_helper.flickr import json_request
from flickr_download_helper import exif
import xml.etree.ElementTree
import sys
import os
import re
import md5
import marshal
from datetime import datetime


def getPhotoInfo(api, token, photo_id):
    rsp_json = json_request(api, token, 'photos.getInfo',
        "photo info for %s", [photo_id], photo_id=photo_id)
    return rsp_json['photo'] if rsp_json else None


def getPhotosetInfos(api, token, photoset_id):
    rsp_json = json_request(api, token, 'photosets.getInfo',
        "photoset %s informations", [photoset_id], photoset_id=photoset_id)
    return rsp_json['photoset'] if rsp_json else None


def getCollectionInfo(api, token, collection_id):
    rsp_json = json_request(api, token, 'collections.getInfo',
        "informations for collection %s", [collection_id],
        collection_id=collection_id)
    return rsp_json['collection'] if rsp_json else None


def getUserFromID(api, user_id, token=None):
    rsp_json = json_request(api, token, 'people.getInfo',
        "user informations for %s", [user_id], user_id=user_id)
    return rsp_json['person'] if rsp_json else None


def getUserFromUsername(api, user_name):
    rsp_json = json_request(api, None, 'people.findByUsername',
        "user %s from username", [user_name], username=user_name)
    return rsp_json['user'] if rsp_json else None


def searchGroupByUrl(api, token, group_url):
    rsp_json = json_request(api, token, 'urls.lookupGroup',
        " info for group %s from url", [group_url], url=group_url,
        content_type=7)
    return rsp_json['group'] if rsp_json else []


def getPhotoExif(api, token, photo_id):
    rsp_json = json_request(api, token, 'photos.getExif',
        "photo EXIF for %s", [photo_id], photo_id=photo_id)
    return rsp_json['photo']['exif'] if rsp_json else None


def getPhotoSize(api, token, photo_id):
    rsp_json = json_request(api, token, 'photos.getSizes',
        "photo size for %s", [photo_id], photo_id=photo_id)
    return rsp_json['sizes']['size'] if rsp_json else None


def getUserGroups(api, token, user_id, page=1):
    rsp_json = json_request(api, token, 'people.getPublicGroups',
        "user %s groups, page %i", [user_id, page],
        page=page, user_id=user_id, content_type=7, invitation_only=1)
    return rsp_json['groups']['group'] if rsp_json else []


def countGroupPhotos(api, token, group_id):
    rsp_json = json_request(api, token, 'groups.pools.getPhotos',
        "photos from group %s", [group_id], per_page=1, group_id=group_id)
    return rsp_json['photos']['total'] if rsp_json else 0


def getUserPhotosets(api, token, user_id):
    rsp_json = json_request(api, token, 'photosets.getList',
        "photosets for user %s", [user_id], user_id=user_id)
    return rsp_json['photosets']['photoset'] if rsp_json else None


def getContactsLatestPhotos(api, token, page=1):
    rsp_json = json_request(api, token, 'photos.getContactsPhotos',
        'the contacts photos', page=page, count=50)
    return rsp_json['photos']['photo'] if rsp_json else []


def getCollectionPhotosets(api, token, collection_id, user_id):
    rsp_json = json_request(api, token, 'collections.getTree',
        "photosets for user (%s) collection %s", [user_id, collection_id],
        collection_id=collection_id, user_id=user_id, content_type=7)

    if rsp_json:
        return rsp_json['collections']['collection'][0]['set']


def getPhotosetPhotos(api, token, photoset_id, page=1):
    rsp_json = json_request(api, token, 'photosets.getPhotos',
        "photos from %s photoset, page %i", [photoset_id, page],
        page=page, per_page=DEFAULT_PERPAGE, photoset_id=photoset_id,
        content_type=7)
    if not rsp_json: return []

    content = rsp_json['photoset']['photo']
    total = int(rsp_json['photoset']['total'])

    if int(len(content) + (page - 1) * DEFAULT_PERPAGE) != total:
        content.extend(getPhotosetPhotos(api, token, photoset_id, page + 1))

    return content


def getUserLastPhotos(api, token, user_id, since, page=1):
    rsp_json = json_request(api, token, 'photos.recentlyUpdated',
        "last %s's photos page %i", [user_id, page],
        page=page, per_page=DEFAULT_PERPAGE, user_id=user_id, content_type=7,
        min_date=since)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    total = int(rsp_json['photos']['total'])

    if len(content) + (page - 1) * DEFAULT_PERPAGE != total:
        content.extend(getUserLastPhotos(api, token, user_id, since, page + 1))

    return content


def getPhotosByTag(api, token, user_id, tags, page=1):
    rsp_json = json_request(api, token, 'photos.search', "searched photos",
        user_id=user_id, tags=tags, content_type=7, page=page)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    total = int(rsp_json['photos']['total'])

    if len(content) + (page - 1) * DEFAULT_PERPAGE != total:
        content.extend(getPhotosByTag(api, token, user_id, tags, page + 1))

    return content


def searchPhotos(api, token, user_id, search, page=1):
    rsp_json = json_request(api, token, 'photos.search', "searched photos",
        user_id=user_id, text=search, content_type=7, page=page)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    total = int(rsp_json['photos']['total'])

    if len(content) + (page - 1) * DEFAULT_PERPAGE != total:
        content.extend(searchPhotos(api, token, user_id, search, page + 1))

    return content


def getContactList(api, token, page=1):
    rsp_json = json_request(api, token, 'contacts.getList',
        'the contact list',
        page=page, sort='time')
    if not (rsp_json and rsp_json.get('contacts')): return []

    content = rsp_json['contacts'].get('contact')
    total = int(rsp_json['contacts']['total'])

    if not content: return []

    if len(content) + (page - 1) * DEFAULT_PERPAGE != total:
        content.extend(getContactList(api, token, page + 1))

    return content


def getUserFavorites(api, token, user_id, page=1, one_shot=False,
        per_page=DEFAULT_PERPAGE, min_fave_date=None):
    rsp_json = json_request(api, token, 'favorites.getList',
        '%s favorites', [user_id],
        user_id=user_id, page=page, content_type=7, per_page=per_page,
        min_fave_date=min_fave_date)
    if not rsp_json: return []

    content = rsp_json['photos']['photo']
    total = int(rsp_json['photos']['total'])

    if not one_shot:
        while len(content) < total:
            if len(content) < total - per_page:
                page += 1
                content.extend(getUserFavorites(api, token,
                    user_id, page, min_fave_date=min_fave_date, one_shot=True))
            else:
                break

    return content


def getGroupPhotosFromScratch(api, token, group_id, batch=0, page_in_batch=100,
        per_page=500):
    Logger().info("getGroupPhotosFromScratch %s %s" % (group_id, batch))

    content = []
    for spage in range(1, page_in_batch + 1):
        page = spage + batch * page_in_batch
        rsp_json = json_request(api, token, 'groups.pools.getPhotos',
            "photos from group %s, page %i", [group_id, page],
            page=page, per_page=per_page, group_id=group_id, content_type=7)

        if not rsp_json: break

        content.extend(rsp_json['photos']['photo'])

        if page * per_page > int(rsp_json['photos']['total']): break

    return content


def groupFromScratch(api, token, group_id):
    rsp_json = json_request(api, token, 'groups.pools.getPhotos',
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
        content = getGroupPhotosFromScratch(api, token, group_id,
            batch, page_in_batch, per_page)

        file_dump(_get_path(batch), content)


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

    rsp_json = json_request(api, token, 'groups.pools.getPhotos',
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

    rsp_json = json_request(api, token, 'people.getPhotos',
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


def getUserFromUrl(api, url, from_nick=False):
    rsp_json = json_request(api, None, 'urls.lookupUser',
        "lookup for user url %s", [url], url=url)
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
            f = re.split('\.', filename)
            if index == 1:
                f.insert(len(f) - 1, str(index))
            else:
                f[len(f) - 2] = str(index)

            filename = '.'.join(f)
            possible_files.append(filename)

        possible_files.pop()

    FileWrite().write(filename, content, existing)

    if info:
        try:
            exif.fillFile(None, None, filename, info=info)
        except Exception, e:
            Logger().warn("Failed to put exif")
            Logger().warn(e)

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
            except Exception, e:
                Logger().error(e)

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
            except Exception, e:
                Logger().error(e)

    return len(content)


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
        return
    return ret


def _mkdir_photoset(destination, retrieve):
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
            _mkdir_photoset(destination, opt.retrieve)
        except OSError, e:
            errors = {
                28: "there is not enough space to continue, " \
                    "please delete some files and try again",
                13: "you dont have the permissions to access %s" % \
                    destination,
            }
            if e.errno in errors:
                if waitFor(errors[e.errno]):
                    _mkdir_photoset(destination, opt.retrieve)
                else:
                    raise
            else:
                Logger().error("while doing stuffs in %s" % destination)
                info = sys.exc_info()
                Logger().error(str(e))
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
