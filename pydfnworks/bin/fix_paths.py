# automatically changes path names in tests directory and pydfnworks

import subprocess

def replace(old, new):
    subprocess.call("find ./../ -type f -print0 | xargs -0 sed -i 's/" + old + "/" + new + "/g'", shell=True)
    subprocess.call("find ./../../tests/ -type f -print0 | xargs -0 sed -i 's/" + old + "/" + new + "/g'", shell=True)

old = '\/home\/nknapp\/dfnworks-main'
new = '\/home\/nknapp\/dfnWorks-Version2.0'

replace(old, new)
