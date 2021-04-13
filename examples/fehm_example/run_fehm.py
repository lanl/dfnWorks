"""
.. file:: run_fehm.py
   :synopsis: run file for dfnWorks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

from pydfnworks import * 

main_time = time()
DFN = create_dfn()

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()

# Run FEHM
DFN.set_flow_solver("FEHM")
DFN.mesh_network()
DFN.correct_stor_file()
DFN.fehm()

print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)

