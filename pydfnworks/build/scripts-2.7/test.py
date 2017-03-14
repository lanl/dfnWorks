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
    arg_string = os.environ['python_dfn'] + " run.py -ncpu 32 -name  " + name+ " -input " + input_file_name #+ " -large_network"
    print "RUNNING ", arg_string 
    subprocess.call(arg_string, shell=True)

if __name__ == '__main__':

    define_paths()
    benchmark_dir = os.environ['DFNWORKS_PATH'] + 'tests'
    subprocess.call('mkdir ~/test_output_files', shell=True)
    if len(sys.argv) == 2: 
        for input_file in os.listdir(benchmark_dir):
            if '.txt' in input_file:
                if sys.argv[1] in input_file:
                    input_file = benchmark_dir + '/' +  input_file 
                    run_test(input_file)
    
    elif len(sys.argv) == 1: 
        for input_file in os.listdir(benchmark_dir):
            if '.txt' in input_file:
                input_file = benchmark_dir + '/' +  input_file 
                run_test(input_file)
    else:
        print 'invalid arguments to test.py script.'
        print 'syntax: python test.py [TEST_NAME_PART]'
