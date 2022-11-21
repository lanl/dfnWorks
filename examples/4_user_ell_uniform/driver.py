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

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.025
DFN.params['tripleIntersections']['value'] = True

DFN.add_user_fract(shape='ell',
                   file_name=f'{src_path}/user_defined_ell.dat',
                   radii=.5,
                   translation=[-0.2, 0, 0],
                   normal_vector=[0, 0, 1],
                   number_of_vertices=8,
                   aperture=1.0e-5)

DFN.add_user_fract(shape='ell',
                   file_name=f'{src_path}/user_defined_ell.dat',
                   radii=.5,
                   translation=[0, 0, 0],
                   normal_vector=[1, 0, 0],
                   number_of_vertices=8,
                   aperture=1.0e-5)

DFN.add_user_fract(shape='ell',
                   file_name=f'{src_path}/user_defined_ell.dat',
                   radii=.4,
                   aspect_ratio=1,
                   translation=[0.2, 0, 0.2],
                   normal_vector=[0, 0, 1],
                   number_of_vertices=8,
                   aperture=1.0e-5)

DFN.add_user_fract(shape='ell',
                   file_name=f'{src_path}/user_defined_ell.dat',
                   radii=.4,
                   aspect_ratio=1,
                   translation=[0.2, 0, -0.2],
                   normal_vector=[0, 0, 1],
                   number_of_vertices=8,
                   aperture=1.0e-5)

DFN.make_working_directory(delete=True)
DFN.print_domain_parameters()
DFN.check_input()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(uniform_mesh = True)

DFN.dfn_flow()
DFN.dfn_trans()
