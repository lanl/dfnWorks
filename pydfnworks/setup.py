import sys
import os
import shutil 
from setuptools import setup

dirs = ["build", "pydfnworks.egg-info", "dist"]
for d in dirs:
    if os.path.isdir(d):
        shutil.rmtree(d)

setup(name='pydfnworks',
      version='2.2',
      description='Python wrapper for dfnWorks',
      url='https://dfnworks.lanl.gov',
      author='Jeffrey Hyman, Satish Karra, Daniel Livingston, Nataliia Makedonska',
      author_email='dfnworks@lanl.gov',
      packages=['pydfnworks','pydfnworks/general', 
            'pydfnworks/dfnGen', 'pydfnworks/dfnFlow',
            'pydfnworks/dfnTrans', 'pydfnworks/dfnGraph'],
      install_requires=[
          'numpy',
          'scipy',
          'h5py',
          'pyvtk',
          'networkx',
          'matplotlib<3.0',
      ],
      include_package_data=True, 
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
