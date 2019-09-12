Introduction
============

dfnWorks is a parallelized computational suite to generate three-dimensional 
discrete fracture networks (DFN) and simulate flow and transport. Developed at 
Los Alamos National Laboratory, it has been used to study flow and transport 
in fractured media at scales ranging from millimeters to kilometers. The 
networks are created and meshed using dfnGen, which combines FRAM (the feature 
rejection algorithm for meshing) methodology to stochastically generate 
three-dimensional DFNs with the LaGriT meshing toolbox to create a high-quality 
computational mesh representation. The representation produces a conforming 
Delaunay triangulation suitable for high performance computing finite volume 
solvers in an intrinsically parallel fashion. Flow through the network is 
simulated with dfnFlow, which utilizes the massively parallel subsurface flow 
and reactive transport finite volume code PFLOTRAN. A Lagrangian approach to 
simulating transport through the DFN is adopted within dfnTrans to determine 
pathlines and solute transport through the DFN. Applications of the dfnWorks 
suite include nuclear waste repository science, hydraulic fracturing and 
|CO2| sequestration.

.. |CO2| replace:: CO\ :sub:`2`    

To run a workflow using the dfnWorks suite, the pydfnworks package is 
highly recommended. pydfnworks calls various tools in the dfnWorks suite with 
the aim to provide a seamless workflow for scientific applications of dfnWorks.

Citing dfnWorks
---------------
`Hyman, J. D., Karra, S., Makedonska, N., Gable, C. W., Painter, S. L., & 
Viswanathan, H. S. (2015). dfnWorks: A discrete fracture network framework 
for modeling subsurface flow and transport. Computers & Geosciences, 84, 
10-19. <http://www.sciencedirect.com/science/article/pii/S0098300415300261/>`_

*BibTex:*

.. code-block:: none

	@article{hyman2015dfnWorks,
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

What's new in v2.2?
-------------------

- pydfnWorks updated for python3
- Graph based (pipe-network approximations) for flow and transport
- Bug fixes in LaGrit Meshing 
- Increased functionalities in pydfnworks including the path option
- dfn2graph capabilities
- FEHM flow solver
- Streamline routing option in dfnTrans 
- Time Domain Random Walk in dfnTrans

What's new in v2.1?
-------------------

- Bug fixes in LaGrit Meshing 
- Increased functionalities in pydfnworks including the path option

What's new in v2.0?
-------------------

- New dfnGen C++ code which is much faster than the Mathematica dfnGen. This code has successfully generated networks with 350,000+ fractures. 
- Increased functionality in the pydfnworks package for more streamlined workflow from dfnGen through visualization. 


Where can one get dfnWorks?
---------------------------
dfnWorks 2.2 can be downloaded from https://github.com/lanl/dfnWorks/

v1.0 can be downloaded from https://github.com/dfnWorks/dfnWorks-Version1.0  


Installation
------------
Tools that you will need to run the dfnWorks work flow are described in 
this section. VisIt and ParaView, which enable visualization of desired 
quantities on the DFNs, are optional, but at least one of them is highly 
recommended for visualization. CMake is also optional but allows faster IO 
processing using C++. 


Operating Systems
^^^^^^^^^^^^^^^^^^
dfnWorks currently runs on Macs and Unix machine running Ubuntu. 


Python 
^^^^^^

pydfnworks is supported on Python 3. The software authors recommend using 
the Anaconda 3 distribution of Python, available at https://www.continuum.io/. 
pydfnworks requires the following python modules: ``numpy``, ``h5py``, ``scipy``, ``matplotlib``,  ``multiprocessing``, ``argparse``, ``shutil``, ``os``, ``sys``, ``networkx``, ``subprocess``, ``glob``, and ``re``.

pydfnworks
^^^^^^^^^^^^^^^

The source for pydfnworks can be found in the dfnWorks suite, in the folder 
pydfnworks. 

dfnGen
^^^^^^
dfnGen primarily involves two steps: FRAM (the feature rejection algorithm for meshing) and LaGriT, the meshing tool box used to create a conforming Delaunay triangulation of the network.

FRAM
******
FRAM (the feature rejection algorithm for meshing) is executed using the 
dfnGen C++ source code, contained in the dfnGen folder of the dfnWorks repository.

LaGriT
******
The LaGriT_ meshing toolbox is used to create a high resolution computational 
mesh representation of the DFN in parallel. An algorithm for conforming 
Delaunay triangulation is implemented so that fracture intersections are 
coincident with triangle edges in the mesh and Voronoi control volumes are 
suitable for finite volume flow solvers such as FEHM and PFLOTRAN.

.. _LaGriT: https://lagrit.lanl.gov

dfnFlow
^^^^^^^
You will need one of either PFLOTRAN or FEHM to solve for flow using the 
mesh files from LaGriT. 

PFLOTRAN
********
PFLOTRAN_  is a massively parallel subsurface flow and reactive transport 
code. PFLOTRAN solves a system of partial differential equations for 
multiphase, multicomponent and multiscale reactive flow and transport in 
porous media. The code is designed to run on leadership-class supercomputers 
as well as workstations and laptops.

.. _PFLOTRAN: http://pflotran.org

FEHM
****
FEHM_ is a subsurface multiphase flow code developed at Los Alamos National 
Laboratory.

.. _FEHM: https://fehm.lanl.gov

dfnTrans
^^^^^^^^
dfnTrans is a method for resolving solute transport using control volume flow 
solutions obtained from dfnFlow on the unstructured mesh generated using 
dfnGen. We adopt a Lagrangian approach and represent a non-reactive 
conservative solute as a collection of indivisible passive tracer particles.  

dfnGraph
^^^^^^^^
dfnGraph is a suite of graph-based methods for use with DFN generated using
dfnWorks DFN. This suite includes multiple methods to prune a DFN and simulate 
flow and transport in pipe-networks derived from a DFN. dfnGraph uses the 
networkX_ python software to handle graph representations. 

.. _networkX: https://networkx.github.io/

CMake
^^^^^^^
CMake_ is an open-source, cross-platform family of tools designed to build, 
test and package software. It is needed to use C++ for processing files at a 
bottleneck IO step of dfnWorks. Using C++ for this file processing optional 
but can greatly increase the speed of dfnWorks for large fracture networks. 
Details on how to use C++ for file processing are in the scripts section of 
this documentation.

.. _CMake: https://cmake.org

Paraview
^^^^^^^^

Paraview_ is a parallel, open-source visualisation software. PFLOTRAN can 
output in ``.xmf`` and ``.vtk`` format. These can be imported in Paraview 
for visualization. 

Instructions for downloading and installing Paraview_ can be found at 
http://www.paraview.org/download/ 

.. _Paraview: http://www.paraview.org

Using pydfnworks in your Python scripts
--------------------------------------------

To access the functionality of pydfnworks, the user must include the 
following line at the 
top of any Python script

.. code-block:: python
	
	import pydfnworks 

Before doing this, one needs to ensure that the pydfnworks directory is in the 
PYTHONPATH. This can be done by configuring ``cshrc`` or ``bashrc`` files. 
Alternatively, one can add the pydfnworks path using ``sys.path.append()`` 
in their driver script.

About this  manual
------------------

This manual comprises of information on setting up inputs to dfnGen, dfnTrans 
and PFLOTRAN, as well as details on the pydfnworks module: :ref:`pydfnworks 
<dfnWorks-python-chapter>`. Finally, the manual contains a short tutorial 
with prepared examples that  can be found in the ``tests`` directory of the 
dfnWorks repository, and a description of some applications of the dfnWorks 
suite.

Contributors
-------------
- Jeffrey Hyman
- Satish Karra
- Nataliia Makedonska
- Carl Gable
- Hari Viswanathan
- Matt Sweeney
- Shriram Srinivasan 
- Quan Bui (now at LLNL)
- Jeremy Harrod (now at Spectra Logic)
- Scott Painter (now at ORNL)
- Thomas Sherman (University of Notre Dame)

Contact
--------

For any questions about dfnWorks, please email dfnworks@lanl.gov.

Copyright information
----------------------

Documentation:

LA-UR-17-22216

Software copyright:

LA-CC-17-02


Contact Information : dfnworks@lanl.gov
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LA-CC-17-027

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(or copyright) 2018 Triad National Security, LLC. All rights reserved.
 
This program was produced under U.S. Government contract 89233218CNA000001
for Los Alamos National Laboratory (LANL), which is operated by Triad 
National Security, LLC for the U.S. Department of Energy/National Nuclear
Security Administration.
This is free software; you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3.0 of the License, or (at your option)
any later version. If software is modified to produce derivative works,
such modified software should be clearly marked, so as not to confuse it with
the version available from LANL.
All rights in the program are reserved by Triad National Security, LLC, 
and the U.S. Department of Energy/National Nuclear Security Administration.
The Government is granted for itself and others acting on its behalf a 
nonexclusive, paid-up, irrevocable worldwide license in this material 
to reproduce, prepare derivative works, distribute copies to the public,
perform publicly and display publicly, and to permit others to do so.
 
 The U.S. Government has rights to use, reproduce, and distribute this software.  
 NEITHER THE GOVERNMENT NOR TRIAD NATIONAL SECURITY, LLC MAKES ANY WARRANTY, 
 EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  
 If software is modified to  produce derivative works, such modified 
 software should be clearly marked, so as not to confuse it with the 
 version available from LANL.
Additionally, this program is free software; you can redistribute it and/or 
modify it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your option) 
any later version. Accordingly, this program is distributed in the hope that it 
will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
License for more details.
 
Additionally, redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following conditions are 
met:
1.       Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.
2.      Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in the 
documentation and/or other materials provided with the distribution.
3.      Neither the name of Los Alamos National Security, LLC, Los Alamos 
National Laboratory, LANL, the U.S. Government, nor the names of its 
contributors may be used to endorse or promote products derived from this 
software without specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY LOS ALAMOS NATIONAL SECURITY, LLC AND 
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A 
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL LOS ALAMOS NATIONAL 
SECURITY, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER 
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.

Additionally, this program is free software; you can redistribute it and/or 
modify it under the terms of the GNU General Public License as published by 
the Free Software Foundation; either version 2 of the License, or (at your 
option) any later version. Accordingly, this program is distributed in the 
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.


.. dfnWorks documentation master file, created by Satish Karra Oct 6, 2016
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

