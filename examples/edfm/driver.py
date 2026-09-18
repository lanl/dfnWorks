#"""
#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os
from build_hex_dfn_lgi import write_lagrit_script

src_path = os.getcwd()
jobname = src_path + "/output"
dfnFlow_file = src_path + '/dfn_explicit.in'
dfnTrans_file = src_path + '/PTDFN_control.dat'

DFN = DFNWORKS(jobname,
               ncpu=4)

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.05

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

DFN.mesh_network(uniform_mesh = True)

lx = DFN.params['domainSize']['value'][0]
ly = DFN.params['domainSize']['value'][1] 
lz = DFN.params['domainSize']['value'][2]

nx = 5
ny = 5
nz = 5 
epsilon = 1e-4 

write_lagrit_script(
        nx=nx,
        ny=ny,
        nz=nz,
        lx=lx,
        ly=ly,
        lz=lz,
        epsilon=epsilon,
    )



DFN.run_lagrit("build_hex_dfn.lgi")

DFN.lagrit2pflotran()


# DFN.dfn_flow()
# DFN.dfn_trans()
