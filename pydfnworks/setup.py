# to run tests: python setup.py test
import sys
#from distutils.core import setup
from setuptools import setup
import os
#os.system('mv ~/.local ~/local_save')
from shutil import rmtree 


dirs = ["build", "pydfnworks.egg-info"]
for d in dirs:
    
    print("Removing dir %s"%d)
    try:
        rmtree(d)
    except:
        print("Unable to remove %s"%d)

setup(name='pydfnworks',
      version='2.2',
      description='Python methods for running dfnWorks',
      url='https://dfnworks.lanl.gov',
      author='Jeffrey Hyman, Satish Karra, Daniel Livingston, Nataliia Makedonska',
      author_email='dfnworks@lanl.gov',
      licenses='BSD',
      packages=['pydfnworks'],
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
      scripts=['bin/run.py', 'bin/run_explicit.py'],
      zip_safe=False)
