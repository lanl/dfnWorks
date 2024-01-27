import subprocess
import os
import glob
import shutil
import sys
import timeit

verbose = False

if not os.path.isdir('example_outputs'):
    os.mkdir('example_outputs')
else:
    shutil.rmtree('example_outputs')
    os.mkdir('example_outputs')

home = os.getcwd()
passed = []
failed = []
times = []

try:
    examples_dirs = [sys.argv[1]]
except:
    examples_dirs = glob.glob("*")
    for d in examples_dirs:
        if not os.path.isdir(d):
            examples_dirs.remove(d)
    examples_dirs.remove('example_outputs')
    examples_dirs.sort()

print(examples_dirs)

for d in examples_dirs:
    print(d)
    os.chdir(d)
    driver_file = glob.glob("*py")
    if verbose:
        cmd = f"python {driver_file[0]}"
    else:
        cmd = f"python {driver_file[0]} > {home}/example_outputs/{d}.out"
    print(cmd)
    tic = timeit.default_timer()
    subprocess.call(cmd, shell=True)
    toc = timeit.default_timer()
    elapsed = toc - tic
    print(f"--> Time required {elapsed:0.2f} seconds\n")
    passed.append([d, elapsed])
    cleanup_dirs = glob.glob("output*")
    for d in cleanup_dirs:
        shutil.rmtree(d)
    os.chdir(home)
    # except:
    #     print(f"--> {d} failed")
    #     failed.append(d)
    #     os.chdir(home)

print(passed)
print(failed)
print(times)
