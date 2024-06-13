#"""
#   :synopsis: Driver run file for wells example
#   :version: 2.7
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

example_path = os.getcwd()
jobname = f"{example_path}/output"
dfnFlow_file = f"{example_path}/dfn_flow_rate.in"

DFN = DFNWORKS(jobname, dfnFlow_file=dfnFlow_file, ncpu=10)

DFN.params['domainSize']['value'] = [15, 15, 15]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 400
DFN.params['domainSizeIncrease']['value'] = [.5, .5, .5]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        probability=.5,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.6,
                        min_radius=1.0,
                        max_radius=5.0,
                        hy_variable="permeability",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 1e-10,
                            "beta": 0.85
                        })
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        probability=.5,
                        aspect=1,
                        beta_distribution=0,
                        beta=0.0,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.6,
                        min_radius=1.0,
                        max_radius=5.0,
                        hy_variable="permeability",
                        hy_function="correlated",
                        hy_params={
                            "alpha": 1e-10,
                            "beta": 0.85
                        })

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()

# Well information and meshing
inject_well = {"name": 'inject', "filename": "well_inject.dat", "r": 0.3}
extract_well = {"name": 'extract', "filename": "well_extract.dat", "r": 0.3}

wells = [inject_well, extract_well]

os.symlink(f"{example_path}/{inject_well['filename']}",
           f"{inject_well['filename']}")
os.symlink(f"{example_path}/{extract_well['filename']}",
           f"{extract_well['filename']}")

DFN.find_well_intersection_points(wells)
DFN.mesh_network()
DFN.lagrit2pflotran()
DFN.tag_well_in_mesh(wells)
DFN.cleanup_wells(wells)
os.chdir(DFN.jobname)
DFN.combine_well_boundary_zones(wells)

####dfnFlow()
fin = open("boundary_bottom.ex", "r")
fin.readline()
line = fin.readline()
fin.close()

fout = open("pinned.ex", "w")
fout.write("CONNECTIONS 1\n")
fout.write(line)
fout.close()

DFN.pflotran()
DFN.parse_pflotran_vtk_python()
DFN.pflotran_cleanup()
