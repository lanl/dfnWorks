#!/usr/bin/env python

import sys
import multiprocessing as mp
import subprocess

def spawn_dfn_job(d):
    jobname = d[0]
    ipfile = d[1]
    print("Running DFNTrans for " + jobname)
    logfile = "{}_trans.log".format(jobname)
    with open(logfile, "w+") as f:
        status = subprocess.call(["python", "/home/shrirams/dfnworks-main/pydfnworks/bin/run_trans.py", "-name", jobname, "-input", ipfile],stdout=f, stdin=f)
    print("DFNTrans for " + jobname + " complete\n")
    #return # <- return what?

jobs = sys.argv[2].split()
ipdir = sys.argv[1]

#jobname = 'job_%d/10_shortest'
#jobs = [jobname%i for i in range(1, 32)]
#print(jobs)


runs = []
data = []

for job in jobs:
    data.append([job, ipdir]) 

num_cpu = 32 
pool = mp.Pool(num_cpu)
pool.map(spawn_dfn_job, data)
pool.close()
pool.join()
pool.terminate()

