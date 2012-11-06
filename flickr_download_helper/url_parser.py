from flickr_download_helper.types import FDHPR
from flickr_download_helper.logger import Logger


class UrlParser:

    def  __init__(self, url=None):
        self.url = url

    def parse(self, url=None):
        if not url:
            if not self.url:
                return (FDHPR.ERROR_NOURL)
            url = self.url

        a_url = url.split('/')
        if not a_url[-1]:
            a_url.pop()

        if a_url[2] != 'www.flickr.com':
            Logger().warn("url is not a flickr url! %s" % url)
            return (FDHPR.ERROR_NOTFLICKR)

        if a_url[len(a_url) - 2] == 'with' or a_url[len(a_url) - 2] == 'in':
            a_url.pop()
            a_url.pop()

        keyword, param, extra1, extra2 = a_url[3:7]

        Logger().debug("%s %s %s %s" % (keyword, param, extra1, extra2))

        if len(a_url) == 5:
            if keyword == 'photos':
                # should be a full flickr account
                Logger().info("account %s" % param)
                return (FDHPR.USER, param)
            elif keyword == 'people':
                # should be a user's profile
                Logger().info("profile of user %s" % param)
                return (FDHPR.PROFILE, param)
            elif keyword == 'groups':
                Logger().info("group %s" % param)
                return (FDHPR.GROUP, param)

        elif len(a_url) == 6:
            if keyword == 'photos' and extra1 == 'sets':
                Logger().info("photosets in account %s" % (param))
                return (FDHPR.PHOTOSETS, param)
            elif keyword == 'photos':
                # should be a picture in a flickr account
                Logger().info("photo %s in account %s" % (extra1, param))
                return (FDHPR.PHOTO, param, extra1)
            elif keyword == 'groups':
                Logger().info("group %s" % param)
                return (FDHPR.GROUP, param)

        elif len(a_url) == 7:
            if keyword == 'photos' and extra1 == 'collections':
                # should be a collection in a flick account
                Logger().info("collection %s in account %s" % (extra2, param))
                return (FDHPR.COLLECTION, param, extra2)
            elif keyword == 'photos' and extra1 == 'sets':
                # should be a set
                Logger().info("set %s %s" % (param, extra2))
                return (FDHPR.SET, param, extra2)
            elif keyword == 'photos' and extra1 == 'tags':
                Logger().info("tag %s %s" % (param, extra2))
                return (FDHPR.TAG, param, extra2)
            elif keyword == 'groups' and extra1 == 'pool':
                Logger().info("user %s in groups %s" % (extra2, param))
                return (FDHPR.INGROUP, extra2, param)

        return (FDHPR.ERROR)
