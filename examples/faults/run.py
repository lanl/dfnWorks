#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import * 


define_paths()
main_time = time()
DFN = create_dfn()

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network(visual_mode = True)