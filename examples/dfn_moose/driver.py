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

DFN = DFNWORKS(jobname,
               ncpu=32)

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

# define_paths()
DFN.create_network()
DFN.mesh_network(uniform_mesh=True)
DFN.mesh_dfm()

DFN.set_flow_solver("MOOSE")
DFN.dfnFlow_file = "/project/simdata4/ajz/dfnWorks/examples/dfn_moose/th_transient.i"
DFN.ncpu = 4
DFN.dfn_flow()