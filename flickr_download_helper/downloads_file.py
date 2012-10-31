from flickr_download_helper.config import OPT, Singleton
from flickr_download_helper.logger import Logger
from flickr_download_helper.existing import mkdir_p
import shutil
import os, errno

class DownloadFile(Singleton):
    file = None
    def write(self, content):
        if self.file is None:
            filename = OPT.downloads_file
            try:
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname): mkdir_p(dirname)
                self.file = open(filename, 'ab')
            except OSError, e:
                if e.errno == 28:
                    ret = waitFor("there is not enough space to continue, please delete some files and try again")
                    if ret:
                        self.file = open(filename, 'ab')
                    else:
                        raise e
                else:
                    raise e
        self.file.write("%s\n"%(content.encode('utf8')))
        self.file.flush()
