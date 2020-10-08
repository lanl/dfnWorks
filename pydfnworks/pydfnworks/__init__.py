#!/usr/bin/env python
"""
pydfnWorks
==========

pydfnWorks is a python wrapper for the discrete fracture network
modeling suite dfnWorks

Website (including Documentation)::

    http://dfnworks.lanl.gov

Mailing list::

    https://groups.google.com/d/forum/dfnworks-users

Source::
    
    https://github.com/lanl/dfnWorks

Bug reports::

    https://github.com/lanl/dfnWorks/issues

License
-------

Released under the GPL License

    Copyright (C) 20015-2019 dfnWorks Developers
    Jeffrey Hyman <jhyman@lanl.gov>
    Daniel Livingston <livingston@lanl.gov>
    Satish Karra < satkarra@lanl.gov>
    
"""
from pydfnworks import release

__author__ = '%s <%s>\n%s <%s>\n%s <%s>' % \
    (release.authors['Hyman'] + release.authors['Livingston'] +
        release.authors['Karra'])

__license__ = release.license

__date__ = release.date

__version__ = release.version

__bibtex__ = """@article{hyman2015dfnworks,
  title={dfnWorks: A discrete fracture network framework for modeling subsurface flow and transport},
  author={Hyman, Jeffrey D and Karra, Satish and Makedonska, Nataliia and Gable, Carl W and Painter, Scott L and Viswanathan, Hari S},
  journal={Computers \& Geosciences},
  volume={84},
  pages={10--19},
  year={2015},
  publisher={Elsevier}
}
"""

import pydfnworks.dfnGen

import pydfnworks.general
from pydfnworks.general import *
