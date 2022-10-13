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

DFN.params['domainSize']['value'] = [20, 20, 20]
DFN.params['h']['value'] = 0.25
DFN.params['tripleIntersections']['value'] = True
DFN.params['stopCondition']['value'] = 0 #define stopCondition and nPoly for user polygons to avoid exception
DFN.params['nPoly']['value'] = 3

DFN.add_user_fract(shape="poly",
                    from_file = True,
                    file_name = '../polygons.dat',
                    by_coord = True,
                    permeability = 1e-12)


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
