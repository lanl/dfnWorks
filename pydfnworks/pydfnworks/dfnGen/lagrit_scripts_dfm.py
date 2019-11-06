"""
.. module:: lagrit_scripts_dfm.py
   :synopsis: create lagrit scripts for meshing DFM using LaGriT
.. moduleauthor:: Matthew Sweeney <msweeney2796@lanl.gov>

"""

import os
import sys
import glob
import subprocess
import numpy as np
import shutil
from pydfnworks.dfnGen import mesh_dfn_helper as mh
import time

def mesh_dfm(self):
    """ This function generates a conforming DFM mesh using the full_mesh.inp 
    as input. Visualization mode must be turned off in the DFN input card.

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    -------
        None

    Notes
    -----

    """
    print('=' * 80)
    print("Creating conforming DFM mesh using LaGriT : Starting")
    print('=' * 80)

    num_poly, h, _, _, domain = mh.parse_params_file()

    # Extent of domain
    x0 = 0 - (domain['x'] / 2.0)
    x1 = 0 + (domain['x'] / 2.0)
    y0 = 0 - (domain['y'] / 2.0)
    y1 = 0 + (domain['y'] / 2.0)
    z0 = 0 - (domain['z'] / 2.0)
    z1 = 0 + (domain['z'] / 2.0)

    # Mesh size in matrix
    l = h/2
    # Number of points in each direction in matrix
    np = domain['x'] / l + 1

    if np**3 > 1e8:
        error = "ERROR: Number of elements > 1e8. Exiting"
        sys.stderr.write(error)
        sys.exit(1)

    dfm_driver(np, num_poly)
    dfm_box(x0, x1, y0, y1, z0, z1)    
    dfm_build()
    dfm_fracture_facets(num_poly)
    dfm_facets()
    dfm_run()

def dfm_driver(np, num_poly):
    """ This function creates the main lagrit driver script, which calls all
    lagrit scripts.

    Parameters
    ----------
    
    Returns
    -------

    Notes
    -----

    """
    floop = ""
    for i in range(1,num_poly+1):
        if i < num_poly:
            floop += "facets_f{0}.table &\n".format(i)
        else:
            floop += "facets_f{0}.table".format(i)
            
    f_name = 'dfm_mesh_fracture_driver.lgi'
    f = open(f_name, 'w')
    fin = ("""#
# dfm_mesh_fracture_driver.lgi
#   dfm_box_dimensions.mlgi
#   dfm_build_background_mesh.mlgi
#   dfm_extract_fracture_facets.mlgi
#      dfm_extract_facets.mlgi
#
# extract_fracture_facets.mlgi must be customized for the number of fractures in the DFN
#
# This is the dfnWorks DFN mesh
#
define / INPUT / full_mesh.inp
read / avs / INPUT / mo_dfn
cmo / DELATT / mo_dfn / dfield
cmo / DELATT / mo_dfn / b_a
cmo / DELATT / mo_dfn / numbnd
cmo / DELATT / mo_dfn / if_numb
#
# Diagnostics on fracture mesh extents and resolution
#
cmo / printatt / mo_dfn / -xyz- / minmax
quality
quality/edge_min
quality/edge_max
#
# Define a resolution for the background mesh. This assumes the DFN
# triangulation is uniform resolution triangles. No attempt is made
# to adapt the volume mesh resolution to the DFN triangle resolution.
#
define / NP / {0}
define / NPM1 / {1}
#
define / MO_BACKGROUND / mo_background
infile dfm_box_dimensions.mlgi
infile dfm_build_background_mesh.mlgi
#
# Remove all vertices of the tet mesh that fall withing a circumsphere of a fracture triangle.
#
addmesh / excavate / mo_tmp / MO_BACKGROUND / mo_dfn
cmo / delete / MO_BACKGROUND
#
# Merge the vertices of the excavated tet mesh with the DFN vertices
#
cmo / create / mo_dfm / / / tet
copypts / mo_dfm / mo_tmp
copypts / mo_dfm / mo_dfn
cmo / delete / mo_tmp
#
cmo / setatt / mo_dfm / imt / 1 0 0 / 1
cmo / setatt / mo_dfm / itp / 1 0 0 / 0
cmo / select / mo_dfm
connect
cmo / setatt / mo_dfm / itetclr / 1 0 0 / 1
resetpts / itp
quality
#
compute / signed_distance_field / mo_dfm / mo_dfn / df_sign_dfm_dfn
#
dump / avs    / dfm_tet_mesh.inp / mo_dfm
dump / lagrit / dfm_tet_mesh.lg  / mo_dfm
dump / exo    / dfm_tet_mesh.exo / mo_dfm

cmo / delete / mo_dfm
cmo / delete / mo_dfn
#
cmo / status / brief
#
infile dfm_extract_fracture_facets.mlgi
# infile diagnostics.mlgi
#
dump / exo / dfm_tet_mesh_w_fsets.exo / mo_dfm / / / &
     facesets &
""".format(int(np), int(np-1)) + floop + """

finish
""")
    f.write(fin)
    f.flush()
    f.close()
    print("Creating dfm_mesh_fracture_driver.lgi file: Complete\n")

def dfm_box(x0, x1, y0, y1, z0, z1):    
    """ This function creates the dfm_box_dimensions.mlgi lagrit script.

    Parameters
    ----------
    
    Returns
    -------

    Notes
    -----

    """
    f_name = 'dfm_box_dimensions.mlgi'
    f = open(f_name, 'w')
    fin = ("""#
# Define a bounding box that surrounds, and is a big bigger, than the DFN
#
define / X0 / {0}
define / X1 / {1}
define / Y0 / {2}
define / Y1 / {3}
define / Z0 / {4}
define / Z1 / {5}

finish
""".format(x0, x1, y0, y1, z0, z1))
    f.write(fin)
    f.flush()
    f.close()
    print("Creating dfm_box_dimensions.mlgi file: Complete\n")

def dfm_build():
    """ This function creates the dfm_build_background_mesh.mlgi lagrit script.

    Parameters
    ----------
    
    Returns
    -------

    Notes
    -----

    """
    f_name = 'dfm_build_background_mesh.mlgi'
    f = open(f_name, 'w')
    fin = ("""#
# Build a uniform background point distribution.
#
cmo / create / MO_BACKGROUND / / / tet
createpts / xyz / NP NP NP / X0 Y0 Z0 / X1 Y1 Z1 / 1 1 1
cmo / setatt / MO_BACKGROUND / imt / 1 0 0 / 1
connect / noadd
cmo / setatt / MO_BACKGROUND / itetclr / 1 0 0 / 1
#
finish
""")
    f.write(fin)
    f.flush()
    f.close()
    print("Creating dfm_box_dimensions.mlgi file: Complete\n")

def dfm_fracture_facets(num_poly):
    """ This function creates the dfm_extract_fracture_facets.mlgi lagrit script.

    Parameters
    ----------
    
    Returns
    -------

    Notes
    -----

    """
    floop1 = ""
    floop2 = ""
    for i in range(1,num_poly+1):
        floop1 += """
define / FRAC_ID / {0}
define / FRAC_FILE_OUT / facets_f{0}.inp
define / FRAC_TABLE_OUT / facets_f{0}.table
#
infile dfm_extract_facets.mlgi
        """.format(i)
        floop2 += """
read / avs2 / facets_f{0}.inp / mo
cmo / setatt / mo / itetclr / 1 0 0 / {0}
addmesh / merge / mo_merge / mo_merge / mo
cmo / delete / mo
        """.format(i)

    f_name = 'dfm_extract_fracture_facets.mlgi'
    f = open(f_name, 'w')
    fin = ("""#
define / INPUT / full_mesh.inp
define / MO_ONE_FRAC / mo_tmp_one_fracture
#
read / avs / dfm_tet_mesh.inp / mo_dfm
cmo / status / brief
read / avs / INPUT / mo_dfn
cmo / status / brief
""" + floop1 + floop2 + """
dump / avs2 / facets_merged.inp / mo_merge
cmo / addatt / mo_merge / id_frac / vint / scalar / nelements
cmo / copyatt / mo_merge / mo_merge / id_frac / itetclr
dump / avs2 / facets_merged.table / mo_merge / 0 0 0 2
cmo / delete / mo_merge

finish
""")
    f.write(fin)
    f.flush()
    f.close()
    print("Creating dfm_extract_fracture_facets.mlgi file: Complete\n")

def dfm_facets():
    """ This function creates the dfm_extract_facets.mlgi lagrit script.

    Parameters
    ----------
    
    Returns
    -------

    Notes
    -----

    """
    f_name = 'dfm_extract_facets.mlgi'
    f = open(f_name, 'w')
    fin = ("""#
cmo / copy / MO_ONE_FRAC / mo_dfn
cmo / select / MO_ONE_FRAC
rmmat / FRAC_ID / element / exclusive
rmpoint / compress
resetpts / itp
cmo / status / brief
#
compute / signed_distance_field / mo_dfm / MO_ONE_FRAC / dfield_sign

cmo / delete / MO_ONE_FRAC
#
cmo / copy / mo_df_work / mo_dfm

cmo / DELATT / mo_dfm / dfield_sign

cmo / select / mo_df_work
pset / p1 / attribute / dfield_sign / 1 0 0 / gt 0.0
pset / p2 / attribute / dfield_sign / 1 0 0 / lt 0.0
eltset / e1 / inclusive / pset get p1
eltset / e2 / inclusive / pset get p2
cmo / setatt / mo_df_work / itetclr / eltset get e1 / 1
cmo / setatt / mo_df_work / itetclr / eltset get e2 / 2
resetpts / itp
extract / surfmesh / 1 0 0 / MO_ONE_FRAC_EXTRACT / mo_df_work
#
cmo / select / MO_ONE_FRAC_EXTRACT
eltset / edel / idelem0 / eq / 0
rmpoint / element / eltset get edel
rmpoint / compress
pset / pdel / attribute / dfield_sign / 1 0 0 / gt / 1.e-9
rmpoint / pset get pdel / inclusive
rmpoint / compress
#
# idelem0, idelem1 are element numbers
# idface0, idface1 are the face numbers
#
cmo / DELATT / MO_ONE_FRAC_EXTRACT / itetclr0
cmo / DELATT / MO_ONE_FRAC_EXTRACT / itetclr1
cmo / DELATT / MO_ONE_FRAC_EXTRACT / facecol
#
# Don't keep both sides of the fracture face information.
#
cmo / DELATT / MO_ONE_FRAC_EXTRACT / idelem0
cmo / DELATT / MO_ONE_FRAC_EXTRACT / idface0
#
dump / avs2 / FRAC_FILE_OUT  / MO_ONE_FRAC_EXTRACT
dump / avs2 / FRAC_TABLE_OUT / MO_ONE_FRAC_EXTRACT  / 0 0 0 2
#
cmo / delete / MO_ONE_FRAC_EXTRACT
#
cmo / status / brief
#
finish
""")
    f.write(fin)
    f.flush()
    f.close()
    print("Creating dfm_extract_facets.mlgi file: Complete\n")

def dfm_run():
    """ This function executes the lagrit scripts. 
    
    Parameters
    ----------
        None    

    Returns
    -------
        None
    
    Notes
    -----
        None
 
    """
    # Run LaGriT

    cmd = os.environ['LAGRIT_EXE'] + '< dfm_mesh_fracture_driver.lgi'
    subprocess.call(cmd, shell=True)
