import os
import sys
import subprocess

def run_test(input_file_name):
    """Run a single test.

    Args:
        input_file_name (str): The input file name for the test
    """

    name = '~/' +  input_file_name.rsplit('/', 1)[-1][:-4]
    arg_string = "python run.py -ncpu 32 -name  " + name+ " -input " + input_file_name + " -large_network"
    print "RUNNING ", arg_string 
    subprocess.call(arg_string, shell=True)

if __name__ == '__main__':
    home_dir = '/home/nknapp'
    benchmark_dir = home_dir +  '/dfnworks-main/tests/'
    benchmark_dir = os.path.abspath(benchmark_dir)
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
