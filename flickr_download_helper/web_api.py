from flickr_download_helper.backup import GenericBackup
from flickr_download_helper.logger import Logger
import os

class PhotoFlags:
    DELETED = 1
    MARKED = 2
PF = PhotoFlags

class PhotoManager(GenericBackup):
    internal = {}
    def __init__(self, obj):
        self.obj = obj
        self.obj.init()
        self.photos = self.obj.getPhotos()
        if os.path.exists(self.obj.filtering_file):
            self.internal = self.loadBackup(self.obj.filtering_file)

    def getPhotos(self): return self.filter()

    def backup(self):
        self.backupToFile(self.obj.filtering_file, self.internal)

    def removePhoto(self, photo_id):
        self.internal[photo_id] = PF.DELETED
        self.backup()

    def markPhoto(self, photo_id):
        self.internal[photo_id] = PF.MARKED
        self.backup()

    def filter(self):
        ret = []
        for photo in self.photos:
            if photo['id'] in self.internal:
                if self.internal[photo['id']] == PF.DELETED:
                    continue
                photo['state'] = self.internal[photo['id']]
            ret.append(photo)
        return ret
