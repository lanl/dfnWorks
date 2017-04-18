# automatically changes path names in tests directory and pydfnworks

import subprocess
import sys, os

def replace(old, new):
    subprocess.call("find ../../tests/ -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)
    subprocess.call("find ../pydfnworks/ -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)

old = '/home/nknapp'
new = 'DUMMY'
#new = os.getcwd().split('/dfnworks-main')[0]
replace(old, new)
