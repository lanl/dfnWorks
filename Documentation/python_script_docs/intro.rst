Introduction
============

PyFLOTRAN is a set of classes and methods that the enable use of the massively parallel subsurface flow and reactive transport code PFLOTRAN_ (http://www.pflotran.org)  within the Python scripting environment. This allows the use of a wide range of libraries available in Python for pre- and post- processing. The main advantages of using PyFLOTRAN include

1. PFLOTRAN input file construction from Python environment. Reduces the need to learn all the keywords in PFLOTRAN.    (see Chapter :ref:`3 <pdata-chapter>`).

2. Post-processing of output using matplotlib as well as including Python-based commandline calls to the open-source visualization toolkits such as VisIt and Paraview.

3. Scripting tools that supports Python's built-in multi-processing capabilities for batch simulations. This reduces the time spent in creating separate input files either for multiple realizations or multiple simulations for comparison.

4. Streamlined workflow from pre-processing to post-processing. Typical workflow with PFLOTRAN involves -- pre-processing in Python or MATLAB, writing input files, executing the input files and then post-processing using matplotlib, VisIt or Paraview. PyFLOTRAN allows users to perform all these steps using one Python script.


Installation
------------

Python 
^^^^^^

PyFLOTRAN_ is supported on Python 2.6 and 2.7, but NOT 3.x. Instructions for downloading and installing Python can be
found at http://www.python.org. PyFLOTRAN requires NumPy, SciPy, Matplotlib modules to be installed

PyFLOTRAN
^^^^^^^^^

A download link for the latest release version 1.0.0 of PyFLOTRAN_ can be found at https://bitbucket.org/satkarra/pyflotran-release-v1.0.0 

.. _PyFLOTRAN: http://pyflotran.lanl.gov

__ PyFLOTRAN_

To install, download and extract the zip file, and run the setup script at the command line: 

``python setup.py install``

PFLOTRAN
^^^^^^^^
PFLOTRAN_ (http://www.pflotran.org) is a massively parallel subsurface flow and reactive transport code. PFLOTRAN solves a system of partial differential equations for multiphase, multicomponent and multiscale reactive flow and transport in porous media. The code is designed to run on leadership-class supercomputers as well as workstations and laptops.

For successfully using PyFLOTRAN, one needs to install PFLOTRAN. For details to install PFLOTRAN please see the wikipage: https://bitbucket.org/pflotran/pflotran-dev/wiki/Home 

.. _PFLOTRAN: https://www.pflotran.org/

__ PFLOTRAN_

VisIt
^^^^^^^^

VisIt_ is a parallel, open-source visualisation software. PFLOTRAN can output in .h5 and .xmf format. These can be imported in VisIt and visualization can be performed. 

Instructions for downloading and installing VisIt_ can be found at https://wci.llnl.gov/codes/visit/download.html 

.. _VisIt: https://wci.llnl.gov/codes/visit

__ VisIt_ 


Paraview
^^^^^^^^

Paraview_ is a parallel, open-source visualisation software. PFLOTRAN can output in .xmf and .vtk format. These can be imported in Paraview and visualization can be performed. 

Instructions for downloading and installing Paraview_ can be found at http://www.paraview.org 

.. _Paraview: http://www.paraview.org

__ Paraview_

Import PyFLOTRAN
----------------

PyFLOTRAN consists of several Python modules. To access their functionality, the user must include the following line at the 
top of any Python script

``from pdata import*``

Before doing this, one needs to ensure that pyflotran directory is in the PYTHONPATH. This can be done by configuring cshrc or bashrc files. Alternatively, one can add the PyFLOTRAN path using sys.path.append() in their driver script.

About this  manual
------------------

This manual comprises sections for each of the important PyFLOTRAN modules: :ref:`pdata <pdata-chapter>` In these, the important
classes and their methods are documented, and example usage provided. Examples can be found in the 'tests' directory of the PyFLOTRAN repository. One can get a feel for setting up, running and visualizing PFLOTRAN simulations (both flow and reactive transport) through these examples.

Contributors
------------

Greg Lackey, CU Boulder -- Added the dataset and simulation related keywords.


Acknowledgements
----------------

PyFLOTRAN was partly developed as part of Cory Kitay's undergraduate internship in the Computational Earth Science Group (EES-16) at the Los Alamos National Laboratory in summer 2014. He was supported through U.S. DOE's Student Undergraduate Laboratory Internship (SULI) program and through LANL LDRD project 20140002DR. 
David Dempsey's guidance and help in developing PyFLOTRAN is highly appreciated. The motivation behind PyFLOTRAN has been the cool capabilities that Dempsey has developed in PyFEHM (http://pyfehm.lanl.gov).
