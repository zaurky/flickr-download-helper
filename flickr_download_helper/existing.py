from flickr_download_helper.config import OPT, Singleton
from flickr_download_helper.utils import waitFor
import pickle
import shutil
import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


class FileWrite(Singleton):
#    existing = None
#    def init(self):
#        self.existing = Existing()

    def write(self, filename, content, existing = None):
        try:
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname): mkdir_p(dirname)
            f = open(filename, 'wb')
            f.write(content)
            f.close()
            if existing != None:
                existing.addFile(filename)
        except OSError, e:
            if e.errno == 28:
                ret = waitFor("there is not enough space to continue, please delete some files and try again")
                if ret:
                    f = open(filename, 'wb')
                    f.write(content)
                    f.close()
                else:
                    raise e
            else:
                raise e


class Existing():
    internals = {'ids':None}
    my_file = None
    user_id = None
    photo_dir = None

    def __init__(self, user_id, sub_photo_dir):
        self.user_id = user_id
        self.photo_dir = os.path.join(OPT.photo_dir, sub_photo_dir)
        if os.path.exists(OPT.existing_ids_file) and os.path.isdir(OPT.existing_ids_file):
            self.my_file = os.path.join(OPT.existing_ids_file, user_id)
        if not self.restoreFromFile():
            self.internals['ids'] = self.getIdsFromDir(self.photo_dir)

    def backupToFile(self):
        if not self.my_file: return -1
        if os.path.exists(self.my_file):
            shutil.move(self.my_file, "%s.bkp"%(self.my_file))
        f = open(self.my_file, 'wb')
        pickle.dump(self.internals, f)
        f.close()

    def restoreFromFile(self):
        if os.path.exists(self.my_file):
            try:
                f = open(self.my_file, 'rb')
                self.internals = pickle.load(f)
                f.close()
            except:
                self.internals = {'ids':None}
                # todo change!
                self.internals['ids'] = self.getIdsFromDir(self.photo_dir)
        else:
            return False
        return True

    def addFile(self, filename):
        basename = os.path.basename(filename).split('_')
        id = basename[0]
        self.internals['ids'].append(id)

    def readDir(self, directory):
        ret = []
        for root, dirs, files in os.walk(directory):
            ret.extend(files)
        return ret

    def getIdsFromDir(self, directory):
        ret = []
        files = self.readDir(directory)
        for file in files:
            f = file.split("_")
            id = f[0]
            ret.append(id)
        return ret

    def exists(self, id):
        if self.internals['ids'] == None:
            # todo change
            self.internals['ids'] = self.getIdsFromDir(self.photo_dir)

        return (id in self.internals['ids'])

    def grepDontExists(self, ids):
        ret = []
        for id in ids:
            if not self.exists(id): ret.append(id)
        return ret

    def grepPhotosDontExists(self, photos):
        ret = []
        for photo in photos:
            if not self.exists(photo['id']): ret.append(photo)
        return ret

    def grepExists(self, ids):
        ret = []
        for id in ids:
            if self.exists(id): ret.append(id)
        return ret

    def grepPhotosExists(self, photos):
        ret = []
        for photo in photos:
            if self.exists(photo['id']): ret.append(photo)
        return ret


