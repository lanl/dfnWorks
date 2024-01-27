#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *

jobname = os.getcwd() + "/output"

DFN = DFNWORKS(jobname, ncpu=8)

DFN.params['domainSize']['value'] = [20, 20, 20]
DFN.params['h']['value'] = 0.1
DFN.params['numOfRegions']['value'] = 1
DFN.params['regions']['value'] = [[-5, 5, -5, 5, -5, 5]]
DFN.params['domainSizeIncrease']['value'] = [2.0, 2.0, 2.0]
DFN.params['keepOnlyLargestCluster']['value'] = True

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=20.0,
                        aspect=1.0,
                        region=1,
                        beta_distribution=1,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        constant=1.0,
                        p32=2.0,
                        hy_variable='permeability',
                        hy_function="constant",
                        hy_params={"mu": 1e-12})

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=20.0,
                        aspect=1.0,
                        region=0,
                        beta_distribution=1,
                        beta=0.0,
                        theta=90.0,
                        phi=0.0,
                        constant=5.0,
                        p32=0.5,
                        hy_variable='permeability',
                        hy_function="constant",
                        hy_params={"mu": 2e-12})

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=20.0,
                        aspect=1.0,
                        region=0,
                        beta_distribution=1,
                        beta=0.0,
                        theta=45.0,
                        phi=135.0,
                        constant=5.0,
                        p32=0.5,
                        hy_variable='permeability',
                        hy_function="constant",
                        hy_params={"mu": 3e-12})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
DFN.output_report()
DFN.visual_mode = True
DFN.mesh_network()
