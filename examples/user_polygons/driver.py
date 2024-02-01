#   :synopsis: Driver run file for TPL example
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

src_path = os.getcwd()
jobname = f"{src_path}/output"
dfnFlow_file = f"{src_path}/dfn_explicit.in"

DFN = DFNWORKS(jobname, dfnFlow_file=dfnFlow_file, ncpu=8)

DFN.params['domainSize']['value'] = [20, 20, 20]
DFN.params['h']['value'] = 0.25
DFN.params['tripleIntersections']['value'] = True
DFN.params['stopCondition'][
    'value'] = 0  #define stopCondition and nPoly for user polygons to avoid exception
DFN.params['nPoly']['value'] = 9
DFN.params['ignoreBoundaryFaces']['value'] = True

DFN.add_user_fract_from_file(
    shape="poly",
    filename=f'{src_path}/polygons.dat',
    permeability=9 * [1e-12],  #list or array of nPolygons perms
    nPolygons=9)
# build network
DFN.make_working_directory(delete=True)
DFN.print_domain_parameters()
DFN.check_input()
DFN.create_network()
DFN.mesh_network()
DFN.dfn_flow()
