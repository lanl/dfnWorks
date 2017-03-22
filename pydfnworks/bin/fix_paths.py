# automatically changes path names in tests directory and pydfnworks

import subprocess
import sys, os

def replace(old, new):
    subprocess.call("find ./../ -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)
    subprocess.call("find ./../../tests/ -type f -print0 | xargs -0 sed -i -e 's@" + old + "@" + new + "@g'", shell=True)

old = '/home/nknapp/'
new = os.getcwd().split('dfnWorks-Version2.0')[0]
replace(old, new)
