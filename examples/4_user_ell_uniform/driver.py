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

DFN.params['domainSize']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.025
DFN.params['tripleIntersections']['value'] = True

DFN.add_user_fract(shape = 'ell', from_file = False, file_name = '../user_defined_ell.dat', by_coord = False, radii = .5, aspect_ratio = 1, beta = 0, translation = [-0.2,0,0], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, aperture = 1.0e-5)

DFN.add_user_fract(shape = 'ell', from_file = False, file_name = '../user_defined_ell.dat', by_coord = False, radii = .5, aspect_ratio = 1, beta = 0, translation = [0,0,0], orientation_option = 0, angle_option = 1, normal_vector = [1,0,0], number_of_vertices = 8, aperture = 1.0e-5)

DFN.add_user_fract(shape = 'ell', from_file = False, file_name = '../user_defined_ell.dat', by_coord = False, radii = .4, aspect_ratio = 1, beta = 0, translation = [0.2,0,0.2], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, aperture = 1.0e-5)

DFN.add_user_fract(shape = 'ell', from_file = False, file_name = '../user_defined_ell.dat', by_coord = False, radii = .4, aspect_ratio = 1, beta = 0, translation = [0.2,0,-0.2], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, aperture = 1.0e-5)


DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

DFN.dfn_flow()
DFN.dfn_trans()
