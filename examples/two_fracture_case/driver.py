#"""
#   :synopsis: Driver run file for bipartite graph of constant fracture network for pressure validation
#   :version: 1.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov> & Collin Sutton <collin.sutton@mines.edu>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname = f"{src_path}/output"
dfnFlow_file = f"{src_path}/pflotran.in"
dfnTrans_file = f"{src_path}/PTDFN_control.dat"

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               dfnTrans_file=dfnTrans_file,
               ncpu=4)

DFN.params['domainSize']['value'] = [2.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.05

DFN.add_user_fract(shape='rect',
                   filename=f'{src_path}/claras_fractures.dat',
                   radii=0.6,
                   translation=[-0.5, 0, 0],
                   normal_vector=[0, 0, 1],
                   aperture=1.0e-4)

DFN.add_user_fract(shape='rect',
                   radii=0.6,
                   translation=[0.5, 0, 0],
                   normal_vector=[0, 1, 0],
                   aperture=1.0e-4)

DFN.make_working_directory(delete=True)
DFN.print_domain_parameters()
DFN.check_input()

DFN.create_network()
DFN.mesh_network()

DFN.lagrit2pflotran()
DFN.pflotran()
DFN.pflotran_cleanup()
DFN.parse_pflotran_vtk_python()  
DFN.effective_perm(inflow_pressure=2e6, 
                    outflow_pressure=1e6, 
                    boundary_file='boundary_left_w.ex', 
                    direction='x', 
                    darcy_vel_file='darcyvel_001.dat')

DFN.dfn_trans(combine_avs = True)