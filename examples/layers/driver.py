#"""
#   :synopsis: Driver run file for layer-conforming fracture example
#              Tests the layerConformingFractures feature added to dfnGen.
#              Two overlapping layers with deliberately large fractures (max_radius
#              up to 10 m in a 20 m domain) to ensure many fractures cross layer
#              boundaries and must be clipped. Run twice -- once with conforming
#              on (default) and once with it off -- to confirm the difference.
#   :version: 2.0
#   :maintainer: Jeffrey Hyman
#.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>
#"""

from pydfnworks import *
import os

# -----------------------------------------------------------------------
# Toggle this flag to test all three modes:
#   0 --> disabled: fractures extend freely beyond layer boundaries
#   1 --> perfect conforming: clipped exactly at layer Z boundaries
#   2 --> soft conforming: clipped at boundary +/- 2h, preserving a
#         small overhang for flow connectivity between layers
# -----------------------------------------------------------------------
LAYER_CONFORMING = 2

jobname = os.getcwd() + "/output"
dfnFlow_file = os.getcwd() + '/dfn_explicit.in'

DFN = DFNWORKS(jobname,
               dfnFlow_file=dfnFlow_file,
               ncpu=8)

# Domain: tall in Z (20 m) so layer boundaries are well inside the domain
# and large fractures have plenty of room to cross them
DFN.params['domainSize']['value'] = [5.0, 5.0, 10.0]
DFN.params['domainSizeIncrease']['value'] = [1.0, 1.0, 1.0]
DFN.params['h']['value'] = 0.1
DFN.params['boundaryFaces']['value'] = [0, 0, 0, 0, 1, 1]
DFN.params['seed']['value'] = 42 

# Two layers that deliberately overlap from z=-2 to z=2.
# Fractures centered in the overlap zone belong to whichever family
# they're assigned to, so layer clipping is the only thing constraining
# their Z extent when LAYER_CONFORMING is True.
#
#   Layer 1:  z in [-10,  2]   (bottom 12 m of domain)
#   Layer 2:  z in [ -2, 10]   (top    12 m of domain)
#   Overlap:  z in [ -2,  2]   (middle  4 m)
DFN.params['numOfLayers']['value'] = 2
DFN.params['layers']['value'] = [[-5.0, 0], [0, 5.0]]

# Key parameter under test
DFN.params['layerConformingFractures']['value'] = LAYER_CONFORMING

# Family 1 -- bottom layer
# Large alpha (2.3) and wide radius range (1-10 m) relative to the 12 m
# layer thickness guarantees many fractures will cross the z=2 boundary
# when LAYER_CONFORMING is False.
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=0.1,
                        layer=1,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.3,
                        min_radius=1.0,
                        max_radius=10.0,
                        p32=4,
                        hy_variable="transmissivity",
                        hy_function="constant",
                        hy_params={"mu": 6.3e-8})

# Family 2 -- top layer
# Steeper alpha (2.6) but same wide radius range.
# Fractures with radius > 8 m centered near z=0 will cross the z=-2
# boundary when LAYER_CONFORMING is False.
DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        kappa=1.0,
                        layer=2,
                        theta=0.0,
                        phi=0.0,
                        alpha=2.6,
                        min_radius=1.0,
                        max_radius=10.0,
                        p32=4,
                        hy_variable="transmissivity",
                        hy_function="constant",
                        hy_params={"mu": 6.3e-9})

DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()

DFN.mesh_network()

DFN.output_report()

DFN.dfn_flow()