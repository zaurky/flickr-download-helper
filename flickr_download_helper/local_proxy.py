import os

from flickr_download_helper.logger import Logger
from flickr_download_helper.api import downloadPhotoFromURL


class LocalProxy():
    home_path = '/var/www/html/proxy/'
    web_path = 'http://%s/' % '192.168.100.176/proxy'

    def convert2path(self, url):
        path = url.replace('http://', self.home_path)
        url = url.replace('http://', self.web_path)
        return (path, url)

    def modifyProxyPhotos(self, photos, field):
        ret = []
        for photo in photos:
            if field in photo:
                orig_url = photo[field]
                path, url = self.convert2path(orig_url)
                if not os.path.exists(path):
                    Logger().debug("%s dont exists, downloading it into %s"%(orig_url, path))
                    downloadPhotoFromURL(orig_url, path)
                photo[field] = url
            ret.append(photo)
        return ret
