#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd() 
jobname = src_path + "/output"
dfnFlow_file = src_path+ '/dfn_explicit.in'
dfnTrans_file = src_path + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [10, 10, 10]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 40
DFN.params['rAngleOption']['value'] = 1
DFN.params['boundaryFaces']['value'] = [0,0,1,1,0,0]

DFN.add_fracture_family(shape="rect",
                        distribution="exp",
                        kappa=1.0,
                        probability=1.0,
                        aspect=1.0,
                        theta=9.52,
                        phi=80.82,
                        exp_mean=3.373,
                        min_radius=1.0,
                        max_radius=50.0,
                        hy_variable='permeability',
                        hy_function='semi-correlated',
                        hy_params={
                            "alpha": 10**-8,
                            "beta": 0.5,
                            "sigma": 1.0
                        })

DFN.make_working_directory(delete=True)

DFN.print_domain_parameters()
DFN.check_input()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network()
DFN.dfn_flow()
DFN.dfn_trans()
