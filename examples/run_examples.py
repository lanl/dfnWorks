import subprocess
import os
import glob
import shutil
import sys
import timeit
import pandas as pd


verbose = False

if not os.path.isdir('example_outputs'):
    os.mkdir('example_outputs')
else:
    shutil.rmtree('example_outputs')
    os.mkdir('example_outputs')

home = os.getcwd()


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
start_time = timeit.default_timer()

df = pd.DataFrame(columns=['Name', 'Pass/Fail', 'Time'])

for i,d in enumerate(examples_dirs):
    tmp = {"Name": d, "Passed/Fail": None, "Time (s)": None}
    sucess = None

    try:
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
        cleanup_dirs = glob.glob("output*")
        for d in cleanup_dirs:
            shutil.rmtree(d)
        os.chdir(home)
        #df_index = len(df) + 1
        #print(df_index, i)
        df.loc[i + 1,:] = [d, 'Pass', elapsed]
    except:
        print(f"--> {d} failed")
        df.loc[df_index,:] = [d, 'Fail', elapsed]
        os.chdir(home)

print(df)

final_time = timeit.default_timer()
total_time = final_time - start_time
print(f"* Total time for test suite {total_time:0.2f} seconds ({total_time/60:0.2f} minutes)")
