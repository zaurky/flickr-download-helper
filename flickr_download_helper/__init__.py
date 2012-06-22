#!/usr/bin/python

"""
flickr_download_helper.py

This small program was developed to help retrieve full bunch of photos from flickr.

To have the description of the parameters, please read flickr_download_helper.config or start the program with the --help flag
"""

import sys
import os
import re
import time
# getPhotosetPhotos, getPhotoSize, getCollectionInfo, getAllPreviousUsers, downloadPhotoFromID
from flickr_download_helper.api import getPhotoInfo, getUserPhotos, getUserGroups
from flickr_download_helper.api import getPhotoURLFlickr, getPhotosetInfos, getUserFromID, getUserPhotosets, getGroupPhotos
from flickr_download_helper.api import getUserFromUsername, getUserFromUrl, getUserFromNick, readFile, downloadPhotoFromURL, getPhotosByTag
from flickr_download_helper.api import backupUser, restoreUser, initialisationFlickrApi
from flickr_download_helper.api import getPhotoset, getCollectionPhotosets, \
    getContactsPhotos, searchGroup, getUser
from flickr_download_helper.url_parser import UrlParser
from flickr_download_helper.types import FDHPR
from flickr_download_helper.utils import extends
from flickr_download_helper.config import OptReader, OPT, OptConfigReader, INS
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.existing import Existing #, FileWrite
from flickr_download_helper.existing import file_load, file_dump
from flickr_download_helper.logger import Logger
from flickr_download_helper.downloads_file import DownloadFile
import datetime
from datetime import date
import simplejson as json
# from flickr_download_helper.database import SaveAll

def main_init(read_command_line = True):
    config = OptConfigReader()
    config.setup()

    if read_command_line:
        opt = OptReader()
        ret = opt.read()
        if ret != 0: return ret

    Logger().setup()

    Logger().warn("####################################################################")
    Logger().warn("%s (running as %s)"%(" ".join(sys.argv), os.getpid()))
    if 'LANG' in os.environ:
        Logger().debug(os.environ['LANG'])

    proxy = FDHProxySettings()
    proxy.setValues(OPT)
    proxy.activate()

    # init of the log all database
#    logall_db = SaveAll()
#    logall_db.init()

    # init of the flickr api
    r = initialisationFlickrApi(OPT)
    if not isinstance(r, (list, tuple)) or len(r) != 2:
        if r != 6:
            Logger().error("Couldn't init flickr api")
            Logger().error(r)
        raise Exception("Couldn't init flickr api %s"%(str(r)))
    api, token = r
    return (api, token)

def main(api, token):
    photo_id2destination = {}
    user_name = None
    infos = {}
    existing = None

    if not os.path.exists(OPT.photo_dir) and OPT.retrieve:
        Logger().error("You want to download the photos, but the destination directory don't exists. Please create %s"%OPT.photo_dir)
        return (-9, 0)

    # create an id for the news_in_dir
    if OPT.new_in_dir:
        OPT.new_in_dir = os.path.join(OPT.news_dir, time.strftime("%Y%m%d%H", time.localtime()))
        if not os.path.exists(OPT.new_in_dir):
            os.mkdir(OPT.new_in_dir)
    if OPT.daily_in_dir:
        OPT.daily_in_dir = os.path.join(OPT.news_dir, "daily", time.strftime("%Y%m%d", time.localtime()))
        if not os.path.exists(OPT.daily_in_dir):
            os.mkdir(OPT.daily_in_dir)

    if OPT.get_url:
        Logger().info("\n== retrieve from URL")
        url = UrlParser(OPT.get_url).parse()

        if '@' in url[1]:
            OPT.user_id = url[1]
        else:
            OPT.url = url[1]

        if url[0] == FDHPR.USER:
            pass
        elif url[0] == FDHPR.TAG:
            OPT.tags = (url[2])
            OPT.username = OPT.url
            OPT.url = None
        elif url[0] == FDHPR.SET:
            OPT.photoset_id = url[2]
        elif url[0] == FDHPR.COLLECTION:
            OPT.collection_id = url[2]
        elif url[0] == FDHPR.PHOTO:
            OPT.url = None
            OPT.user_id = None
            OPT.photo_ids = (url[1])
        elif url[0] == FDHPR.PROFILE:
            OPT.url = None
            OPT.user_id = None
            Logger().warn("I don't know what to do with that! %s"%(OPT.get_url))
        elif url[0] == FDHPR.PHOTOSETS:
            OPT.sort_by_photoset = True
        elif url[0] == FDHPR.GROUP:
            Logger().error("Don't know how to get group")
        elif url[0] == FDHPR.INGROUP:
            group = searchGroup(api, token, url[2])
            OPT.group_id = group['id']
        elif url[0] in (FDHPR.ERROR, FDHPR.ERROR_NOURL, FDHPR.ERROR_NOTFLICKR):
            OPT.url = None
            OPT.user_id = None
            Logger().error("error parsing OPT.get_url : %s"%(url[0]))

#    if OPT.scan_groups:
#        INS['put_group_in_session'] = True

    if OPT.photo_id_in_file:
        # work on a list of photos ids
        content = readFile(OPT.photo_id_in_file)
        content = content.split("\n")
        while '' in content: content.remove('')
        # user_id NOT
        # content = Existing().grepDontExists(content)
        OPT.photo_ids = content

    if OPT.photoset_id:
        # work on a photoset
        photoset = getPhotosetInfos(api, token, OPT.photoset_id)
        photoset_name = photoset['title']

        Logger().info("\n== get user information")
        user_id = photoset['owner']
        user = getUserFromID(api, user_id)
        user_name = user['username']
        Logger().warn("username = %s"%user_name)

        existing = Existing(user_id, user_name)

        urls, photo_id2destination, destination, infos = getPhotoset(OPT, api, token, user_name, OPT.photoset_id, photoset_name, user_id, existing)

    elif OPT.photo_ids:
        Logger().info("\n== retrieve photos informations")
        photos = []
        photo_id2username = {}
        for photo_id in OPT.photo_ids:
            try:
                photo = getPhotoInfo(api, token, photo_id)
            except:
                # try again then continue
                try:
                    Logger().info("second try to get photo %s infos"%(photo_id))
                    photo = getPhotoInfo(api, token, photo_id)
                except Exception, e:
                    Logger().warn("can't get photo %s (%s)"%(photo_id, str(e)))
            if photo == None:
                Logger().warn("can't get photo %s"%photo_id)
                continue
            username = photo['owner']['username']
            photo_id2username[photo_id] = username
            photos.append(photo)
            infos[photo['id']] = photo

        Logger().info("\n== prepare the photo directory")
        if OPT.sort_by_user:
            for photo_id in photo_id2username:
                user_name = photo_id2username[photo_id]
                if re.search("/", user_name):
                    user_name = user_name.replace("/", "##")
                destination = os.path.join(OPT.photo_dir, user_name)
                photo_id2destination[photo_id] = destination
                if OPT.retrieve and not os.path.exists(destination): os.mkdir(destination)

        Logger().info("\n== get all photos url")
        urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
    else:
        # we work with user_id, so whatever is the input, now we want user_id
        user = getUser(api, token)
        if user is None:
            return (3, 0)

        if not user:
            Logger().error("can't find user")
            return (4, 0)

        OPT.user_id = user['id']
        OPT.user_hash[OPT.user_id] = user

        # getting user's informations
        Logger().info("\n== get user information")
        user_name = user['username']
        user_id = user['id']
        Logger().warn("username = %s"%user_name)

        if not OPT.scan_groups:
            existing = Existing(user_id, user_name)

        if OPT.collection_id:
            Logger().info("\n== getting collection %s"%OPT.collection_id)
            OPT.sort_by_user = True
            photosets = getCollectionPhotosets(api, token, OPT.collection_id, user_id)
            urls = {}
            photo_id2destination = {}
            destination = ""
            for photoset in photosets:
                Logger().info("\n== getting photoset %s"%photoset['title'])
                l_urls, l_photo_id2destination, destination, infos = getPhotoset(OPT, api, token, user_name, photoset['id'], photoset['title'], user_id, existing)
                urls = extends(urls, l_urls)
                photo_id2destination = extends(photo_id2destination, l_photo_id2destination)
        elif OPT.sort_by_photoset:
            Logger().info("\n== getting user (%s) photoset"%user_id)
            OPT.sort_by_user = True
            photosets = getUserPhotosets(api, token, user_id)
            urls = {}
            photo_id2destination = {}
            destination = ""
            for photoset in photosets:
                Logger().info("\n== getting photoset %s"%photoset['title'])
                l_urls, l_photo_id2destination, destination, l_infos = getPhotoset(OPT, api, token, user_name, photoset['id'], photoset['title'], user_id, existing)
                urls = extends(urls, l_urls)
                photo_id2destination = extends(photo_id2destination, l_photo_id2destination)
                infos = extends(infos, l_infos)
        elif OPT.try_from_groups or OPT.scan_groups:
            if OPT.group_id:
                groups = [{'name':OPT.group_id, 'nsid':OPT.group_id}]
            else:
                if OPT.try_from_groups:
                    Logger().info("\n== trying to get users (%s) photos from groups"%user_id)
                    groups = getUserGroups(api, token, user_id, page = 1)
                elif OPT.scan_groups:
                    Logger().info("\n== trying to get users (%s) photos from %s groups"%(user_id, OPT.my_id))
                    if isinstance(OPT.scan_groups, bool):
                        OPT.scan_groups = {'IAMADICT':True}

                    if isinstance(OPT.scan_groups, dict) and 'groups' in OPT.scan_groups:
                        groups = OPT.scan_groups['groups']
                    else:
                        groups = getUserGroups(api, token, OPT.my_id, page = 1)
                        OPT.scan_groups['groups'] = groups
            photos = []
            index = 0
            for group in groups[0:500]:
                Logger().info("\n== getting group %s (%s) [%s/%s]"%(group['name'], group['nsid'], index, len(groups)))
                if OPT.scan_groups:
                    l_photos = getGroupPhotos(api, token, group['nsid'], per_page=500)
                    count = 0
                    for l_photo in l_photos:
                        if l_photo['owner'] == user_id:
                            count += 1
                            photos.append(l_photo)
                    if count != 0:
                        Logger().debug("got %i photos in group %s"%(count, group['nsid']))
                elif OPT.force_group_verbose:
                    l_photos = getGroupPhotos(api, token, group['nsid'], user_id = user_id, per_page=500)
                    count = 0
                    for l_photo in l_photos:
                        if l_photo['owner'] == user_id:
                            count += 1
                            photos.append(l_photo)
                    if count != 0:
                        Logger().debug("got %i photos in group %s"%(count, group['nsid']))
                else:
                    l_photos = getGroupPhotos(api, token, group['nsid'], user_id = user_id, per_page=500)
                    if len(l_photos) != 0:
                        Logger().debug("got %i photos in group %s"%(len(l_photos), group['nsid']))
                    photos.extend(l_photos)
                index += 1
            total = len(photos)
            # user_id ok
            if OPT.scan_groups and len(photos) > 0:
                existing = Existing(user_id, user_name)

            if len(photos) > 0:
                photos = existing.grepPhotosDontExists(photos)

            total_after_filter = len(photos)
            if total != total_after_filter:
                Logger().info("filter %d photos" % (total - total_after_filter))
            for photo in photos: infos[photo['id']] = photo
            urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
            if '/' in user_name: user_name = user_name.replace("/", "##")
            destination = os.path.join(OPT.photo_dir, user_name)
            try:
                if OPT.retrieve and not os.path.exists(destination): os.mkdir(destination)
            except Exception, e:
                Logger().warn(destination)
                raise e
        elif OPT.tags or OPT.group_id:
            if OPT.tags:
                Logger().info("\n== getting photos in tag %s"%OPT.tags)
                photos = getPhotosByTag(api, token, user_id, OPT.tags)
            else:
                Logger().info("\n== getting user %s files in group %s"%(user_name, OPT.group_id))
                photos = getGroupPhotos(api, token, OPT.group_id, user_id = user_id, per_page=500)
            total = len(photos)
            # user_id ok
            existing = Existing(user_id, user_name)
            photos = existing.grepPhotosDontExists(photos)
            total_after_filter = len(photos)
            if total != total_after_filter:
                Logger().info("filter %d photos" % (total - total_after_filter))
            for photo in photos: infos[photo['id']] = photo
            urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
            destination = os.path.join(OPT.photo_dir, user_name)
            if OPT.retrieve and not os.path.exists(destination): os.mkdir(destination)
            if OPT.tags:
                destination = os.path.join(destination, OPT.tags)
                if OPT.retrieve and not os.path.exists(destination): os.mkdir(destination)
        else:
            # prepare the photo directory
            Logger().info("\n== prepare the photo directory")
            if re.search("/", user_name):
                user_name = user_name.replace("/", "##")
            destination = os.path.join(OPT.photo_dir, user_name)
            try:
                Logger().debug('look if %s exists, else create it'%destination)
                if OPT.retrieve and not os.path.exists(destination): os.mkdir(destination)
            except OSError, e:
                Logger().error("%s: %s (%s)"%(e.errno, e.filename, e.strerror))
                raise e
            except UnicodeEncodeError, e:
                Logger().error(e)
                Logger().error(str(e))
                Logger().error(dir(e))
                Logger().error(e.message)
                #Logger().print_tb(e)
                raise e
            except Exception, e:
                Logger().error(str(e))
                Logger().error(dir(e))
                Logger().print_tb(e)
                raise e

            # getting the file's URL
            if OPT.restore_photo_url:
                Logger().info("\n== get the files'URL from a backup file")
                urls = restoreUser(user_id, OPT.backup_dir)
                if not urls:
                    Logger().error("couldn't restore the backup for that user %s"%(user_id))
                    return (5, 0)
            else:
                Logger().info("\n== get the files'URL from flick API")
                if OPT.since:
                    photos = getUserPhotos(api, token, user_id, OPT.since)
                else:
                    photos = getUserPhotos(api, token, user_id)
                total = len(photos)
                # user_id ok
                photos = existing.grepPhotosDontExists(photos)
                total_after_filter = len(photos)
                if total != total_after_filter:
                    Logger().info("filter %d photos" % (total - total_after_filter))
                if len(infos) == 0:
                    for photo in photos: infos[photo['id']] = photo
                urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)

                # backuping what we are going to get
                Logger().info("\n== backup user's photo information")
                backupUser(user_id, urls, OPT.backup_dir)

                if OPT.only_backup_photo_url:
                    Logger().info("\n== end")
                    return (0, len(urls))

    # retrieving files
    Logger().info("\n== retrieve files")
    total_size = 0
    total = 0
    count_url = len(urls.keys())
    Logger().info("sort_by_user %s"%str(OPT.sort_by_user))
    for id, url in urls.items():
        if OPT.retrieve:
            if OPT.sort_by_user:
                destination = photo_id2destination[id]
            filename = os.path.join(destination, os.path.basename(url))
            info = None
            if len(infos) != 0 and id in infos:
                info = infos[id]
            if os.path.exists(filename) and not OPT.force:
                if OPT.user_id and OPT.user_id in OPT.check_md5:
                    # TODO check the md5 or the size for users in OPT.check_md5:
                    Logger().info("%s> check %s"% (id, filename))
                    size = downloadPhotoFromURL(url, filename, existing, True, info = info)
                    if size == 0:
                        Logger().info("%s> is the same"%(id))
                        count_url -= 1
                    else:
                        Logger().info("%s> got a new one"%(id))
                        total_size += size
                        total += 1
                        Logger().info("%i/%i %s : %i"%(total, count_url, id, size))
                        time.sleep(OPT.sleep_time)
                else:
                    Logger().info("%s> already exists (%s)" % (id, filename))
                    count_url -= 1
            else:
                size = downloadPhotoFromURL(url, filename, existing, info = info)
                total_size += size
                total += 1
                Logger().info("%i/%i %s : %i"%(total, count_url, id, size))
                time.sleep(OPT.sleep_time)
        else:
            Logger().info("%s> %s" % (id, url))
    if not OPT.sort_by_user: Logger().info(destination)
    if OPT.retrieve:
        if total == 0:
            Logger().info("download %i file for %i octets"%(total, total_size))
        else:
            if hasattr(OPT, 'has_been_download') and user_name != None:
                OPT.has_been_download[user_name] = [total, total_size]
            Logger().warn("download %i file for %i octets"%(total, total_size))
            DownloadFile().write("%s %s %s"%(str(datetime.datetime.now()), total, user_name))

    if existing and len(urls) > 0:
        # we only save photo cache when something has been downloaded
        existing.backupToFile()
    Logger().info("\n== end")
    return (0, total)

def getRecentlyUploadedContacts(api, token):
    owners = []
    photos = getContactsPhotos(api, token)
    for photo in photos:
        if photo['owner'] not in owners:
            owners.append(photo['owner'])
    return owners

