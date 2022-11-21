#"""
#   :synopsis: run file for TPL example
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname = f"{src_path}/output"
pflotran_file = f"{src_path}/dfn_explicit.in"
dfntrans = f"{src_path}/PTDFN_control.in"

DFN = DFNWORKS(jobname, dfnFlow_file=pflotran_file, ncpu=8)

DFN.params['domainSize']['value'] = [100, 200, 50]
DFN.params['domainSizeIncrease']['value'] = [10, 10, 10]
DFN.params['h']['value'] = 0.5
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = True
DFN.params['seed']['value'] = 1

DFN.params['polygonBoundaryFlag']['value'] = True
DFN.params['polygonBoundaryFile']['value'] = f"{src_path}/vertices.dat"

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=2.2,
                        min_radius=5.0,
                        max_radius=25.0,
                        kappa=0.1,
                        theta=0.0,
                        phi=0.0,
                        aspect=2,
                        beta_distribution=1,
                        beta=45.0,
                        p32=0.55,
                        number_of_points=16,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })

DFN.print_domain_parameters()
DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
DFN.mesh_network(min_dist=0.1, max_dist=100, slope=0.9)
DFN.dfn_flow()
