"""
.. file:: run_octree.py
   :synopsis: run file for dfnworks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Matt Sweeney <msweeney2796@lanl.gov>

"""


from pydfnworks import * 

DFN = create_dfn()

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network(visual_mode=True)

DFN.set_flow_solver("PFLOTRAN")
DFN.inp_file = "octree_dfn.inp"

DFN.map_to_continuum(l=0.1,orl=3)
DFN.upscale(mat_perm=1e-15,mat_por=0.01)

DFN.zone2ex(uge_file='full_mesh.uge',zone_file='all')

DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()
