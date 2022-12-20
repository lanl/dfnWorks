Welcome To dfnWorks
=========================

dfnWorks is a parallelized computational suite to generate three-dimensional 
discrete fracture networks (DFN) and simulate flow and transport. Developed at 
Los Alamos National Laboratory, it has been used to study flow and transport 
in fractured media at scales ranging from millimeters to kilometers. The 
networks are created and meshed using dfnGen, which combines FRAM (the feature 
rejection algorithm for meshing) methodology to stochastically generate 
three-dimensional DFNs with the LaGriT meshing toolbox to create a high-quality 
computational mesh representation. The representation produces a conforming 
Delaunay triangulation suitable for high-performance computing finite volume 
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


Obtaining dfnWorks
---------------------------
dfnWorks can be downloaded from https://hub.docker.com/r/ees16/dfnworks 

dfnWorks can be downloaded from https://github.com/lanl/dfnWorks/

v1.0 can be downloaded from https://github.com/dfnWorks/dfnWorks-Version1.0  


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

Versions
-------------------
v2.
^^^^^^^^^^^^^^^^^^^^^^^^

- Hydraulic aperture of fracture based on background stress field
- Bug fixes


v2.5
^^^^^^^^^^^^^^^^^^^^^^^^

- New Generation parameters, family orientation by trend/plunge and dip/strike
- Define fracture families by region
- Updated output report


v2.4
^^^^^^^^^^^^^^^^^^^^^^^^

- New meshing technique (Poisson disc sampling)
- Define fracture families by region
- Updated output report
- Well Package

v2.3
^^^^^^^^^^^^^^^^^^^^^^^^

- Bug fixes in LaGrit Meshing 
- Bug fixes in dfnTrans checking
- Bug fixes in dfnTrans output
- Expanded examples
- Added PDF printing abilities
 

v2.3
^^^^^^^^^^^^^^^^^^^^^^^^

- pydfnWorks updated for python3
- Graph based (pipe-network approximations) for flow and transport
- Bug fixes in LaGrit Meshing 
- Increased functionalities in pydfnworks including the path option
- dfn2graph capabilities
- FEHM flow solver
- Streamline routing option in dfnTrans 
- Time Domain Random Walk in dfnTrans

v2.1
^^^^^^^^^^^^^^^^^^^^^^^^

- Bug fixes in LaGrit Meshing 
- Increased functionalities in pydfnworks including the path option

v2.0
^^^^^^^^^^^^^^^^^^^^^^^^

- New dfnGen C++ code which is much faster than the Mathematica dfnGen. This code has successfully generated networks with 350,000+ fractures. 
- Increased functionality in the pydfnworks package for more streamlined workflow from dfnGen through visualization. 


About this  manual
------------------

This manual comprises of information on setting up inputs to dfnGen, dfnTrans 
and PFLOTRAN, as well as details on the pydfnworks module: :ref:`pydfnworks 
<dfnWorks-python-chapter>`. Finally, the manual contains a short tutorial 
with prepared examples that  can be found in the ``examples`` directory of the 
dfnWorks repository, and a description of some applications of the dfnWorks 
suite.

Contact
--------

Please email dfnworks@lanl.gov with questions about dfnWorks. Please let us know if you publish using dfnWorks and we'll add it to the :ref:`Publication Page <publications-chapter>`

Contributors
-------------
LANL
^^^^^^^
- Jeffrey D. Hyman
- Satish Karra
- Nataliia Makedonska
- Carl Gable
- Hari Viswanathan
- Matt Sweeney
- Shriram Srinivasan 
- Aric Hagberg
- Yu Chen

External
^^^^^^^^^^^^^^
- Quan Bui (now at LLNL)
- Jeremy Harrod (now at Spectra Logic)
- Scott Painter (now at ORNL)
- Thomas Sherman (University of Notre Dame)
- Johannes Krotz  (Oregon State University)


Copyright Information
----------------------

Documentation:

LA-UR-17-22216

Software copyright:

LA-CC-17-027

Contact Information : dfnworks@lanl.gov

(or copyright) 2018 Triad National Security, LLC. All rights reserved.
 
This program was produced under U.S. Government contract 89233218CNA000001
for Los Alamos National Laboratory (LANL), which is operated by Triad 
National Security, LLC for the U.S. Department of Energy/National Nuclear
Security Administration.
 
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

