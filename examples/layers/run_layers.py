"""
.. file:: run_layers.py
   :synopsis: run file for layer example 
   :version: 1.0
   :maintainer: Jeffrey Hyman
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os, sys
from time import time
from pydfnworks import * 
import subprocess

define_paths()
main_time = time()
DFN = create_dfn()

DFN.make_working_directory()
## dfnGen
DFN.check_input()
DFN.create_network()
DFN.output_report()
DFN.mesh_network()

# assign hydraulic properties by family, which depends on layer
variable = "transmissivity"
function = "correlated"
params = {"alpha":6.7*10**-7,"beta":1.4}
b1,perm1,T1 = DFN.generate_hydraulic_values(variable,function,params,family_id=1)

function = "semi-correlated"
params = {"alpha":6.3*10**-7,"beta":0.5,"sigma":1.0}
b2,perm2,T2 = DFN.generate_hydraulic_values(variable,function,params,family_id=2)

function = "constant"
params = {"mu":6.3*10**-9}
b3,perm3,T3 = DFN.generate_hydraulic_values(variable,function,params,family_id=3)

function = "log-normal"
params = {"mu":6.3*10**-9,"sigma":0.5}
b4,perm4,T4 = DFN.generate_hydraulic_values(variable,function,params,family_id=4)

T = T1 + T2 + T2 + T4
b = b1 + b2 + b3 + b4
perm = perm1 + perm2 + perm3 + perm4 
DFN.dump_hydraulic_values(b,perm,T)

##dfnFlow()
DFN.lagrit2pflotran()
DFN.pflotran()
DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()

# dfnTrans
DFN.copy_dfn_trans_files()
DFN.check_dfn_trans_run_files()
DFN.run_dfn_trans()

print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
