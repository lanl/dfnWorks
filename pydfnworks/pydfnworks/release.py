
name = "pydfnWorks"

date = "22 June 2022"

version = "2.6.1"

description = "This python package serves as a wrapper for dfnWorks"

long_description = \
    """
pydfnWorks is a a Python package interactively working with the 
dfnWorks DFN simulate suite. 
"""
license = 'GPL'

authors = {'Hyman': ('Jeffrey Hyman', 'jhyman@lanl.gov'),
  'Livingston': ('Daniel Livingston', 'livingston@lanl.gov'),
  'Gable': ('Carl Gable', 'gable@lanl.gov'),
  'Karra': ('Satish Karra', 'satkarra@lanl.gov'),
  'Makedonska': ('Nataliia Makedonska', 'nataliia@lanl.gov'),
  'Sweeney': ('Matthew Sweeney', 'sweeney2796@lanl.gov')
}

maintainer = "dfnWorks Developers"

maintainer_email = "dfnworks@lanl.gov"

url = 'http://dfnworks.lanl.gov'

project_urls={
    "Bug Tracker": "https://github.com/lanl/dfnWorks/issues",
    "Documentation": "https://dfnworks.lanl.gov/index_docs.html",
    "Source Code": "https://github.com/lanl/dfnWorks/tree/master/pydfnworks",
    "Mailing List": "https://groups.google.com/d/forum/dfnworks-users",
}

platforms = ['Linux', 'Mac OSX', 'Unix']

keywords = ['Discrete Fracture Networks', 'Subsurface flow and Transport',
            'Graph Theory', 'Mathematics','Fracture Networks', 'Simulations',
            'Computational Geometry','network', 'graph', 'discrete mathematics',
             'math']

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics']

packages=["pydfnworks",
          "pydfnworks.general", 
          "pydfnworks.dfnGen",
          "pydfnworks.dfnGen.generation",
          "pydfnworks.dfnGen.generation.input_checking",
          "pydfnworks.dfnGen.generation.output_report",
          "pydfnworks.dfnGen.meshing",
          "pydfnworks.dfnGen.meshing.udfm",
          "pydfnworks.dfnGen.meshing.poisson_disc",
          "pydfnworks.dfnGen.well_package",
          "pydfnworks.dfnFlow",
          "pydfnworks.dfnTrans",
          "pydfnworks.dfnGraph"]

install_requires=["numpy",
          "scipy",
          "h5py",
          "pyvtk",
          "fpdf",
          "pytz",
          "datetime",
          "networkx>=2.4",
          "mplstereonet",
          "matplotlib>3.0"]
