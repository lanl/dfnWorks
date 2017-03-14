# automatically changes path names in tests directory and pydfnworks

import subprocess
import sys

def replace(old, new):
    subprocess.call("find ./../ -type f -print0 | xargs -0 sed -i 's/" + old + "/" + new + "/g'", shell=True)
    subprocess.call("find ./../../tests/ -type f -print0 | xargs -0 sed -i 's/" + old + "/" + new + "/g'", shell=True)

if (len(sys.argv) > 2):
    old = sys.argv[1]
    new = sys.argv[2]
else:
    old = '\/home\/nknapp'
    new = sys.argv[1]

replace(old, new)
