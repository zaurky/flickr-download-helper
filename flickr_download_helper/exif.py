#!/usr/bin/python

try:
    from flickr_download_helper.api import getPhotoInfo
except:
    pass

from flickr_download_helper.logger import Logger
import pyexiv2
import os
import re

class fillDir(object):
    def __init__(self, api, token):
        self.api = api
        self.token = token

    def fillDir(self, args, dirname, names):
        total_count = len(names)
        count = 1

        for name in names:
            filename = os.path.join(dirname, name)

            if os.path.isdir(filename):
                os.path.walk(filename, self.fillDir, [self.api, self.token])
            elif os.path.isfile(filename):
                fillFile(self.api, self.token, filename, count, total_count)

            count += 1

def encode(string):
    try:
        return string.encode('latin1')
    except:
        return string.encode('utf8')

def writeMetadata(metadata, key, val):
    if isinstance(metadata, dict):
        metadata[key] = pyexiv2.ExifTag(key, val)
    else:
        metadata[key] = val
    return metadata

def contains(metadata, key):
    if isinstance(metadata, dict):
        if key in metadata:
            return metadata[key]
        return None
    else: # is image
        if key in metadata.exifKeys():
            return metadata[key]
        return None

def getMetadata(filename):
    try:
        metadata = pyexiv2.ImageMetadata(filename)
        metadata.read()
        return metadata
    except:
        image = pyexiv2.Image(filename)
        metadata = image.readMetadata()
        return image
    return None

def getGeneralInfo(filename):
    ret = {}
    metadata = getMetadata(filename)

    artist = contains(metadata, 'Exif.Image.Artist')
    if artist:
        ret['Exif.Image.Artist'] = artist.value

    comment = contains(metadata, 'Exif.Photo.UserComment')
    if comment:
        ret['Exif.Photo.UserComment'] = comment.value

    return ret

def putGeneralInfo(api, token, photo_id, metadata, info = None):
    owner = contains(metadata, 'Exif.Image.Artist')
    comment = contains(metadata, 'Exif.Photo.UserComment')
    if owner and comment:
        Logger().debug("%s already have a owner and a comment" % (photo_id))
        return metadata

    if not info:
        info = getPhotoInfo(api, token, photo_id)

    if not info:
        Logger().warn("Couldn't get info for photo %s" % (photo_id))
        return metadata

    if 'owner' in info and metadata and not owner:
        if 'username' in info['owner'] and 'realname' in info['owner']:
            metadata = writeMetadata(metadata, 'Exif.Image.Artist',
                "%s (%s)" % (encode(info['owner']['username']),
                encode(info['owner']['realname'])))
        elif 'username' in info['owner']:
            metadata = writeMetadata(metadata, 'Exif.Image.Artist',
                "%s" % (encode(info['owner']['username'])))
        elif 'realname' in info['owner']:
            metadata = writeMetadata(metadata, 'Exif.Image.Artist',
            "(%s)" % (encode(info['owner']['realname'])))

    a_userComment = []
    if info.get('title'):
        a_userComment.append('<title>%s</title>' % (encode(info['title'])))

    if info.get('description'):
        a_userComment.append('<description>%s</description>' % (encode(info['description'])))

    if len(info.get('tags', {}).get('tag', [])):
        a_userComment.append('<tags>%s</tags>' % (', '.join(map(encode, info['tags']['tag']))))

    if len(a_userComment) and comment:
        metadata = writeMetadata(metadata, 'Exif.Photo.UserComment',
            '<xml>%s</xml>' % ('\n'.join(map(encode, a_userComment))))

    return metadata

def fillFile(api, token, file_path, count=None, total_count=None, info=None):
    filename = os.path.basename(file_path)
    tmp = filename.split('_')
    i = 0
    while not re.match('^\d{10}$', tmp[i]) and i < len(tmp)-1:
        i += 1
    photoid = tmp[i]

    if not count:
        Logger().debug("filling photo %s" % (photoid))
    else:
        Logger().debug("filling photo %s (%i/%i)" % (photoid, count, total_count))

    try:
        metadata = getMetadata(file_path)
        metadata = putGeneralInfo(api, token, photoid, metadata, info)

        if isinstance(metadata, dict):
            metadata.write()
        else:
            metadata.writeMetadata()

    except IOError:
        Logger().warn("Can't read file %s"%(file_path))
    except (AttributeError, TypeError), e:
        Logger().error(e)
    except (UnicodeEncodeError, UnicodeDecodeError), e:
        Logger().error(e.reason)
    except Exception, e:
        Logger().print_tb(e)
        Logger().error(e)
        Logger().warn("Can't fill photo %s"%(photoid))
