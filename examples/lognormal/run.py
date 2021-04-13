#"""
#   :synopsis: run file for dfnworks 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""


from pydfnworks import * 

main_time = time()
DFN = create_dfn()
DFN.dfn_gen()
DFN.dfn_flow()
DFN.dfn_trans()
