import os, sys
import subprocess

dir_list = []
source_path = '/home/nknapp/dfnworks-main/pydfnworks/pydfnworks'
script_path = '/home/nknapp/dfnworks-main/pydfnworks/bin'
test_path = '/home/nknapp/dfnworks-main/tests'

dir_list.append(script_path)
dir_list.append(source_path)
dir_list.append(test_path)

old = sys.argv[1]
new = sys.argv[2]

for dir in dir_list:
    subprocess.call("find " + dir + " -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)


