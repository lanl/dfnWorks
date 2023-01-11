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

DFN.params['domainSize']['value'] = [200, 200, 200]
DFN.params['h']['value'] = 1.0
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 300
DFN.params['radiiListIncrease']['value'] = 0.01
DFN.params['outputFinalRadiiPerFamily']['value'] = True
DFN.params['outputAcceptedRadiiPerFamily']['value'] = True
DFN.params['forceLargeFractures']['value'] = 1
DFN.params['domainSizeIncrease']['value'] = [10,10,10]
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1,1,1,1,1,1]
DFN.params['rejectsPerFracture']['value'] = 350
DFN.params['seed']['value'] = 4

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=21.7,
                        probability=.5,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        number_of_points=19,
                        theta=90.0,
                        phi=90.0,
                        alpha=3.0,
                        min_radius=20.0,
                        max_radius=100.0,
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":1e-12})

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=21.5,
                        probability=.5,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        number_of_points=19,
                        theta=0.0,
                        phi=0.0,
                        alpha=3.0,
                        min_radius=10.0,
                        max_radius=80.0,
                        hy_variable='permeability',
                        hy_function='constant',
                        hy_params={"mu":2e-12})

DFN.add_user_fract(shape = 'rect', from_file = False, file_name = '../user_defined_rect.dat', by_coord = False, radii = 200, aspect_ratio = 0.01, beta = 90, translation = [0,0,0], orientation_option = 0, angle_option = 1, normal_vector = [0,0,1], number_of_vertices = 8, permeability = 1.0e-11)

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()
DFN.mesh_network()

# call LaGriT to run a script for identifying all the nodes on the well
cmd = os.environ['LAGRIT_EXE'] + ' < DUMMY/dfnworks/examples/reservoir_example/CreateWellZone.lgi '
subprocess.call(cmd,shell=True)

# run python  script to combine 4 boundary faces nodes into one zone file  -> inflow boundary
# and the well zone file -> outflow boundary

cmd = 'python DUMMY/dfnworks/examples/reservoir_example/create_boundaries.py'
subprocess.call(cmd,shell=True)

DFN.lagrit2pflotran()
# create a "well.ex" for assigning pressure boundary conditions to the well
DFN.zone2ex(zone_file="well.zone",face="none")

DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()

# DFNtrans
DFN.dfn_trans()
