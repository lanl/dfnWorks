# Use this script to test the code before merging. Do not merge if any of the tests are not passed

#!/usr/bin/python
import sys
import os
import subprocess

# define all path names here
dfn_dir = '/home/nknapp/dfnworks-main/'
python_dir = dfn_dir + 'python_scripts/'
input_dir = dfn_dir + 'sample_inputs/'
four_rect_name = python_dir + 'input_text.txt'
TSA_name = input_dir + 'TSA/TSA_test.dat'

def print_result(test_name, result):
	print test_name, " ", result

def run_test(input_file_name):
	arg_string = "python run_dfnworks.py -name " + input_file_name[:-4] + " -input " + input_file_name
	subprocess.call(arg_string, shell=True)

test_list = []
test_list.append(four_rect_name)
#test_list.append(TSA_name)

result_list = []
for test_name in test_list:
	result = run_test(test_name)
	print_result(test_name, result)
	result_list.append(result)

if "FAILED" in result_list:
	print "At least one test failed. Do not merge."



