#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT, OptReader
import pickle
import shutil
import os, errno


config = OptConfigReader()
config.setup()

file = os.path.join(OPT['files_dir'], "doubles")

content = {}
if os.path.exists(file):
    shutil.move(file, "%s.bkp"%(file))
    f = open(file, 'rb')
    content = pickle.load(f)
    f.close()

#####################
# DO THE STUFF
#####################
r_content = content.values()

def get_files(directory):
    for f in os.listdir(directory):
        ret = []
        if os.path.is_file(f): # file
            if f not in content:
                ret.append(f)
        elif os.path.is_dir(f): # dir
            ret.extend(get_files(f))
        return ret

files = get_files(OPT['photo_dir'])

for f in files:
    content[f] = md5sum





#####################

f = open(file, 'wb')
pickle.dump(content, f)
f.close()


