#!/usr/bin/python

from flickr_download_helper.config import OptConfigReader, OPT, OptReader
import pickle
import shutil
import os, errno

import md5
import sys

config = OptConfigReader()
config.setup()

file = os.path.join(OPT.files_dir, "doubles")

content = {}
h_filesmd5 = {}
h_md5files = {}
h_double = {}

if os.path.exists(file):
    shutil.move(file, "%s.bkp"%(file))
    f = open(file, 'rb')
    content = pickle.load(f)
    f.close()

if 'h_filesmd5' in content:
    h_filesmd5 = content['h_filesmd5']

if 'h_md5files' in content:
    h_md5files = content['h_md5files']
    r_content = h_md5files.keys()
else:
    r_content = []

if 'h_double' in content:
    h_double = content['h_double']

#####################
# DO THE STUFF
#####################
def get_md5(path):
    fd = open(path, 'rb')
    ret = md5.new(fd.read()).hexdigest()
    fd.close()
    return ret

def get_files(directory):
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        if os.path.isfile(path): # file
            if f not in r_content:
                md5sum = get_md5(path)
                h_filesmd5[path] = md5sum
                if md5sum in h_md5files:
                    if path not in h_md5files[md5sum]:
                        h_double[path] = md5sum
                        h_md5files[md5sum].append(path)
                else:
                    h_md5files[md5sum] = []
        elif os.path.isdir(path): # dir
            get_files(path)

import Set
def uniq(seq):
    # Not order preserving    
    s = set(seq)
    return list(s)

get_files(OPT.photo_dir)


#####################
content['h_filesmd5'] = h_filesmd5
content['h_double'] = h_double
content['h_md5files'] = h_md5files

f = open(file, 'wb')
pickle.dump(content, f)
f.close()


