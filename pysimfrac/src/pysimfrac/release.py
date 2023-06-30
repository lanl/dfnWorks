import datetime

now = datetime.datetime.now()

name = "pySimFrac"

date = now.strftime("%Y-%m-%d %H:%M")

version = "0.2"

description = "Single Fracture generation and analysis"

long_description = \
    """
pySimfrac is a a Python package to make rough surfaces for single fractures
"""

authors = {
    'Hyman': ('Jeffrey Hyman', 'jhyman@lanl.gov'),
    'Santos': ('Javier Santos', 'jesantos@lanl.gov'),
    'Guiltinan': ('Eric Guiltinan', 'eric.guiltinan@lanl.gov'),
    'Purswani': ('Prakash Purswani', 'ppurswani@lanl.gov')
}

license = "GPL"

maintainer = "pySimFrac Developers, Jeffrey Hyman"

maintainer_email = "jhyman@lanl.gov"

url = 'https://github.com/hymanjd/pysimfrac'

# project_urls={
#     "Bug Tracker": "https://github.com/lanl/dfnWorks/issues",
#     "Documentation": "https://dfnworks.lanl.gov/index_docs.html",
#     "Source Code": "https://github.com/lanl/dfnWorks/tree/master/pydfnworks",
#     "Mailing List": "https://groups.google.com/d/forum/dfnworks-users",
# }

platforms = ['Linux', 'Mac OSX', 'Unix']

keywords = [
    'Fracture Roughness', 'Subsurface flow and Transport', 'Graph Theory',
    'Mathematics', 'Fracture Networks', 'Simulations', 'Computational Geometry'
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers', 'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Geoscience',
    'Topic :: Scientific/Engineering :: Physics'
]

packages = [
    "pysimfrac", "pysimfrac.src", "pysimfrac.src.general", "pysimfrac.src.methods",
    "pysimfrac.src.analysis", "pysimfrac.src.io", "pysimfrac.src.analysis.effective_aperture",
]

install_requires = ["numpy", "scipy", "matplotlib", 
                    "seaborn", "scikit-gstat", "vedo"]
