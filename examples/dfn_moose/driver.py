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
dfnflow_file = f"{src_path}/th_transient.i"
DFN = DFNWORKS(jobname,
               ncpu=4,
               dfnFlow_file = dfnflow_file,
               flow_solver = "MOOSE")

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.1

DFN.add_user_fract(shape='rect',
                   radii=0.6,
                   translation=[-0.4, 0, 0],
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=1.0,
                   aspect_ratio=.65,
                   translation=[0, 0, 0],
                   normal_vector=[1, 0, 0],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=.6,
                   translation=[0.4, 0, 0.2],
                   normal_vector=[0, 0, 1],
                   permeability=2.0e-12)

DFN.add_user_fract(shape='rect',
                   radii=.6,
                   translation=[0.4, 0, -0.2],
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.print_domain_parameters()

DFN.create_network()
DFN.mesh_network(uniform_mesh=True)
DFN.dfn_flow()