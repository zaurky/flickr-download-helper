
from flickr_download_helper.types import FDHPR

class UrlParser:
    def  __init__(self, url = None):
        self.url = url
    def parse(self, url=None):
        if url == None:
            if self.url == None: return (FDHPR.ERROR_NOURL)
            url = self.url
        a_url = url.split('/')
        if a_url[len(a_url) - 1] == '':
            a_url.pop()
        if a_url[2] != 'www.flickr.com':
            print "url is not a flickr url! %s"%url
            return (FDHPR.ERROR_NOTFLICKR)
        if a_url[len(a_url) - 2] == 'with' or a_url[len(a_url) - 2] == 'in':
            a_url.pop()
            a_url.pop()
        print a_url
        print len(a_url)

        if len(a_url) == 5:
            if a_url[3] == 'photos':
                # should be a full flickr account
                print "account %s"%a_url[4]
                return (FDHPR.USER, a_url[4])
            elif a_url[3] == 'people':
                # should be a user's profile
                print "profile of user %s"%a_url[4]
                return (FDHPR.PROFILE, a_url[4])
            elif a_url[3] == 'groups':
                print "group %s"%a_url[4]
                return (FDHPR.GROUP, a_url[4])
        elif len(a_url) == 6:
            if a_url[3] == 'photos' and a_url[5] == 'sets':
                print "photosets in account %s"%( a_url[4])
                return (FDHPR.PHOTOSETS, a_url[4])
            elif a_url[3] == 'photos':
                # should be a picture in a flickr account
                print "photo %s in account %s"%(a_url[5], a_url[4])
                return (FDHPR.PHOTO, a_url[4], a_url[5])
            elif a_url[3] == 'groups':
                print "group %s"%a_url[4]
                return (FDHPR.GROUP, a_url[4])
        elif len(a_url) == 7:
            if a_url[3] == 'photos' and a_url[5] == 'collections':
                # should be a collection in a flick account
                print "collection %s in account %s"%(a_url[6], a_url[4])
                return (FDHPR.COLLECTION, a_url[4], a_url[6])
            elif a_url[3] == 'photos' and a_url[5] == 'sets':
                # should be a set
                print "set %s %s"%(a_url[4], a_url[6])
                return (FDHPR.SET, a_url[4], a_url[6])
            elif a_url[3] == 'photos' and a_url[5] == 'tags':
                print "tag %s %s"%(a_url[4], a_url[6])
                return (FDHPR.TAG, a_url[4], a_url[6])
            elif a_url[3] == 'groups' and a_url[5] == 'pool':
                print "user %s in groups %s"%(a_url[6], a_url[4])
                return (FDHPR.INGROUP, a_url[6], a_url[4])
        return (FDHPR.ERROR)
