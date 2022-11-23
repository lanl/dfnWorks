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
DFN.params['seed']['value'] = 1 
DFN.params['boundaryFaces']['value'] = [0,0,1,1,0,0]

DFN.add_fracture_family(shape="rect",
                        distribution="exp",
                        probability = 1,
                        kappa=0.1,
                        theta=0,
                        phi=0,
                        exp_mean=2.5,
                        min_radius=1.0,
                        max_radius=10.0,
                        hy_variable='permeability',
                        hy_function='semi-correlated',
                        hy_params={
                            "alpha": 1e-13,
                            "beta": 0.9,
                            "sigma": 1.0
                        })

DFN.dfn_gen()
DFN.dfn_flow()
DFN.dfn_trans()
