import os
import sys
import subprocess

def run_test(input_file_name):
    """Run a single test.

    Args:
        input_file_name (str): The input file name for the test
    """

    name = '~/' +  input_file_name.rsplit('/', 1)[-1][:-4]
    arg_string = "python run_dfnworks.py -ncpu 32 -name  " + name+ " -input " + input_file_name
    print "RUNNING ", arg_string 
    subprocess.call(arg_string, shell=True)

if __name__ == '__main__':
    home_dir = '/home/nknapp'
    benchmark_dir = home_dir +  '/dfnworks-main/benchmarks/'
    benchmark_dir = os.path.abspath(benchmark_dir)
    for input_file in os.listdir(benchmark_dir):
        input_file = benchmark_dir + '/' +  input_file 
        if "ell" not in input_file and "rect" in input_file: 
            run_test(input_file)
