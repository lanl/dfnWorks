# to run tests: python setup.py test

from setuptools import setup

setup(name='pydfnworks',
      version='2.0',
      description='Python methods for running dfnWorks',
      url='TBD',
      author='Jeffrey Hyman, Satish Karra, Nathaniel Knapp, Nataliia Makedonska',
      author_email='dfnworks@lanl.gov',
      #licenses='MIT',
      packages=['pydfnworks'],
      install_requires=[
          'numpy',
          'scipy',
          'h5py',
      ],
      include_package_data=True, 
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['bin/compile.py', 'bin/test.py', 'bin/run.py', 'bin/run_explicit.py'],
      dependency_links=['https://github.com/deknapp/testdfn/tarball/master#egg-package-1.0'],
      zip_safe=False)
