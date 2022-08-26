"""
.. file:: run_wells.py
   :synopsis: run file for well example 
   :version: 1.0
   :maintainer: Jeffrey Hyman
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import os
from pydfnworks import * 

DFN = create_dfn()
#
DFN.make_working_directory()
#### dfnGen
DFN.check_input()
DFN.create_network()
#DFN.output_report()

# Well information and meshing
inject_well = {"name": 'inject', "filename": "well_inject.dat","r":0.1}
extract_well = {"name": 'extract', "filename": "well_extract.dat","r":0.1}
 
wells = [inject_well, extract_well]


path = "/home/astansberry/dfnworks/examples/well_example/"
os.symlink(f"{path}"+f"{inject_well['filename']}",f"{inject_well['filename']}")
os.symlink(f"{path}"+f"{extract_well['filename']}",f"{extract_well['filename']}")


DFN.find_well_intersection_points(wells)
DFN.mesh_network()
DFN.lagrit2pflotran()
DFN.tag_well_in_mesh(wells)
DFN.cleanup_wells(wells)
os.chdir(DFN.jobname)
DFN.combine_well_boundary_zones(wells)

####dfnFlow()
os.symlink("pboundary_bottom.ex","pinned.ex")
DFN.pflotran()
DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()
