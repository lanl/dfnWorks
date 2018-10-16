import os
import sys
import re
import argparse
import subprocess

def move_files(file_list, dir_name):
    os.mkdir(dir_name) 
    for fle in os.listdir(os.getcwd()):
        for name in file_list:
            if name in fle:
                subprocess.call('mv ' + fle + ' ' + dir_name, shell=True)
def commandline_options():
    """Read command lines for use in dfnWorks.
    
    Options:
        * -name : Jobname (Mandatory)
        * -ncpu : Number of CPUS (Optional, default=4)
        * -input : input file with paths to run files (Mandatory if the next three options are not specified)
        * -gen   : Generator Input File (Mandatory, can be included within this file)
        * -flow  : PFLORAN Input File (Mandatory, can be included within this file)
        * -trans : Transport Input File (Mandatory, can be included within this file)
        * -prune : Prune Input File 
        * -path  : Prune Path 
        * -cell: True/False Set True for use with cell based aperture and permeabuility (Optional, default=False)
    """
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-name", "--jobname", default="", type=str,
              help="jobname") 
    parser.add_argument("-ncpu", "--ncpu", default=4, type=int, 
              help="Number of CPUs")
    parser.add_argument("-input", "--input_file", default="", type=str,
              help="input file with paths to run files") 
    parser.add_argument("-gen", "--dfnGen", default="", type=str,
              help="Path to dfnGen run file") 
    parser.add_argument("-flow", "--dfnFlow", default="", type=str,
              help="Path to dfnFlow run file") 
    parser.add_argument("-trans", "--dfnTrans", default="", type=str,
              help="Path to dfnTrans run file") 
    parser.add_argument("-path", "--path", default="", type=str,
              help="Path to directory for sub-network runs") 
    parser.add_argument("-cell", "--cell", default=False, action="store_true",
              help="Binary For Cell Based Apereture / Perm")
    parser.add_argument("-prune_file", "--prune_file", default="", type=str, 
              help="Path to prune DFN list file") 
    parser.add_argument("-prune_path", "--prune_path", default="", type=str, 
              help="Path to original DFN files") 
    options = parser.parse_args()
#    if options.jobname is "":
#        sys.exit("Error: Jobname is required. Exiting.")
    return options


def dump_time(local_jobname, section_name, time):
    '''dump_time
    keeps log of cpu run time, current formulation is not robust
    '''
    if (os.path.isfile(local_jobname+"_run_time.txt") is False):    
        f = open(local_jobname+"_run_time.txt", "w")
        f.write("Runs times for " + local_jobname + "\n")
    else:
        f = open(local_jobname+"_run_time.txt", "a")
    if time < 60.0:
        line = section_name + " :  %f seconds\n"%time
    else:
        line = section_name + " :  %f minutes\n"%(time/60.0)
    f.write(line)
    f.close()

def print_run_time(local_jobname):
    '''print_run_time
    Read in run times from file and and print to screen with percentages
    '''
    f=open(local_jobname+"_run_time.txt").readlines()
    unit = f[-1].split()[-1]
    total = float(f[-1].split()[-2])
    if unit is 'minutes':
        total *= 60.0

    print 'Runs times for ', f[0]
    percent = []
    name = []
    for i in range(1,len(f)):
        unit = f[i].split()[-1]
        time = float(f[i].split()[-2])

        if unit is 'minutes':
            time *= 60.0
        percent.append(100.0*(time/total))
        name.append(f[i].split(':')[1])
        print f[i], '\t--> Percent if total %0.2f \n'%percent[i-1]
    print("Primary Function Percentages")

    for i in range(1,len(f) - 1):
        if name[i-1] == ' dfnGen ' or name[i-1] == ' dfnFlow ' or name[i-1] == ' dfnTrans ':
            print(name[i-1]+"\t"+"*"*int(percent[i-1]))
    print("\n")

def get_num_frac():
    """ Get the number of fractures from the params.txt file.
    """
    try: 
        f = open('params.txt')
        _num_frac = int(f.readline())
        f.close()
    except:
        print '-->ERROR getting number of fractures, no params.txt file'

