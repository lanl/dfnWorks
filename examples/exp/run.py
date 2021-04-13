#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""


from pydfnworks import * 

# General Work Flow
DFN = create_dfn()
DFN.dfn_gen(output=False)
DFN.dfn_flow()
DFN.dfn_trans()

