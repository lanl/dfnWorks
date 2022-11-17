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

DFN.params['domainSize']['value'] = [15, 15, 15]
DFN.params['h']['value'] = 0.1
DFN.params['domainSizeIncrease']['value'] = [0.5, 0.5, 0.5]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['seed']['value'] = 1

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        alpha=1.8,
                        min_radius=1.0,
                        max_radius=5.0,
                        kappa=1.0,
                        theta=0.0,
                        phi=0.0,
                        aspect=2,
                        beta_distribution=1,
                        beta=45.0,
                        p32=1.1,
                        hy_variable='aperture',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 10**-5,
                            "beta": 0.5
                        })

DFN.make_working_directory(delete = True)
DFN.check_input()
DFN.create_network()
DFN.output_report()
DFN.mesh_network(min_dist = 1, max_dist = 5, slope = 0.9)
# DFN.assign_hydraulic_properties()
DFN.dfn_flow()
DFN.dfn_trans()
