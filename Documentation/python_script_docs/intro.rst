Introduction
============

dfnworks is a parallalized computational suite to generate three-dimensional discrete fracture networks (DFN) and simulate flow and transport.

Developed at  Los Alamos National Laboratory since 2011, dfnWorks has been used to study flow and transport in fractured media at scales ranging from millimeters to kilometers.

The dfnworks suite mitigates this principal drawback of high computational cost, and allows researchers to perform numerical experiments of flow and transport through fractured porous media which were previously deemed unfeasible.

The networks are created and meshed using dfnGen, which combines FRAM (the feature rejection algorithm for meshing) methodology to stochastically generate three-dimensional DFNs on the basis of site specific data with the LaGriT meshing toolbox to create a high-quality computational mesh representation, specifically a conforming Delaunay triangulation suitable for high performance computing finite volume solvers,  of the DFN in an intrinsically parallel fashion.

Flow through the network is simulated in dfnFlow, which utilizes the massively parallel subsurface flow and reactive transport finite volume code PFLOTRAN.

A Lagrangian approach to simulating transport through the DFN is adopted within dfnTrans, which is an extension of the of the walkabout particle tracking method to determine pathlines through the DFN.

Publications, videos, and links that describe software components of dfnWorks including PFLOTRAN and LaGriT can be found at: http://www.lanl.gov/org/padste/adcles/earth-environmental-sciences/computational-earth-science/software/dfnworks/index.php 

Installation
------------

Python 
^^^^^^

dfnWorks_ is supported on Python 2.6 and 2.7, but NOT 3.x. Instructions for downloading and installing Python can be
found at http://www.python.org. dfnWorks requiresi the  NumPy, SciPy,i and  Matplotlib modules to be installed.

dfnWorks
^^^^^^^^^

A download link for the latest release version 2.0.0 of dfnWorks_ can be found at JDH_TODO.

.. _dfnWorks: http://www.lanl.gov/org/padste/adcles/earth-environmental-sciences/computational-earth-science/software/dfnworks/index.php

__ dfnWorks_

To install, first, download and extract the zip file from the GitHub repository, or clone the GitHub repostiory.  Then, run the setup script, in the python_scripts folder,  at the command line: 

``python setup.py install``

PFLOTRAN
^^^^^^^^
PFLOTRAN_ (http://www.pflotran.org) is a massively parallel subsurface flow and reactive transport code. PFLOTRAN solves a system of partial differential equations for multiphase, multicomponent and multiscale reactive flow and transport in porous media. The code is designed to run on leadership-class supercomputers as well as workstations and laptops.

For successfully using dfnWorks, one needs to install PFLOTRAN. For details to install PFLOTRAN please see the wikipage: https://bitbucket.org/pflotran/pflotran-dev/wiki/Home 

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

Import dfnWorks
----------------

dfnWorks consists of several Python modules. To access their functionality, the user must include the following line at the 
top of any Python script

``from modules import*``

Before doing this, one needs to ensure that dfnWorks directory is in the PYTHONPATH. This can be done by configuring cshrc or bashrc files. Alternatively, one can add the dfnWorks path using sys.path.append() in their driver script.

About this  manual
------------------

This manual comprises sections for each of the important dfnWorks modules: :ref:`modules <modules-chapter>` In these, the important
classes and their methods are documented, and example usage provided. Examples can be found in the 'tests' directory of the dfnWorks repository. One can get a feel for setting up, running and visualizing dfnWorks simulations (both flow and reactive transport) through these examples.

Contributors
------------

Jeffrey Hyman and Nathaniel Knapp

Acknowledgements
----------------

JDH_TODO
