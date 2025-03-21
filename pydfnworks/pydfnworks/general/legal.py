from pydfnworks import *
import datetime


def legal(self):
    """Print the legal LANL statement for dfnWorks.

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    -------
        None

    Notes 
    ----
        None
    """
    lanl_statement = f'''
===================================================================
===================================================================
===================================================================
||\    _____         \               / ______  _______       /  \ 
||  \  |     |\     | \             /  |    |  |     | | /  /    \ 
||   \ |___  | \    |  \    /\     /   |    |  |_____| |/   |  |  |
||   / |     |   \  |   \  /  \  /     |    |  |   \   |\    \  \ 
||  /  |     |     \|    \/    \/      |____|  |    \  | \ |  |  |
||/ ======================================================= \    /
============================================================  \/
===================================================================

Program: pydfnWorks v{pydfnworks.__version__} 
Run time : {datetime.datetime.now()}

This program was prepared at Los Alamos National Laboratory (LANL),
Earth and Environmental Sciences Division, Computational Earth
Science Group (EES-16), Subsurface Flow and Transport Team.
All rights in the program are reserved by the DOE and LANL.
Permission is granted to the public to copy and use this software
without charge, provided that this Notice and any statement of
authorship are reproduced on all copies. Neither the U.S. Government
nor LANS makes any warranty, express or implied, or assumes
any liability or responsibility for the use of this software.

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
'''
    self.print_log(lanl_statement)
