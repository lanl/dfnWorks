import os, sys, time
from dfnWorks import *
import dfnGen_meshing as mesh


def define_paths():
	# Set Environment Variables
	os.environ['PETSC_DIR']='/home/satkarra/src/petsc-git/petsc-3.7-release'
	os.environ['PETSC_ARCH']='/Ubuntu-14.04-nodebug'
	os.environ['PFLOTRAN_DIR']='/home/satkarra/src/pflotran-dev-Ubuntu-14.04'

	os.environ['DFNGENC_PATH']='/home/jhyman/dfnworks/DFNGen/DFNC++Version'
	os.environ['DFNWORKS_PATH'] = '/home/jhyman/dfnworks/dfnworks-main/'
	os.environ['DFNTRANS_PATH']= os.environ['DFNWORKS_PATH'] +'ParticleTracking/'
	#os.environ['DFNTRANS_PATH']= '/home/nataliia/DFNWorks_UBUNTU/DFNTrans2.0/'

	# Executables	
	os.environ['python_dfn'] = '/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python'
	os.environ['lagrit_dfn'] = '/n/swdev/LAGRIT/bin/lagrit_ulin3.2'

	os.environ['connect_test'] = os.environ['DFNWORKS_PATH']+'/DFN_Mesh_Connectivity_Test/ConnectivityTest'
	os.environ['correct_uge_PATH'] = os.environ['DFNWORKS_PATH']+'/C_uge_correct/correct_uge' 
	
	#os.environ['PYLAGRIT']='/home/jhyman/pylagrit/src'
	#os.system('module load pylagrit/june_8_2015')


lanl_statement = '''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~ Program: DFNWorks  V2.0 ~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Copyright (c) 2016, Los Alamos National Security, LLC
All rights reserved.
Copyright 2016. Los Alamos National Security, LLC. This software was produced 
under U.S. Government contract DE-AC52-06NA25396 for Los Alamos National 
Laboratory (LANL), which is operated by Los Alamos National Security, LLC for 
the U.S. Department of Energy. The U.S. Government has rights to use, reproduce,
 and distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL 
SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY 
FOR THE USE OF THIS SOFTWARE.  If software is modified to produce derivative 
works, such modified software should be clearly marked, so as not to confuse it
 with the version available from LANL.
 
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
 

print ('='*80)
print lanl_statement
print ('='*80)
os.system("date")
define_paths()

# 4 fracture test
#dfnGen_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/4_fracture_test/input_4_fracture.dat'	
#dfnFlow_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/4_fracture_test/dfn_explicit.in'	
#dfnTrans_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/4_fracture_test/PTDFN_control.dat'	
#

# USER INPUT FILES, ALL PATHS MUST BE VALID	
#dfnGen_run_file = '/home/jhyman/dfnworks/dfnworks-main/sample_inputs/1L_network.dat'	
#dfnGen_run_file = '/home/jhyman/dfnworks/dfnworks-main/sample_inputs/multi_rect.dat'	
#dfnGen_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/4_fracture_test/input_4_fracture.dat'	
#dfnGen_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/simple_pl/pl_test.dat'	
#dfnFlow_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/simple_pl/dfn_explicit.in'
#dfnTrans_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/simple_pl/PTDFN_control.dat'	
#
dfnGen_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/CGU_networks/pl_test.dat'	
dfnFlow_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/simple_pl/dfn_explicit.in'	
dfnTrans_run_file = os.environ['DFNWORKS_PATH']+'sample_inputs/simple_pl/PTDFN_control.dat'	
#dfnFlow_run_file = '/scratch/fe/jhyman/dfnWorks/2016-marco/fors15_115/dfn_explicit.in'	




main_time = time()
# Command lines: argv[1] = jobname, argv[2] = number of cpus. 
# Command line is overloaded, so argv[3], argv[4], argv[5] 
# can be dfnGen, dfnFlow, and dfnTrans control files. 
# They need to be the FULL path name
try: 
	jobname = sys.argv[1]
	ncpu = int(sys.argv[2])
except:
	print 'Not enough input parameters'
	print 'Usage:', sys.argv[0], '[jobname][nCPU]'; sys.exit(1)

if len(sys.argv) == 4:
	dfnGen_run_file = sys.argv[3] 
elif len(sys.argv) == 5:
	dfnGen_run_file = sys.argv[3] 
	dfnFlow_run_file = sys.argv[4] 
elif len(sys.argv) == 6:
	dfnGen_run_file = sys.argv[3] 
	dfnFlow_run_file = sys.argv[4] 
	dfnTrans_run_file = sys.argv[5] 

# Create DFN object
dfn = dfnworks(jobname = jobname, input_file = dfnGen_run_file, ncpu = ncpu, pflotran_file = dfnFlow_run_file, dfnTrans_file = dfnTrans_run_file)

print 'Running Job: ', jobname
print 'Number of cpus requested: ', ncpu 
print '--> dfnGen input file: ',dfnGen_run_file
print '--> dfnFlow input file: ',dfnFlow_run_file
print '--> dfnTrans input file: ',dfnTrans_run_file
print ''




#dfn.make_working_directory()
#dfn.check_input()

dfn.dfnGen()
dfn.dfnFlow()
dfn.dfnTrans()
#os.chdir(dfn._jobname)
#mesh.cleanup_dir()


# possible commands
#dfn.make_working_directory()
#dfn.check_input()
#dfn.create_network()   
#dfn.output_report()
#dfn.dfnFlow()
#dfn.dfnTrans()

main_elapsed = time() - main_time
print jobname, 'Complete'
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
print timing
dfn.dumpTime(dfn._jobname,main_elapsed) 
dfn.runTime()	

