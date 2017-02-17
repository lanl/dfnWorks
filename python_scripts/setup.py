#!/usr/bin/python
import sys
import os
import subprocess
import argparse
import glob


def command_line_options():
    '''Read command lines 
    -clean: True/False to clean 
    '''
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-clean", "--clean", default=False, action="store_true",
              help="Run make clean")
    options = parser.parse_args()
    return options
	
def remove_batch(name):
    """ Removes files with wild card *

    Args:
        name (string): the pattern attached to * which will be removed from the current working  directory 
    """

    print("Removing files:")
    for fl in glob.glob(name):
        print fl
        try:
	        os.remove(fl)
        except OSError:
            pass	

def compile_exe(directory_list):
        
    """ setup option - performs all compilations necessary before running run_dfnworks.py
    
    Args:
       directory_list (list): list of directory names which contain Makefiles
    """ 
    for directory in directory_list:
            print directory
            os.chdir(directory)
            subprocess.call("make")
            print("")

def clean(directory_list, python_dir):
    """      clean option - removes all files not needed in the repository
    
    Args:
       directory_list (list): list of directory names to be cleaned of object files
       python_dir (string): python directory name where *.pyc will be removed
    """
    for directory in directory_list:
        print directory
        os.chdir(directory)
        remove_batch("*.o")
        print ""
    os.chdir(python_dir)
    remove_batch("*pyc")


# 1. C_uge_correct - make
# 2. DFN_Mesh_Connectivity_Test - make
# 3. Particle Tracking - make
# 4. GenIntElmList - make
# 5. DFNGen - make

if __name__ == "__main__":

    options=command_line_options()

    DFN_PATH = '/home/nknapp/dfnworks-main/'
    C_UGE_PATH = DFN_PATH + 'C_uge_correct/'
    CONNECTIVITY_TEST_PATH = DFN_PATH + 'DFN_Mesh_Connectivity_Test/'
    PARTICLE_TRACKING_PATH = DFN_PATH +'ParticleTracking/'
    GEN_INT_ELM_LIST_PATH = DFN_PATH + 'GenIntElmtList/'
    DFNGEN_PATH = DFN_PATH +'DFNGen/DFNC++Version/'
    PYTHON_DIR = DFN_PATH + 'python_scripts/modules'

    directory_list = []
    directory_list.append(C_UGE_PATH)
    directory_list.append(CONNECTIVITY_TEST_PATH)
    directory_list.append(PARTICLE_TRACKING_PATH)
    directory_list.append(DFNGEN_PATH)
    directory_list.append(GEN_INT_ELM_LIST_PATH)

    if options.clean:
        print("Removing *.o and *.pyc files before compiling\n")
        clean(directory_list, PYTHON_DIR)	
        print("Compiling executables\n")
        compile_exe(directory_list)
    else:
        compile_exe(directory_list)
            
