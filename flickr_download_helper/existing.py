from flickr_download_helper.config import OPT, Singleton
from flickr_download_helper.utils import waitFor
from flickr_download_helper.logger import Logger
import pickle
import shutil
import os, errno


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def file_load(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception, exc:
        print exc


def file_dump(path, content):
    if os.path.exists(path):
        shutil.move(path, "%s.bkp" % path)

    with open(path, 'wb') as f:
        pickle.dump(content, f)


class FileWrite(Singleton):
    def write(self, filename, content, existing=None):
        try:
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                mkdir_p(dirname)

            with open(filename, 'wb') as f:
                f.write(content)

            if existing is not None:
                existing.addFile(filename)

        except OSError, exc:
            if exc.errno == 28:
                ret = waitFor("there is not enough space to continue, " \
                    "please delete some files and try again")

                if ret:
                    with open(filename, 'wb') as f:
                        f.write(content)
                else:
                    raise
            else:
                raise


class Existing():
    internals = {
        'ids': None, # a list of all existing ids
        'usernames': [], # a list of all previous names
        'lastupdate': {} # for each id, it's last update
    }
    my_file = None
    user_id = None
    user_name = None
    photo_dir = None
    logger = None

    def __init__(self, user_id, sub_photo_dir):
        self.logger = Logger()
        self.logger.info(">>Existing initialising with %s %s" %
            (user_id, sub_photo_dir))

        self.user_id = user_id
        self.user_name = sub_photo_dir

        if self.user_name not in self.internals['usernames']:
            self.internals['usernames'].append(self.user_name)

        if os.path.exists(OPT.existing_ids_file) \
                and os.path.isdir(OPT.existing_ids_file):
            self.my_file = os.path.join(OPT.existing_ids_file, user_id)

        self.restoreFromFile()

    def isYounger(self, contact_id, last_update):
        if contact_id in self.internals['lastupdate']:
            if self.internals['lastupdate'][contact_id] < last_update:
                self.internals['lastupdate'][contact_id] = last_update
                self.logger.debug("%s is younger" % contact_id)
                return True

            self.logger.debug("%s is older" % contact_id)
            return False

        self.internals['lastupdate'][contact_id] = last_update
        self.logger.debug("%s is younger" % contact_id)
        return True

    def backupToFile(self):
        self.logger.info(">>Existing backupToFile (%s)" % (self.user_id))
        if not self.my_file:
            return -1

        if os.path.exists(self.my_file):
            shutil.move(self.my_file, "%s.bkp" % (self.my_file))

        with open(self.my_file, 'wb') as f:
            pickle.dump(self.internals, f)

    def restoreFromFile(self):
        self.logger.info(">>Existing restoreFromFile (%s)" % (self.user_id))
        if os.path.exists(self.my_file):
            try:
                with open(self.my_file, 'rb') as f:
                    self.internals = pickle.load(f)
            except:
                self.internals = {'ids': None}
                # todo change!
                self.internals['ids'] = self.getIdsFromDir()
        else:
            self.internals['ids'] = self.getIdsFromDir()

        if 'usernames' not in self.internals:
            self.internals['usernames'] = []

        if self.user_name not in self.internals['usernames']:
            self.internals['usernames'].append(self.user_name)

        if 'lastupdate' not in self.internals:
            self.internals['lastupdate'] = {}

        return True

    def forceReload(self):
        self.logger.debug(">>Existing forceReload (%s)" % (self.user_id))
        self.internals['ids'] = self.getIdsFromDir()
        return True

    def addFile(self, filename):
        self.logger.debug(">>Existing addFile %s (%s)" %
            (filename, self.user_id))

        basename = os.path.basename(filename).split('_')
        self.internals['ids'].append(basename[0])

    def readDir(self, directory):
        ret = []
        for _, _, files in os.walk(directory):
            ret.extend(files)
        return ret

    def getIdsFromDir(self):
        ret = []
        for user_name in self.internals['usernames']:
            directory = os.path.join(OPT.photo_dir, user_name)
            files = self.readDir(directory)
            for filename in files:
                f = filename.split("_")
                ret.append(f[0])
        return ret

    def exists(self, photo_id):
        if not self.internals['ids']:
            # todo change
            self.internals['ids'] = self.getIdsFromDir()

        return photo_id in self.internals['ids']

    def grepDontExists(self, ids):
        return [photo_id for photo_id in ids if not self.exists(photo_id)]

    def grepPhotosDontExists(self, photos):
        if self.user_id in OPT.check_md5:
            return photos

        return [photo for photo in photos if not self.exists(photo['id'])]

    def grepExists(self, ids):
        return [photo_id for photo_id in ids if self.exists(photo_id)]

    def grepPhotosExists(self, photos):
        return [photo for photo in photos if self.exists(photo['id'])]
