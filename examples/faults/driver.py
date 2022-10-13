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

DFN.params['domainSize']['value'] = [100, 100, 100]
DFN.params['h']['value'] = 0.05
DFN.params['visualizationMode']['value'] = True

DFN.add_user_fract(shape = 'ell', from_file = False, file_name = '../user_defined_faults.dat', by_coord = False, radii = 100, aspect_ratio = 1, beta = 0, translation = [0,0,25], orientation_option = 1, angle_option = 1, trend_plunge = [45,35], number_of_vertices = 8, permeability = 1e-12)

DFN.add_user_fract(shape = 'ell', from_file = False, file_name = '../user_defined_faults.dat', by_coord = False, radii = 100, aspect_ratio = 1, beta = 0, translation = [0,25,0], orientation_option = 1, angle_option = 1, trend_plunge = [111,57], number_of_vertices = 8, permeability = 1e-13)

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

for key in DFN.params.keys():
    print(key)
    print(key, DFN.params[key]['value'])

DFN.check_input()

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network(coarse_factor=10)

DFN.dfn_flow()
DFN.dfn_trans()
