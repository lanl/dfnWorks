#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""


from pydfnworks import * 

DFN = create_dfn()
# General Work Flow

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()

DFN.mesh_network(max_dist=100)

DFN.dfn_flow()
DFN.dfn_trans()
