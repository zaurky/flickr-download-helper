from flickr_download_helper.config import OPT, Singleton
from flickr_download_helper.existing import mkdir_p
from flickr_download_helper.utils import waitFor
import os


class DownloadFile(Singleton):
    _file = None

    def write(self, content):
        if self._file is None:
            filename = OPT.downloads_file
            try:
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname):
                    mkdir_p(dirname)

                self._file = open(filename, 'ab')
            except OSError, err:
                if err.errno == 28:
                    if waitFor("there is not enough space to continue, " \
                            "please delete some files and try again"):
                        self._file = open(filename, 'ab')
                    else:
                        raise
                else:
                    raise

        self._file.write(content.encode('utf8') + "\n")
        self._file.flush()
