#!/usr/bin/python

"""
flickr_download_helper.py

This small program was developed to help retrieve full bunch of photos from flickr.

To have the description of the parameters, please read flickr_download_helper.config or start the program with the --help flag
"""

import sys
import traceback
import flickr_download_helper
from flickr_download_helper.logger import Logger
from flickr_download_helper.config import OPT

if __name__ == "__main__":
    try:
        api, token = flickr_download_helper.main_init()
        ret, num = flickr_download_helper.main(api, token)
        sys.exit(ret)
    except Exception, e:
        info = sys.exc_info()
        if OPT.debug:
            try:
                Logger().error(info[1])
                Logger().print_tb(info[2])
            except:
                print info
                print info[1]
                traceback.print_tb(info[2])
        else:
            try:
                Logger().error(info[1])
            except:
                print info[1]
                traceback.print_tb(info[2])
        sys.exit(-1)
