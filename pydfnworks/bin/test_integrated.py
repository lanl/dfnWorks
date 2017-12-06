import os
import sys
import subprocess
from pydfnworks import *

def run_test(input_file_name):
    """Run a single test.

    Args:
        input_file_name (str): The input file name for the test
    """
    
    name = '~/' + 'test_output_files/' + input_file_name.rsplit('/', 1)[-1][:-4]
    arg_string = os.environ['python_dfn'] + " run.py -ncpu 32 -name  " + name+ " -input " + input_file_name 
    print "RUNNING ", arg_string 
    subprocess.call(arg_string, shell=True)

if __name__ == '__main__':

    define_paths()
    os.system(os.environ['python_dfn'] + ' create_test_run_scripts.py ' + os.environ['dfnworks_PATH'] + 'tests/integrated_test/')
    print os.environ['python_dfn'] + ' create_test_run_scripts.py ' + os.environ['dfnworks_PATH'] + 'tests/integrated_test/'
    run_test(os.environ['dfnworks_PATH'] + 'tests/integrated_test/integrated.txt')
