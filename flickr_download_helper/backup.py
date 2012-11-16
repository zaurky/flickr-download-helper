from flickr_download_helper.config import Singleton, OPT
from flickr_download_helper.api import (getContactList, getUserFavorites,
    initialisationFlickrApi)
import pickle
import shutil
import time
import os


class GenericBackup(object):

    def backupToFile(self, filename, obj):
        if os.path.exists(filename):
            shutil.move(filename, "%s.bkp" % (filename))

        fhandle = open(filename, 'wb')
        pickle.dump(obj, fhandle)
        fhandle.close()

    def loadBackup(self, filename):
        if not os.path.exists(filename):
            return None

        fhandle = open(filename)
        obj = pickle.load(fhandle)
        fhandle.close()

        return obj


class PhotosBackup(GenericBackup, Singleton):
    """
    self.photos = {
        'user_id': [time.time(), {photo_id : photo, ...}],
        ....
    }
    """
    photos = {}
    filename = None

    def refreshPhotos(self):
        pass

    def fullRefreshPhotos(self):
        pass

    def init(self):
        self.filename = OPT.photos_backup_file


class FavoritesBackup(GenericBackup, Singleton):
    """
    self.favorites = {
        'user_id': [time.time(), [sorted list of photos] ],
        ....
    }
    """
    favorites = {}
    time = 0

    # refresh the list only once per hour
    refresh_time = 3600

    def refreshFavorites(self):
        self.time = time.time()

        # load the list
        h_photos = {}
        contacts = getContactList(self.api, self.token)

        for contact in contacts:
            user_id = contact['nsid']
            min_fave_date = None
            if user_id in self.favorites:
                min_fave_date = self.favorites[user_id][0]
            else:
                self.favorites[user_id] = [self.time, []]

            photos = getUserFavorites(self.api, self.token, user_id,
                min_fave_date=min_fave_date)
            self.favorites[user_id][0] = self.time

            h_photos = {}
            for photo in photos:
                photo['contact'] = contact
                h_photos[photo['dateupload']] = photo

            h_photos_keys = h_photos.keys()
            h_photos_keys.sort()
            for key in h_photos_keys:
                self.favorites[user_id][1].append(h_photos[key])

        # BACKUP FAVORITES
        self.backupToFile(self.filename, [self.time, self.favorites])

    def orderPhoto(self):
        # prepare the list of photos in the order
        self.ordered_photos = []
        h_photos = {}
        for user_id in self.favorites:
            for photo in self.favorites[user_id][1]:
                h_photos[photo['dateupload']] = photo

        h_photos_keys = h_photos.keys()
        h_photos_keys.sort()

        for k in h_photos_keys:
            self.ordered_photos.append(h_photos[k])

    def init(self):
        self.filename = OPT.favorites_file
        self.filtering_file = "%s.filter" % self.filename

        self.api, self.token = initialisationFlickrApi(OPT)

        # RESTORE FAVORITES
        obj = self.loadBackup(self.filename)
        if obj:
            self.time = obj[0]
            self.favorites = obj[1]

        if self.time < time.time() - self.refresh_time:
            self.refreshFavorites()

        self.orderPhoto()

    def getFavorites(self):
        return self.ordered_photos

    def getPhotos(self):
        return self.getFavorites()
