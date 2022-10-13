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

DFN.params['domainSize']['value'] = [1, 1, 1]
DFN.params['h']['value'] = 0.05
DFN.params['tripleIntersections']['value'] = 1
DFN.params['visualizationMode']['value'] = 1

DFN.add_user_fract(shape = 'rect', from_file = False, file_name = '../user_defined_rect.dat', by_coord = False, radii = 0.6, aspect_ratio = 1, beta = 0, translation = [-0.4,0,0], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, permeability = 1.0e-12)

DFN.add_user_fract(shape = 'rect', from_file = False, file_name = '../user_defined_rect.dat', by_coord = False, radii = 1.0, aspect_ratio = .65, beta = 0, translation = [0,0,0], orientation_option = 0, angle_option = 1, normal_vector = [1,0,0], number_of_vertices = 8, permeability = 1.0e-13)

DFN.add_user_fract(shape = 'rect', from_file = False, file_name = '../user_defined_rect.dat', by_coord = False, radii = 0.6, aspect_ratio = 1, beta = 0, translation = [0.4,0,0.2], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, permeability = 1.0e-14)

DFN.add_user_fract(shape = 'rect', from_file = False, file_name = '../user_defined_rect.dat', by_coord = False, radii = 0.6, aspect_ratio = 1, beta = 0, translation = [0.4,0,-0.2], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, permeability = 1.0e-15)

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

DFN.set_flow_solver("PFLOTRAN")
DFN.inp_file = "octree_dfn.inp"

DFN.map_to_continuum(l=0.1,orl=3)
DFN.upscale(mat_perm=1e-15,mat_por=0.01)

DFN.zone2ex(uge_file='full_mesh.uge',zone_file='all')

DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()
