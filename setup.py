#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = ['redis',
            'celery',
            'celery[redis]']

version='0.0.2'

setup(name='fdh',
      version=version,
      description='Utility helping with flickr interactions.'
      long_description=README + '\n\n' + CHANGES,
      author='Zaurky',
      author_email='zaurky@zeb.re',
      classifiers=[
          'Programming Language :: Python',
          'Topic :: Terminals'
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      ],
      url='https://github.com/zaurky/flickr-download-helper',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
[console_scripts]
fdh = fdh.bin.fdh:main
""",
      )


