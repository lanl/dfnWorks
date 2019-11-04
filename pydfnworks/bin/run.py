#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman, Carl Gable, Nathaniel Knapp
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

import os, sys
from time import time
from pydfnworks import * 
import subprocess

if __name__ == "__main__":

    define_paths()
    main_time = time()
    print('Compiling executables')
#    subprocess.call(os.environ['PYTHON_EXE'] + ' compile.py', shell=True)  
    DFN = create_dfn()
    if type(DFN) is ' NoneType':
        print('ERROR: DFN object not created correctly')
        exit(1)
    # General Work Flow
    DFN.dfn_gen(output=False)
    DFN.dfn_flow()
    DFN.dfn_trans()

    main_elapsed = time() - main_time
    timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
    DFN.dump_time("Total run time",main_elapsed)
    #dfn.print_run_time()	
    print("*"*80)
    print(DFN.jobname+' complete')
    print("Thank you for using dfnWorks")
    print("*"*80)

