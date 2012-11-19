#!/usr/bin/python

"""
flickr_download_helper.py

This small program was developed to help retrieve full bunch of photos from flickr.

To have the description of the parameters, please read flickr_download_helper.config or start the program with the --help flag
"""

import sys
import os
import time
from datetime import datetime

from flickr_download_helper.api import *
from flickr_download_helper.flickr import API as Flickr
from flickr_download_helper.url_parser import UrlParser
from flickr_download_helper.types import FDHPR
from flickr_download_helper.utils import extends, mkdir
from flickr_download_helper.config import OptReader, OPT, OptConfigReader, INS
from flickr_download_helper.proxy import FDHProxySettings
from flickr_download_helper.existing import Existing, file_load, file_dump
from flickr_download_helper.logger import Logger
from flickr_download_helper.downloads_file import DownloadFile


def main_init(read_command_line=True):
    api = Flickr(read_command_line)
    return (api.api, api.token)


def filter_photos(user_id, user_name, photos, existing=None):
    if not photos:
        return existing, photos, {}

    total = len(photos)
    # user_id ok
    if not existing:
        existing = Existing(user_id, user_name)

    if photos:
        photos = existing.grepPhotosDontExists(photos)

    diff = total - len(photos)
    if diff:
        Logger().info("filter %d photos" % (diff))

    infos = {}
    for photo in photos:
        infos[photo['id']] = photo

    return (existing, photos, infos)


def create_dir_env(user_name):
    # prepare the photo directory
    Logger().info("\n== prepare the photo directory")

    user_name = user_name.replace("/", "##")
    destination = os.path.join(OPT.photo_dir, user_name)

    try:
        Logger().debug('look if %s exists, else create it' % destination)
        mkdir(destination)
    except OSError, err:
        Logger().error("%s: %s (%s)" % (err.errno, err.filename, err.strerror))
        raise
    except UnicodeEncodeError, err:
        Logger().error(str(err))
        Logger().error(err.message)
        raise
    except Exception, err:
        Logger().error(str(err))
        Logger().print_tb(err)
        raise

    return (user_name, destination)


def get_photosets_photos(api, token, user_id, user_name, photosets, existing):
    urls = {}
    infos = {}
    photo_id2destination = {}
    destination = ""

    for photoset in photosets:
        Logger().info("\n== getting photoset %s" % photoset['title'])
        l_urls, l_photo_id2destination, destination, l_infos = getPhotoset(
            OPT, api, token, user_name, photoset['id'],
            photoset['title'], user_id, existing)

        urls = extends(urls, l_urls)
        photo_id2destination = extends(photo_id2destination, l_photo_id2destination)
        infos = extends(infos, l_infos)

    return (urls, photo_id2destination, infos)


def main(api, token):
    user_name = None
    existing = None
    photo_id2destination = {}
    infos = {}

    if not os.path.exists(OPT.photo_dir) and OPT.retrieve:
        Logger().error("You want to download the photos, " \
            "but the destination directory don't exists. " \
            "Please create %s" % OPT.photo_dir)
        return (-9, 0)

    # create an id for the news_in_dir
    if OPT.new_in_dir:
        OPT.new_in_dir = os.path.join(OPT.news_dir,
            time.strftime("%Y%m%d%H", time.localtime()))
        mkdir(OPT.new_in_dir)

    if OPT.daily_in_dir:
        OPT.daily_in_dir = os.path.join(OPT.news_dir, "daily",
            time.strftime("%Y%m%d", time.localtime()))
        mkdir(OPT.daily_in_dir)

    if OPT.get_url:
        UrlParser(OPT.get_url).fill_opt(api, token)

    if OPT.photo_id_in_file:
        # work on a list of photos ids
        OPT.photo_ids = filter(lambda line: line != '',
            readFile(OPT.photo_id_in_file).split("\n"))

    if OPT.photoset_id:
        # work on a photoset
        photoset = getPhotosetInfos(api, token, OPT.photoset_id)
        photoset_name = photoset['title']

        Logger().info("\n== get user information")
        user_id = photoset['owner']

        user = getUserFromID(api, user_id)
        user_name = user['username']

        Logger().warn("username = %s" % user_name)

        existing = Existing(user_id, user_name)

        urls, photo_id2destination, destination, infos = getPhotoset(
            OPT, api, token, user_name, OPT.photoset_id, photoset_name,
            user_id, existing)

    elif OPT.photo_ids:
        Logger().info("\n== retrieve photos informations")
        photos = []
        photo_id2username = {}

        for photo_id in OPT.photo_ids:
            photo = getPhotoInfo(api, token, photo_id)

            if not photo:
                Logger().warn("can't get photo %s" % photo_id)
                continue

            photo_id2username[photo_id] = photo['owner']['username']
            photos.append(photo)
            infos[photo['id']] = photo

        Logger().info("\n== prepare the photo directory")

        if OPT.sort_by_user:
            for photo_id in photo_id2username:
                user_name = photo_id2username[photo_id]
                destination = create_dir_env(user_name)
                photo_id2destination[photo_id] = destination

        Logger().info("\n== get all photos url")
        urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)

    else:
        # we work with user_id, so whatever is the input, now we want user_id
        user = getUser(api, token)
        if not user:
            Logger().error("can't find user")
            return (4, 0)

        OPT.user_id = user['id']
        OPT.user_hash[OPT.user_id] = user

        # getting user's informations
        Logger().info("\n== get user information")

        user_name = user['username']
        user_id = user['id']

        Logger().warn("username = %s" % user_name)

        if not OPT.scan_groups:
            existing = Existing(user_id, user_name)

        if OPT.collection_id:
            Logger().info("\n== getting collection %s" % OPT.collection_id)

            OPT.sort_by_user = True
            photosets = getCollectionPhotosets(api, token, OPT.collection_id, user_id)

            urls, photo_id2destination, infos = get_photosets_photos(
                api, token, user_id, user_name, photosets, existing)

        elif OPT.sort_by_photoset:
            Logger().info("\n== getting user (%s) photoset" % user_id)

            OPT.sort_by_user = True
            photosets = getUserPhotosets(api, token, user_id)

            urls, photo_id2destination, infos = get_photosets_photos(
                api, token, user_id, user_name, photosets, existing)

        elif OPT.try_from_groups or OPT.scan_groups:
            if OPT.group_id:
                groups = [{'name': OPT.group_id, 'nsid': OPT.group_id}]
            else:
                if OPT.try_from_groups:
                    Logger().info("\n== trying to get users (%s) photos " \
                        "from groups" % user_id)

                    groups = getUserGroups(api, token, user_id, page = 1)
                elif OPT.scan_groups:
                    Logger().info("\n== trying to get users (%s) photos " \
                        "from %s groups" % (user_id, OPT.my_id))

                    if isinstance(OPT.scan_groups, bool):
                        OPT.scan_groups = {'IAMADICT': True}

                    if isinstance(OPT.scan_groups, dict) and 'groups' in OPT.scan_groups:
                        groups = OPT.scan_groups['groups']
                    else:
                        groups = getUserGroups(api, token, OPT.my_id, page=1)
                        OPT.scan_groups['groups'] = groups

            photos = []
            for index, group in enumerate(groups[0:750]):
                group_id = group['nsid']

                Logger().info("\n== getting group %s (%s) [%s/%s]" % (
                    group['name'], group_id, index, len(groups)))

                count = 0

                kargs = {'user_id': user_id, 'per_page': 500}

                if OPT.scan_groups:
                    kargs.pop('user_id')

                l_photos = getGroupPhotos(api, token, group_id, **kargs)

                if OPT.scan_groups or OPT.force_group_verbose:
                    for l_photo in l_photos:
                        if l_photo['owner'] == user_id:
                            count += 1
                            photos.append(l_photo)
                else:
                    count = len(l_photos)
                    photos.extend(l_photos)

                if count:
                    Logger().debug("got %i photos in group %s" % (count, group_id))

            existing, photos, infos = filter_photos(
                user_id, user_name, photos, existing)
            urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
            user_name, destination = create_dir_env(user_name)

        elif OPT.tags:
            Logger().info("\n== getting photos in tag %s" % OPT.tags)
            photos = getPhotosByTag(api, token, user_id, OPT.tags)

            existing, photos, infos = filter_photos(
                user_id, user_name, photos, existing)
            urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
            user_name, destination = create_dir_env(user_name)

            destination = os.path.join(destination, OPT.tags)
            mkdir(destination)

        elif OPT.group_id:
            Logger().info("\n== getting user %s files in group %s" % (
                user_name, OPT.group_id))
            photos = getGroupPhotos(
                api, token, OPT.group_id, user_id=user_id, per_page=500)

            existing, photos, infos = filter_photos(
                user_id, user_name, photos, existing)
            urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
            user_name, destination = create_dir_env(user_name)

        elif OPT.search:
            photos = searchPhotos(api, token, user_id, OPT.search)
            existing, photos, infos = filter_photos(
                user_id, user_name, photos, existing)
            urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
            user_name, destination = create_dir_env(user_name)

        else:
            # getting the file's URL
            if OPT.restore_photo_url:
                Logger().info("\n== get the files'URL from a backup file")
                urls = restoreUser(user_id, OPT.backup_dir)
                if not urls:
                    Logger().error("couldn't restore the backup " \
                        "for that user %s" % (user_id))
                    return (5, 0)
            else:
                Logger().info("\n== get the files'URL from flick API")
                if OPT.since:
                    photos = getUserPhotos(api, token, user_id, OPT.since)
                else:
                    photos = getUserPhotos(api, token, user_id)

                existing, photos, infos = filter_photos(
                    user_id, user_name, photos, existing)
                urls = getPhotoURLFlickr(api, token, photos, OPT.fast_photo_url)
                user_name, destination = create_dir_env(user_name)

                # backuping what we are going to get
                Logger().info("\n== backup user's photo information")
                backupUser(user_id, urls, OPT.backup_dir)

                if OPT.only_backup_photo_url:
                    Logger().info("\n== end")
                    return (0, len(urls))

    # retrieving files
    Logger().info("\n== retrieve files")
    total_size = total = 0
    count_url = len(urls)
    Logger().info("sort_by_user %s" % str(OPT.sort_by_user))

    for id, url in urls.items():
        if OPT.retrieve:
            if OPT.sort_by_user:
                destination = photo_id2destination[id]

            filename = os.path.join(destination, os.path.basename(url))
            info = infos.get(id)

            if os.path.exists(filename) and not OPT.force:
                if OPT.user_id and OPT.user_id in OPT.check_md5:
                    # TODO check the md5 or the size for users in OPT.check_md5:
                    Logger().info("%s> check %s" % (id, filename))

                    size = downloadPhotoFromURL(
                        url, filename, existing, True, info=info)

                    if not size:
                        Logger().info("%s> is the same" % (id))
                        count_url -= 1
                    else:
                        Logger().info("%s> got a new one" % (id))
                        total_size += size
                        total += 1

                        Logger().info("%i/%i %s : %i" % (total, count_url, id, size))
                        time.sleep(OPT.sleep_time)
                else:
                    Logger().info("%s> already exists (%s)" % (id, filename))
                    count_url -= 1

            else:
                size = downloadPhotoFromURL(url, filename, existing, info=info)
                total_size += size
                total += 1

                Logger().info("%i/%i %s : %i" % (total, count_url, id, size))
                time.sleep(OPT.sleep_time)

        else:
            Logger().info("%s> %s" % (id, url))

    if not OPT.sort_by_user:
        Logger().info(destination)

    if OPT.retrieve:
        if not total:
            Logger().info("download 0 file for 0 octets")
        else:
            if hasattr(OPT, 'has_been_download') and user_name:
                OPT.has_been_download[user_name] = [total, total_size]

            Logger().warn("download %i file for %i octets" % (total, total_size))
            DownloadFile().write("%s %s %s" % (
                str(datetime.now()), total, user_name))

    if existing and urls:
        # we only save photo cache when something has been downloaded
        existing.backupToFile()

    Logger().info("\n== end")
    return (0, total)


def getRecentlyUploadedContacts(api, token):
    return list(set(map(lambda photo:
        photo['owner'],
        getContactsLatestPhotos(api, token)
    )))
