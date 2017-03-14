# automatically changes path names in tests directory and pydfnworks

import subprocess

def replace(old, new):
    subprocess.call('find ./../ -type f -print0 | xargs -0 sed -i \'s/' + old + '/' + new + '/g\'', shell=True)
    subprocess.call('find ./../../tests/ -type f -print0 | xargs -0 sed -i \'/' + old + '/' + new + '/g\'', shell=True)

old = '\/home\/nknapp'
new = 'LOUIS_THE_CHILD'

replace(old, new)
