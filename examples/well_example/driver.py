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

DFN.params['domainSize']['value'] = [15, 15, 15]
DFN.params['h']['value'] = 0.1
DFN.params['stopCondition']['value'] = 0
DFN.params['nPoly']['value'] = 400
DFN.params['domainSizeIncrease']['value'] = [.5,.5,.5]
DFN.params['keepOnlyLargestCluster']['value'] = True
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1,1,0,0,0,0]

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
                        hy_variable = "permeability",
                        hy_function = "semi-correlated",
                        hy_params = {"alpha":1e-12, "beta":1.2, "sigma":1.3})

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
                        hy_variable = "permeability",
                        hy_function = "semi-correlated",
                        hy_params = {"alpha":2e-12, "beta":1.2, "sigma":1.3})

DFN.print_family_information(1)

DFN.make_working_directory(delete=True)

DFN.check_input()

for key in DFN.params.keys():
    print(key, DFN.params[key]['value'])

# define_paths()
DFN.create_network()
# DFN.output_report()

# Well information and meshing
inject_well = {"name": 'inject', "filename": "well_inject.dat","r":0.1}
extract_well = {"name": 'extract', "filename": "well_extract.dat","r":0.1}

wells = [inject_well, extract_well]


path = "DUMMY/dfnWorks/examples/well_example/"
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


