#!/usr/bin/python
import sys
import os
import subprocess

# setup option - performs all compilations necessary before running run_dfnworks.py
def compile(make_directory_list):
        for directory in make_directory_list:
                os.chdir(directory)
                subprocess.call("make")

# clean option - removes all files not needed in the repository
def clean(make_directory_list, python_dir):
        for directory in make_directory_list:
                print directory
                os.chdir(directory)
                subprocess.call("rm *.o")
        os.chdir(python_dir)
        subprocess.call("rm -rf *~")
        subprocess.call("rm -rf *.pyc")

# 1. C_uge_correct - make
# 2. DFN_Mesh_Connectivity_Test - make
# 3. Particle Tracking - make
# 4. GenIntElmList - make

DFN_PATH = '/home/nknapp/dfnworks-main/'
C_UGE_PATH = DFN_PATH + 'C_uge_correct/'
CONNECTIVITY_TEST_PATH = DFN_PATH + 'DFN_Mesh_Connectivity_Test/'
PARTICLE_TRACKING_PATH = DFN_PATH +'ParticleTracking/'
GEN_INT_ELM_LIST_PATH = DFN_PATH + 'GenIntElmtList/'
PYTHON_DIR = DFN_PATH + 'python_scripts/'

make_directory_list = []
make_directory_list.append(C_UGE_PATH)
make_directory_list.append(CONNECTIVITY_TEST_PATH)
make_directory_list.append(PARTICLE_TRACKING_PATH)
make_directory_list.append(GEN_INT_ELM_LIST_PATH)


#clean(make_directory_list, PYTHON_DIR)
if (len(sys.argv) == 1):
	compile(make_directory_list)
else:
	print 'Invalid arguments to setup script.'
	
