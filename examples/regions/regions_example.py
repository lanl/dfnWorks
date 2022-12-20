#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

regions_example_path = os.getcwd()
jobname = regions_example_path + "/output"
dfnFlow_file = regions_example_path + '/dfn_explicit.in'
dfnTrans_file = regions_example_path + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [20, 20, 20]
DFN.params['h']['value'] = 0.05
DFN.params['domainSizeIncrease']['value'] = [2.0, 2.0, 2.0]
# Create a sub region in the center of the domain
DFN.params['numOfRegions']['value'] = 1
# size is 10 x 10 x 10 centered at 0,0,0
DFN.params['regions']['value'] = [[-5, 5, -5, 5, -5, 5]]
## ensure a connection from top to bottom
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [0, 0, 0, 0, 1, 1]

# Family 1 is created in the entire domain (region = 0)
DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=5.0,
                        aspect=1.0,
                        region=0,
                        beta_distribution=1,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        constant=5.0,
                        p32=1.0,
                        hy_variable='permeability',
                        hy_function="constant",
                        hy_params={"mu": 2e-12})

# Family 2 is created in the sub- domain (region = 1)
DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=5.0,
                        aspect=1.0,
                        region=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        constant=1.0,
                        p32=3.0,
                        hy_variable='permeability',
                        hy_function="constant",
                        hy_params={"mu": 1e-12})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.print_domain_parameters()
DFN.create_network()
DFN.mesh_network(min_dist=0.1, max_dist=10, slope=0.9)
DFN.dfn_flow()
DFN.dfn_trans()
