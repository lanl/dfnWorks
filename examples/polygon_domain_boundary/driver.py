#"""
#   :synopsis: run file for TPL example 
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import * 
import os

jobname = os.getcwd() + "/output"
pflotran_file = os.getcwd() + "/dfn_explicit.in"
dfntrans = os.getcwd() + "/PTDFN_control.in"

DFN = DFNWORKS(jobname,dfnFlow_file = pflotran_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [100, 200, 50]
DFN.params['domainSizeIncrease']['value'] = [10,20,10]
DFN.params['h']['value'] = 0.5
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = True
DFN.params['seed']['value'] = 1

DFN.params['polygonBoundaryFlag']['value'] = True
DFN.params['polygonBoundaryFile']['value'] = os.getcwd() + os.sep + "vertices.dat"

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=2.2,
                        min_radius=5.0,
                        max_radius=25.0,
                        kappa=0.1,
                        theta=0.0,
                        phi=0.0,
                        aspect=2,
                        p32=0.5,
                        number_of_points = 16,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })

DFN.print_domain_parameters()
DFN.make_working_directory(delete = True)
DFN.check_input()
DFN.create_network()
DFN.mesh_network(max_dist = 10, slope = 0.5)
DFN.dfn_flow()
