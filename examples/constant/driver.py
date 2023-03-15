#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname =  f"{src_path}/output"
dfnFlow_file = f"{src_path}/dfn_explicit.in"
dfnTrans_file = f"{src_path}/PTDFN_control.dat"

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=8)

DFN.params['domainSize']['value'] = [10, 10, 10]
DFN.params['h']['value'] = 0.1
DFN.params['orientationOption']['value'] = 1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 80
DFN.params['seed']['value'] = 6969420
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=20.0,
                        probability=.25,
                        aspect=1.0,
                        beta_distribution=1,
                        beta=0.0,
                        trend=0.0,
                        plunge=0.0,
                        constant=2.0,
                        hy_variable='transmissivity',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 1e-13,
                            "beta": 1
                        })

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=20.0,
                        probability=.25,
                        aspect=1.0,
                        beta_distribution=1,
                        beta=0.0,
                        trend=35.0,
                        plunge=90.0,
                        constant=2.0,
                        hy_variable='transmissivity',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 1e-13,
                            "beta": 1
                        })

DFN.add_fracture_family(shape="rect",
                        distribution="constant",
                        kappa=20.0,
                        probability=.5,
                        aspect=1.0,
                        beta_distribution=1,
                        beta=0.0,
                        trend=70.0,
                        plunge=45.0,
                        constant=2.0,
                        hy_variable='transmissivity',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 1e-13,
                            "beta": 1
                        })


DFN.make_working_directory(delete=True)
DFN.print_domain_parameters()
DFN.check_input()

DFN.create_network()
DFN.output_report()
DFN.mesh_network()

DFN.dfn_flow()
DFN.dfn_trans()
