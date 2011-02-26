#!/usr/bin/python

from flickr_download_helper.api import getPhotoInfo
from flickr_download_helper.logger import Logger
import pyexiv2
import os

def fillDir(api, token, args, dirname, names):
    total_count = len(names)
    count = 1
    for name in names:
        filename = os.path.join(dirname, name)
        if os.path.isdir(filename):
            os.path.walk(filename, fillDir, [api, token])
        elif os.path.isfile(filename):
            pass
            #fillFile(api, token, filename, count, total_count)
        count += 1

def writeMetadata(metadata, key, val):
    metadata[key] = pyexiv2.ExifTag(key, val)
    return metadata

def contains(metadata, key):
    try: metadata[key]
    except KeyError: return None
    return metadata[key]

def getGeneralInfo(filename):
    ret = {}
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    artist = contains(metadata, 'Exif.Image.Artist')
    if artist != None:
        ret['Exif.Image.Artist'] = artist.value
    comment = contains(metadata, 'Exif.Photo.UserComment')
    if comment != None:
        ret['Exif.Photo.UserComment'] = comment.value
    return ret

def putGeneralInfo(api, token, photo_id, metadata, info = None):
    owner = contains(metadata, 'Exif.Image.Artist')
    comment = contains(metadata, 'Exif.Photo.UserComment')
    if owner != None and comment != None:
        Logger().debug("%s already have a owner and a comment"%(photo_id))
        return metadata

    if info == None:
        info = getPhotoInfo(api, token, photo_id)

    if info == None:
        Logger().warn("Couldn't get info for photo %s"%(photo_id))
        return metadata

    if 'owner' in info and metadata and owner == None:
        if 'username' in info['owner'] and 'realname' in info['owner']:
            metadata = writeMetadata(metadata, 'Exif.Image.Artist', "%s (%s)"%(info['owner']['username'], info['owner']['realname']))
        elif 'username' in info['owner']:
            metadata = writeMetadata(metadata, 'Exif.Image.Artist', "%s"%(info['owner']['username']))
        elif 'realname' in info['owner']:
            metadata = writeMetadata(metadata, 'Exif.Image.Artist', "(%s)"%(info['owner']['realname']))

    a_userComment = []
    if 'title' in info and info['title'] != '':
        a_userComment.append('<title>%s</title>'%(info['title']))

    if 'description' in info and info['description'] != '':
        a_userComment.append('<description>%s</description>'%(info['description']))

    if 'tags' in info and len(info['tags']['tag']) != 0:
        a_userComment.append('<tags>%s</tags>'%(', '.join(info['tags']['tag'])))

    if len(a_userComment) != 0 and comment == None:
        metadata = writeMetadata(metadata, 'Exif.Photo.UserComment', '<xml>%s</xml>'%('\n'.join(a_userComment)))

    return metadata

def fillFile(api, token, file_path, count = None, total_count = None, info = None):
    filename = os.path.basename(file_path)
    tmp = filename.split('_')
    photoid = tmp[0]
    if count == None:
        Logger().debug("filling photo %s"%(photoid))
    else:
        Logger().debug("filling photo %s (%i/%i)"%(photoid, count, total_count))

    try:
        metadata = pyexiv2.ImageMetadata(file_path)
        metadata.read()

        metadata = putGeneralInfo(api, token, photoid, metadata, info)

        metadata.write()
    except IOError:
        Logger().warn("Can't read file %s"%(file_path))
    except  Exception, e:
        Logger().print_tb(e)
        Logger().error(e)
        Logger().warn("Can't fill photo %s"%(photoid))


