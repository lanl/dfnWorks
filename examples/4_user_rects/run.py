#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

import os, sys
from time import time
from pydfnworks import * 


define_paths()
main_time = time()
DFN = create_dfn()
# General Work Flow
DFN.set_flow_solver("FEHM")
DFN.dfn_gen(output=False)
#DFN.dfn_flow()
#DFN.dfn_trans()

main_elapsed = time() - main_time
print('Time Required: %0.2f Minutes'%(main_elapsed/60.0))
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)

