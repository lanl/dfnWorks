#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for pydfnworks
You can install pydfnworks with
pip install -r requirements.txt 
or
pip install -r requirements.txt --user

if you don't have admin privileges. 
"""

import os
import sys
import shutil
from setuptools import setup, find_namespace_packages

dirs = ["build", "pydfnworks.egg-info", "dist"]
for d in dirs:
    if os.path.exists(d):
        shutil.rmtree(d)

if sys.argv[-1] == 'setup.py':
    print("To install, run 'pip install -r requirements.txt'")
    print()

if sys.version_info[:2] < (3, 6):
    error = f"pydfnworks 2.4+ requires Python 3.6 or later ({sys.version_info[:2]} detected) %\n"
    sys.stderr.write(error)
    sys.exit(1)

from pydfnworks import release

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
        url=release.url,
        project_urls=release.project_urls,
        classifiers=release.classifiers,
        packages=release.packages,
        install_requires=release.install_requires,
        python_requires='>=3.5',
        test_suite='nose.collector',
        tests_require=['nose>=1.3.7'],
        zip_safe=False,
        include_package_data=True,
        package_data={'': ['dfnGen/generation/output_report/figures/*png']}
    )
