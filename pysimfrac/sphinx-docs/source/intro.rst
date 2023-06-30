.. _simfrac-intro:

.. pySimFrac documentation master file, created by Jeffrey Hyman 7 July 2022
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to pySimFrac documentation
=======================================

.. figure:: figures/surface.png
   :alt: Figure Not Found
   :align: center
    
What is pySimFrac?
--------------------------
pySimFrac is a Python module for constructing 3D single fracture geometries. The software is designed to help researchers investigate flow through fractures using direct numerical simulations of single/multi phase flow. One advantage of the Python implementation is that it allows for greater flexibility and customization compared to a GUI-based approach. With a Python-based interface, researchers can readily expand their development and test new fracture generation algorithms or modify existing methods to better match experimental data. pySimFrac offers spectral-based and convolution-based generation methods. pySimFrac also includes utilities for characterizing fracture properties such as the correlation length, moments, and probability density function of the fracture surfaces and aperture field. 

    
What can pySimFrac do?
--------------------------

pySimFrac not only excels in fracture geometry generation but also ensures seamless integration with open-source flow simulation libraries, elevating its utility for researchers. This ease of integration streamlines the process of conducting direct numerical simulations of single/multi-phase flow through fractures, fostering a comprehensive understanding of fluid dynamics within these complex structures. By providing built-in compatibility with popular open-source simulators, pySimFrac eliminates the need for time-consuming and error-prone manual configuration, allowing users to focus on their research objectives. The library's robust and extensible design caters to a wide array of applications, accommodating users with varying requirements and expertise. Ultimately, pySimFrac's integration with flow simulation libraries further enhances its value as a tool for investigating fracture flow behavior, contributing significantly to advancements in subsurface hydrology, reservoir engineering, and environmental studies.


Contributors
-------------
- Eric Joseph Guiltinan
- Prakash Purswani
- Javier Estrada Santos
- Jeffrey D. Hyman


Contact
----------------------

- Email: simfrac@lanl.gov  
- Please post issues on the github issues page


Copyright Information
----------------------

Triad National Security, LLC. All rights reserved.
 
This program was produced under U.S. Government contract 89233218CNA000001for Los Alamos National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S. Department of Energy/National NuclearSecurity Administration.
 
All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear Security Administration.The Government is granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute copies to the public,perform publicly and display publicly, and to permit others to do so.

The U.S. Government has rights to use, reproduce, and distribute this software.   NEITHER THE GOVERNMENT NOR TRIAD NATIONAL SECURITY, LLC MAKES ANY WARRANTY,EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE. If software is modified to  produce derivative works, such modified software should be clearly marked, so as not to confuse it with the version available from LANL.

Additionally, this program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. Accordingly, this program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 
Additionally, redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following conditions are met

   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

   3. Neither the name of Los Alamos National Security, LLC, Los Alamos National Laboratory, LANL, the U.S. Government, nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY LOS ALAMOS NATIONAL SECURITY, LLC AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL LOS ALAMOS NATIONAL SECURITY, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Additionally, this program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. Accordingly, this program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.




