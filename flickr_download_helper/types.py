class FlickrDownloadHelperErrorTypes:
    DISPLAY_HELP = 1


FDHET = FlickrDownloadHelperErrorTypes


class FlickrDownloadHelperParserResponse:
    USER = 1
    SET = 2
    COLLECTION = 3
    PHOTO = 4
    PROFILE = 5
    PHOTOSETS = 6
    TAG = 7
    GROUP = 8
    INGROUP = 9
    SEARCH = 13

    ERROR = 10
    ERROR_NOURL = 11
    ERROR_NOTFLICKR = 12


FDHPR = FlickrDownloadHelperParserResponse
