#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""


from pydfnworks import * 

DFN = create_dfn()
# General Work Flow
DFN.dfn_gen(from_file = True)
DFN.dfn_flow()
DFN.dfn_trans()
