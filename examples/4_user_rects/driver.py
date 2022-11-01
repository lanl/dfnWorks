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

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.050

# This is kind of clunky. There's a lot of repitition. How can we clean this up?
DFN.add_user_fract(shape='rect',
                   file_name=f'{src_path}/user_defined_rect.dat',
                   by_coord=False,
                   radii=0.6,
                   aspect_ratio=1,
                   beta=0,
                   translation=[-0.4, 0, 0],
                   orientation_option=0,
                   angle_option=1,
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   from_file=False,
                   file_name=f'{src_path}/user_defined_rect.dat',
                   by_coord=False,
                   radii=1.0,
                   aspect_ratio=.65,
                   beta=0,
                   translation=[0, 0, 0],
                   orientation_option=0,
                   angle_option=1,
                   normal_vector=[1, 0, 0],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   from_file=False,
                   file_name=f'{src_path}/user_defined_rect.dat',
                   by_coord=False,
                   radii=.6,
                   aspect_ratio=1,
                   beta=0,
                   translation=[0.4, 0, 0.2],
                   orientation_option=0,
                   angle_option=1,
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.add_user_fract(shape='rect',
                   from_file=False,
                   file_name=f'{src_path}/user_defined_rect.dat',
                   by_coord=False,
                   radii=.6,
                   aspect_ratio=1,
                   beta=0,
                   translation=[0.4, 0, -0.2],
                   orientation_option=0,
                   angle_option=1,
                   normal_vector=[0, 0, 1],
                   permeability=1.0e-12)

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.print_domain_parameters()

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network()

DFN.dfn_flow()
DFN.dfn_trans()
