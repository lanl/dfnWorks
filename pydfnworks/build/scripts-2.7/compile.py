#!/n/swdev/packages/Ubuntu-14.04-x86_64/anaconda-python/2.4.1/bin/python
import sys
import os
import subprocess
import argparse
import glob
from pydfnworks import *

def command_line_options():
    """Read command lines 
    -clean: True/False to clean 
    -ncpus: number of CPUs to use for compilation
    """
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-clean", "--clean", default=False, action="store_true",
              help="Run make clean")
    parser.add_argument("-ncpus", "--ncpus", default=1, help="Run make using ncpus processors")
    parser.add_argument("-large_network", "--large_network", default=False, action="store_true",
              help="Set true to use CPP for file processing bottleneck. default=False")
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

def compile_exe(directory_list, options):
        
    """ setup option - performs all compilations necessary before running run_dfnworks.py
    
    Args:
       directory_list (list): list of directory names which contain Makefiles
    """ 
    for directory in directory_list:
            print directory
            os.chdir(directory)
            if options.ncpus > 1:
                subprocess.call("make -j" + str(options.ncpus), shell=True)
            else:
                subprocess.call("make", shell=True)
            print("")

def clean(directory_list, python_dir):
    """ clean option - removes all files not needed in the repository
    
    Args:
       directory_list (list): list of directory names to be cleaned of object files
       python_dir (str): python directory name where ``*.pyc`` will be removed
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
# 6. inp2vtk - make

if __name__ == "__main__":

    define_paths()
    options=command_line_options()

    directory_list = []
    directory_list.append(os.environ['correct_uge_PATH'])
    directory_list.append(os.environ['connect_test'])
    directory_list.append(os.environ['DFNTRANS_PATH'])
    directory_list.append(os.environ['DFNGEN_PATH'])
    if options.large_network:    
        directory_list.append(os.environ['VTK_PATH'])
        print("Using C++ to parse VTK files")
    if options.clean:
        print("Removing *.o and *.pyc files before compiling\n")
        clean(directory_list, PYTHON_DIR)	
        print("Compiling executables\n")
        compile_exe(directory_list, options)
    else:
        compile_exe(directory_list, options)
            
