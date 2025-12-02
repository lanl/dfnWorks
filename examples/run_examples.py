import subprocess
import os
import glob
import shutil
import sys
import timeit
import pandas as pd


verbose = True 
# verbose = False 

if not os.path.isdir('example_outputs'):
    os.mkdir('example_outputs')
else:
    shutil.rmtree('example_outputs')
    os.mkdir('example_outputs')

home = os.getcwd()

try:
    examples_dirs = [sys.argv[1]]
    verbose = True
except:
    examples_dirs = glob.glob("*")
    for d in examples_dirs:
        if not os.path.isdir(d):
            examples_dirs.remove(d)
    examples_dirs.remove('example_outputs')
    examples_dirs.sort()

print(examples_dirs)

start_time = timeit.default_timer()

df = pd.DataFrame(columns=['Name', 'Pass/Fail', 'Time', 'Error'])

for i,d in enumerate(examples_dirs):
    tmp = {"Name": d, "Passed/Fail": None, "Time (s)": None}
    sucess = None

    try:
        print(d)
        os.chdir(d)
        if os.path.isdir('output'):
            shutil.rmtree('output')
            #print(f"--> Removing output directory from {d}")
        if os.path.isfile('output.log'):
            os.remove('output.log')
            #print(f"--> Removing output.log file from {d}")
        driver_file = glob.glob("driver.py")
        if verbose:
            cmd = f"python3.11 {driver_file[0]}"
        else:
            cmd = f"python3.11 {driver_file[0]} > {home}/example_outputs/{d}.out"
        print(cmd)
        tic = timeit.default_timer()
        subprocess.call(cmd, shell=True)
        toc = timeit.default_timer()
        elapsed = toc - tic
        print(f"--> Time required {elapsed:0.2f} seconds\n")
        #print(f"--> Cleaning up outputs")
        if os.path.isdir('output'):
            shutil.rmtree('output')
            #print(f"--> Removing output directory from {d}")
        if os.path.isfile('output.log'):
            os.remove('output.log')
            #print(f"--> Removing output.log file from {d}")
        os.chdir(home)
        #df_index = len(df) + 1
        #print(df_index, i)
        df.loc[i + 1, :] = [d, 'Pass', elapsed, None]

    except Exception as error:
        print(f"--> {d} failed")
        print(f"--> error {error}")
        df.loc[i+1,:] = [d, 'Fail', elapsed, error]
        os.chdir(home)

print(df)

final_time = timeit.default_timer()
total_time = final_time - start_time
print(f"* Total time for test suite {total_time:0.2f} seconds ({total_time/60:0.2f} minutes)")
