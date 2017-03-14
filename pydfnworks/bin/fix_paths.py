# automatically changes path names in tests directory and pydfnworks

import subprocess
import sys

def replace(old, new):
    subprocess.call("find ./../ -type f -print0 | xargs -0 sed -i 's@" + old + "@" + new + "@g'", shell=True)
    subprocess.call("find ./../../tests/ -type f -print0 | xargs -0 sed -i 's@" + old + "@" + new + "@g'", shell=True)

old = sys.argv[1]
new = sys.argv[2]
replace(old, new)
