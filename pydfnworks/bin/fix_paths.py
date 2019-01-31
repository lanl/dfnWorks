# automatically changes path names in tests directory and pydfnworks

import subprocess
import sys, os

def replace(old, new):
    subprocess.call("find ../ -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)
    subprocess.call("find ../../examples -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)

old = 'DUMMY/'
 
dir_name = os.getcwd().split('/')
n = len(dir_name)
new = ''
for i in range(n-3):
    new += dir_name[i]+'/'

print 'replacing ', old, ' with ', new 
replace(old, new)
