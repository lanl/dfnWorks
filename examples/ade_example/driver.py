#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname = f"{src_path}/output"
dfnFlow_file = f"{src_path}/dfn_explicit.in"
restart_file = f"{src_path}/dfn_restart.in"

DFN = DFNWORKS(jobname, dfnFlow_file=dfnFlow_file, ncpu=8)

DFN.params['domainSize']['value'] = [10, 10, 10]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 20
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['rejectsPerFracture']['value'] = 10
DFN.params['seed']['value'] = 1
DFN.params['keepIsolatedFractures']['value'] = True 


DFN.add_fracture_family(shape="rect",
                        distribution="exp",
                        probability=1.0,
                        kappa=1.0,
                        theta=0,
                        phi=0,
                        exp_mean=3.373,
                        min_radius=1.0,
                        max_radius=10.0,
                        hy_variable='permeability',
                        hy_function='log-normal',
                        hy_params={"mu": 1e-12,
                                   "sigma":0.4})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.print_domain_parameters()
DFN.set_flow_solver("PFLOTRAN")
DFN.create_network()
fracture_volume = DFN.aperture * DFN.surface_area

volume = DFN.params['domainSize']['value'][0] * DFN.params['domainSize']['value'][1] * DFN.params['domainSize']['value'][2]

p33 = fracture_volume.sum() / volume

print(p33)




# exit() 

# DFN.output_report() 
# DFN.mesh_network()


# exit() 

# DFN.lagrit2pflotran()
# DFN.pflotran(restart=True, restart_file=restart_file)
# DFN.parse_pflotran_vtk_python()
# DFN.pflotran_cleanup()
