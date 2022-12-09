#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

jobname = os.getcwd() + "/output"
dfnFlow_file = os.getcwd() + '/dfn_explicit.in'
dfnTrans_file = os.getcwd() + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [10.0, 10.0, 20.0]
DFN.params['domainSizeIncrease']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.1
DFN.params['boundaryFaces']['value'] = [0, 0, 0, 0, 1, 1]
# Create Layers in the DFN
# There are 2 layers
DFN.params['numOfLayers']['value'] = 2
# The bottom layer (layer #1) spans z in [-10,2]
# the top layer (layer #2) spans x in [-2,10]
# So the layers overlap from [-2, 2]
DFN.params['layers']['value'] = [[-10.0, 2.0], [-2.0, 10.0]]

# Add one family in layer #1  
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        probability=0.5,
                        layer=1,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.3,
                        min_radius=1.0,
                        max_radius=10.0,
                        p32=1,
                        hy_variable="transmissivity",
                        hy_function="constant",
                        hy_params={"mu": 6.3 * 10**-8})

# Add one family in layer #2
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=1.0,
                        probability=.25,
                        layer=2,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.6,
                        min_radius=1.0,
                        max_radius=10.0,
                        p32=2,
                        hy_variable="transmissivity",
                        hy_function="constant",
                        hy_params={"mu": 6.3 * 10**-9})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.print_domain_parameters()
DFN.create_network()
DFN.output_report()
DFN.mesh_network()
DFN.dfn_flow()
DFN.dfn_trans()

