#"""
#   :synopsis: Driver run file for TPL example 
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import * 
import os

jobname = os.getcwd() + "/tpl_obj_output"
DFN = DFNWORKS(jobname)
DFN_2 = DFNWORKS(jobname)
DFN.params['domainSize']['value'] = [10,10,10]
DFN.params["h"]["value"] = 0.1
exit(1)

DFN.add_fracture_family(shape = "rect", distribution = "constant", constant = 1, 
    kappa = 10, phi = 0, theta = 0, p32 = 1)

DFN.add_fracture_family(shape = "rect", distribution = "tpl", alpha = 3,
    min_radius = 1, max_radius = 10,
    kappa = 10, phi = 0, theta = 0, p32 = 4)
DFN.print_family_information(1)    
 
DFN.make_working_directory(delete = True)
DFN.check_input()

DFN.create_network()
# DFN.output_report()
# DFN.mesh_network(coarse_factor=10)
# DFN.dfn_flow()
# DFN.dfn_trans()
