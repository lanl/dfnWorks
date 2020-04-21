import glob
import os
import subprocess

dirs = glob.glob("*")
cwd = os.getcwd()

fail = []
for d in dirs[:2]:
    if os.path.isdir(d):
        os.chdir(d)
        subprocess.call("bash notes.txt", shell=True)
        if not os.path.isfile(d+"_example/traj/partime"):
            fail.append(d)
        os.chdir(cwd)

print(fail)
