Introduction
============

dfnWorks is a parallelized computational suite to generate three-dimensional discrete fracture networks (DFN) and simulate flow and transport. Developed at Los Alamos National Laboratory, it has been used to study flow and transport in fractured media at scales ranging from millimeters to kilometers. The networks are created and meshed using dfnGen, which combines FRAM (the feature rejection algorithm for meshing) methodology to stochastically generate three-dimensional DFNs with the LaGriT meshing toolbox to create a high-quality computational mesh representation. The representation produces a conforming Delaunay triangulation suitable for high performance computing finite volume solvers in an intrinsically parallel fashion. Flow through the network is simulated with dfnFlow, which utilizes the massively parallel subsurface flow and reactive transport finite volume code PFLOTRAN. A Lagrangian approach to simulating transport through the DFN is adopted within dfnTrans to determine pathlines and solute transport through the DFN. Applications of the dfnWorks suite include nuclear waste repository science, hydraulic fracturing and |CO2| sequestration.

.. |CO2| replace:: CO\ :sub:`2`    

To run a workflow using the dfnWorks suite, the pydfnworks package is highly recommended. pydfnworks calls various tools in the dfnWorks suite; its aim is to provide a seamless workflow for scientific applications of dfnWorks.

Citing dfnWorks
---------------
`Hyman, J. D., Karra, S., Makedonska, N., Gable, C. W., Painter, S. L., & Viswanathan, H. S. (2015). dfnWorks: A discrete fracture network framework for modeling subsurface flow and transport. Computers & Geosciences, 84, 10-19. <http://www.sciencedirect.com/science/article/pii/S0098300415300261/>`_

*BibTex:*

.. code-block:: none

	@article{hyman2015dfnworks,
	  title={dfnWorks: A discrete fracture network framework
      for modeling subsurface flow and transport},
	  author={Hyman, Jeffrey D and Karra, Satish and Makedonska,
      Nataliia and Gable, Carl W and Painter, Scott L
      and Viswanathan, Hari S},
	  journal={Computers \& Geosciences},
	  volume={84},
	  pages={10--19},
	  year={2015},
	  publisher={Elsevier}
	}


What's new in v2.0?
-------------------
- New dfnGen C++ code which is much faster than the Mathematica dfnGen. This code has successfully generated networks with 350,000+ fractures. 
- Increased functionality in the pydfnworks package for more streamlined workflow from dfnGen through visualization.


Where can one get dfnWorks?
---------------------------
dfnWorks 2.0 can be downloaded from https://github.com/dfnWorks/dfnWorks-Version2.0

v1.0 can be downloaded from https://github.com/dfnWorks/dfnWorks-Version1.0  


Installation
------------
Tools that you will need to run the dfnWorks work flow are described in this section. VisIt and ParaView, which enable visualization of desired quantities on the DFNs, are optional, but at least one of them is highly recommended for visualization. CMake is also optional but allows faster IO processing using C++. 

Python 
^^^^^^

pydfnworks is supported on Python 2.7. The software authors recommend using the Anaconda 2.7 distribution of Python, available at https://www.continuum.io/. 
pydfnworks requires the ``numpy`` and ``h5py`` modules to be installed.

pydfnworks
^^^^^^^^^^^^^^^

The source for pydfnworks can be found in the dfnWorks suite, in the folder pydfnworks. 

dfnGen
^^^^^^
dfnGen primarily involves two steps:

1. FRAM - Create DFN: Using the fractured site characterization networks are constructed using the feature rejection algorithm for meshing
2. LaGriT - Mesh DFN: The LaGriT meshing tool box is used to create a conforming Delaunay triangulation of the network.


FRAM
******
FRAM (the feature rejection algorithm for meshing) is executed using the dfnGen C++ source code, contained in the dfnGen folder of the dfnWorks repository.

LaGriT
******
The LaGriT_ (http://lagrit.lanl.gov) meshing toolbox is used to create a high resolution computational mesh representation of the DFN in parallel. An algorithm for conforming Delaunay triangulation is implemented so that fracture intersections are coincident with triangle edges in the mesh and Voronoi control volumes are suitable for finite volume flow solvers such as FEHM and PFLOTRAN.

dfnFlow
^^^^^^^
You will need one of either PFLOTRAN or FEHM to solve for flow using the mesh files from LaGriT. 

PFLOTRAN
********
PFLOTRAN_ (http://www.pflotran.org) is a massively parallel subsurface flow and reactive transport code. PFLOTRAN solves a system of partial differential equations for multiphase, multicomponent and multiscale reactive flow and transport in porous media. The code is designed to run on leadership-class supercomputers as well as workstations and laptops.

.. _PFLOTRAN: https://www.pflotran.org/

FEHM
****
FEHM_ (http://fehm.lanl.gov) is a subsurface multiphase flow code developed at Los Alamos National Laboratory.

dfnTrans
^^^^^^^^
dfnTrans is a method for resolving solute transport using control volume flow solutions obtained from dfnFlow on the unstructured mesh generated using dfnGen. We adopt a Lagrangian approach and represent a non-reactive conservative solute as a collection of indivisible passive tracer particles.  

CMake
^^^^^^^
CMake (https://cmake.org/) is an open-source, cross-platform family of tools designed to build, test and package software. It is needed to use C++ for processing files at a bottleneck IO step of dfnWorks. Using C+C++ for this file processing optional but can greatly increase the speed of dfnWorks for large fracture networks. Details on how to use C++ for file processing are in the scripts section of this documentation.

VisIt
^^^^^

VisIt_ is a parallel, open-source visualisation software. PFLOTRAN can output in ``.xmf`` and ``.vtk`` format. These can be imported in VisIt for visualization. 

Instructions for downloading and installing VisIt_ can be found at https://wci.llnl.gov/codes/visit/download.html 

.. _VisIt: https://wci.llnl.gov/codes/visit

Paraview
^^^^^^^^

Paraview_ is a parallel, open-source visualisation software. PFLOTRAN can output in ``.xmf`` and ``.vtk`` format. These can be imported in Paraview for visualization. 

Instructions for downloading and installing Paraview_ can be found at http://www.paraview.org 

.. _Paraview: http://www.paraview.org

Using pydfnworks in your Python scripts
--------------------------------------------

To access the functionality of pydfnworks, the user must include the following line at the 
top of any Python script

.. code-block:: python
	
	import pydfnworks 

Before doing this, one needs to ensure that the pydfnworks directory is in the PYTHONPATH. This can be done by configuring ``cshrc`` or ``bashrc`` files. Alternatively, one can add the pydfnworks path using ``sys.path.append()`` in their driver script.

About this  manual
------------------

This manual comprises of information on setting up inputs to dfnGen, dfnTrans and PFLOTRAN, as well as details on the pydfnworks module: :ref:`pydfnworks <dfnworks-python-chapter>`. Finally, the manual contains a short tutorial with prepared examples that  can be found in the ``tests`` directory of the dfnWorks repository, and a description of some applications of the dfnWorks suite.

Contributors
-------------
- Satish Karra
- Nataliia Makedonska
- Jeffrey Hyman
- Jeremy Harrod (now at Spectra Logic)
- Quan Bui (now at University of Maryland)
- Carl Gable
- Scott Painter (now at ORNL)
- Hari Viswanathan
- Nathaniel Knapp

Contact
--------

For any questions about dfnWorks, please email dfnworks@lanl.gov.

Copyright information
----------------------

Documentation:

LA-UR-17-22216

Software copyright:

LA-CC-17-027

Copyright (2017).  Los Alamos National Security, LLC. This material was produced under U.S. Government contract DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is operated by Los Alamos National Security, LLC for the U.S. Department of Energy. The U.S. Government has rights to use, reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is modified to produce derivative works, such modified software should be clearly marked, so as not to confuse it with the version available from LANL.

Additionally, this program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. Accordingly, this program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


.. dfnWorks documentation master file, created by Satish Karra Oct 6, 2016
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

