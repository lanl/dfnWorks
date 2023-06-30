#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for pysimfrac 
You can install pysimfrac with
python setup.py install 
or
python setup.py install --user 
"""

import os
import sys
import shutil
from setuptools import setup

dirs = ["build", "pysimfrac.egg-info", "dist"]
for d in dirs:
    if os.path.exists(d):
        shutil.rmtree(d)

if sys.argv[-1] == 'setup.py':
    print("To install, run 'python setup.py install'")
    print()

if sys.version_info[:2] < (3, 8):
    error = """pySimFrac requires Python 3.8 or later (%d.%d detected).
""" % sys.version_info[:2]
    sys.stderr.write(error + "\n")
    sys.exit(1)

from pysimfrac import release

if __name__ == "__main__":

    setup(
        name=release.name.lower(),
        version=release.version,
        maintainer=release.maintainer,
        maintainer_email=release.maintainer_email,
        author=release.authors['Hyman'][0],
        author_email=release.authors['Hyman'][1],
        description=release.description,
        keywords=release.keywords,
        long_description=release.long_description,
        license=release.license,
        platforms=release.platforms,
        #url=release.url,
        #project_urls=release.project_urls,
        classifiers=release.classifiers,
        packages=release.packages,
        install_requires=release.install_requires,
        python_requires='>=3.8',
        test_suite='nose.collector',
        tests_require=['nose>=1.3.7'],
        zip_safe=False)
