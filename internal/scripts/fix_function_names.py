import os, sys
import subprocess

def replace_capitals(line):
    
    capital_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
                'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 
                'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                'X', 'Y', 'Z']
    
    for capital in capital_list:
        line = line.replace(capital, '_' + capital.lower())
   
    return line

def get_function_list(file_name):
    f = open(file_name)
    function_list = []
    for line in f:
        if "def " in line:
            line = line.lstrip(' \t\n\r')
            function_name = line.split('(')[0][4:]
            function_list.append(function_name + '(')
    return function_list
    

py_dir = '/home/nknapp/dfnworks-main/pydfnworks/pydfnworks'
script_dir = '/home/nknapp/dfnworks-main/pydfnworks/bin'
dir_list = [py_dir, script_dir]

function_list = []
for dir in dir_list:
    for root, dirs, files in os.walk(os.path.abspath(py_dir)):
        for file in files:
            abs_path = os.path.join(root, file)
            function_list.append(get_function_list(abs_path))

function_list = sum(function_list, [])

for fxn in function_list:
    old = fxn
    new = replace_capitals(fxn)
    print 'replacing ', old 
    print 'with ', new
    subprocess.call("find " + py_dir + " -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)
    subprocess.call("find " + script_dir + " -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)


