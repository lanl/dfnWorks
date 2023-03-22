import os
import numpy as np


def create_merge_poly_files(self):
    """ Creates a LaGriT script that reads in each fracture mesh, appends it to the main mesh, and then deletes that mesh object. Then duplicate points are removed from the main mesh using EPS_FILTER.  The points are compressed, and then written to file.

    Parameters
    ----------
        ncpu : int 
            Number of Processors used for meshing
        fracture_list : list of int
            List of fracture numbers in the DFN
        h : float 
            Meshing length scale
        visual_mode : bool
            If True, reduced_mesh.inp will be output. If False, full_mesh.inp is output
        domain : dict
            Dictionary of x,y,z domain size
        flow_solver : string
            Name of target flow solver (Changes output files)

    Returns
    -------
        n_jobs : int
            number of merge jobs

    Notes
    -----
        1. Fracture mesh objects are read into different part_*.lg files. This allows for merging of the mesh to be performed in batches.  
    """
    # get leading digits
    digits = len(str(self.num_frac))

    part_size = max(np.floor(self.num_frac / self.ncpu),
                    1)  # number of fractures in each part
    print(f"--> There are {part_size} fractures in each part")
    endis = []
    ii = 0
    for i in self.fracture_list[:-1]:
        ii += 1
        if ii == part_size:
            endis.append(i)
            ii = 0
    endis.append(self.fracture_list[-1])
    n_jobs = len(endis)
    print(endis)

    print("--> Writting partial merge scripts")
    lagrit_input = """
# Change to read LaGriT
read / lagrit /  %s / mo_%d / binary
cmo / move / mo_%d / mo_final 
define / MO_NAME_FRAC / mo_%d
"""
    if not self.visual_mode:
        lagrit_input += """
cmo / addatt / MO_NAME_FRAC / volume / evol_one
math / sum / MO_NAME_FRAC / evol_sum / 1 0 0 / MO_NAME_FRAC / evol_one 
"""
    lagrit_input += """
addmesh / merge / cmo_tmp / cmo_tmp / mo_%d
cmo / delete / mo_%d
"""
    lagrit_input_2 = '# Writing out merged fractures\n'
    if not self.visual_mode:
        lagrit_input_2 += """
mo / addatt/ cmo_tmp / volume / evol_all
math / sum / cmo_tmp / evol_sum / 1 0 0 / cmo_tmp / evol_all """
    lagrit_input_2 += """ 
cmo select cmo_tmp
dump lagrit part%d.lg cmo_tmp
finish \n 
"""

    j = 0  # Counter for cpus
    fout = 'lagrit_scripts/merge_poly_part_1.lgi'
    f = open(fout, 'w')
    for frac_id in self.fracture_list:
        tmp = f'mesh_{frac_id:0{digits}d}.lg'
        f.write(lagrit_input %
                (tmp, frac_id, frac_id, frac_id, frac_id, frac_id))
        # if i is the last fracture in the cpu set
        # move to the next cpu set
        if frac_id == endis[j]:
            f.write(lagrit_input_2 % (j + 1))
            f.flush()
            f.close()
            j += 1
            fout = f'lagrit_scripts/merge_poly_part_{j + 1}.lgi'
            f = open(fout, 'w')

    f.flush()
    f.close()
    os.remove(fout)

    print("--> Writing : merge_poly.lgi")
    ## Write LaGriT file for merge parts of the mesh and remove duplicate points
    lagrit_input = """
read / lagrit / part%d.lg / junk / binary
addmesh / merge / mo_all / mo_all / cmo_tmp 
cmo / delete / cmo_tmp 
    """
    f = open('lagrit_scripts/merge_rmpts.lgi', 'w')
    for j in range(1, n_jobs + 1):
        f.write(lagrit_input % (j))

    # Append meshes complete
    if not self.visual_mode:
        lagrit_input = """
# Appending the meshes complete 
# LaGriT Code to remove duplicates and output the mesh
cmo / select / mo_all 
#recon 1
define / EPS / %e 
define / EPS_FILTER / %e 
pset / pinter / attribute / dfield / 1,0,0 / lt / EPS 
#cmo / addatt / mo_all / inter / vint / scalar / nnodes 
#cmo / setatt / mo_all / inter / 1 0 0 / 0 
#cmo / setatt / mo_all / inter / pset, get, pinter / 1 

filterkd / pset get pinter / EPS_FILTER / nocheck
pset / pinter / delete

rmpoint / compress 
# SORT can affect a_b attribute
sort / mo_all / index / ascending / ikey / imt xic yic zic 
reorder / mo_all / ikey 
cmo / DELATT / mo_all / ikey
""" % (self.h * 10**-5, self.h * 10**-3)
        lagrit_input += """ 
resetpts / itp 
boundary_components 
#dump / full_mesh.gmv / mo_all
dump / full_mesh.inp / mo_all
dump / lagrit / full_mesh.lg / mo_all
"""
        if self.flow_solver == "PFLOTRAN":
            print("\n--> Dumping output for %s" % self.flow_solver)
            lagrit_input += """
dump / pflotran / full_mesh / mo_all / nofilter_zero
dump / stor / full_mesh / mo_all / ascii
    """
        elif self.flow_solver == "FEHM":
            print("\n--> Dumping output for %s" % self.flow_solver)
            lagrit_input += """
dump / stor / full_mesh / mo_all / ascii
dump / coord / full_mesh / mo_all 
# matid start at 1, but we need them to start at 7 for FEHM due to zone files
# So we do a little addition
math / add / mo_all / imt1 / 1,0,0 / mo_all / imt1 / 6
dump / zone_imt / full_mesh / mo_all
# and then we subtract 6 back 
math / subtract / mo_all / imt1 / 1,0,0 / mo_all / imt1 / 6
"""
        else:
            print("WARNING!!!!!!!\nUnknown flow solver selection: %s" %
                  self.flow_solver)
        lagrit_input += """ 
# Dump out Material ID Dat file
cmo / modatt / mo_all / isn / ioflag / l
cmo / modatt / mo_all / x_four / ioflag / l
cmo / modatt / mo_all / fac_n / ioflag / l
cmo / modatt / mo_all / dfield / ioflag / l
cmo / modatt / mo_all / rf_field / ioflag / l
cmo / modatt / mo_all / a_b / ioflag / l
cmo / modatt / mo_all / b_a / ioflag / l
cmo / modatt / mo_all / xnorm / ioflag / l
cmo / modatt / mo_all / ynorm / ioflag / l
cmo / modatt / mo_all / znorm / ioflag / l
cmo / modatt / mo_all / evol_one / ioflag / l
cmo / modatt / mo_all / evol_all / ioflag / l
cmo / modatt / mo_all / numbnd / ioflag / l
cmo / modatt / mo_all / id_numb / ioflag / l
cmo / modatt / mo_all / evol_all / ioflag / l
cmo / modatt / mo_all / itp / ioflag / l
cmo / modatt / mo_all / icr / ioflag / l
cmo / modatt / mo_all / meshid / ioflag / l
cmo / modatt / mo_all / id_n_1 / ioflag / l
cmo / modatt / mo_all / id_n_2 / ioflag / l
cmo / modatt / mo_all / pt_gtg / ioflag / l
# Dump out Material ID Dat file
dump / avs2 / materialid.dat / mo_all / 0 0 2 0

cmo / modatt / mo_all / imt1 / ioflag / l
#cmo / modatt / mo_all / family_id / ioflag / l
cmo / modatt / mo_all / evol_onen / ioflag / l
# Dump mesh with no attributes for viz
# dump / full_mesh_viz.inp / mo_all

# Dump out zone files
define / XMAX / %e 
define / XMIN / %e 
define / YMAX / %e 
define / YMIN / %e 
define / ZMAX / %e 
define / ZMIN / %e 

define / ZONE / 1
define / FOUT / boundary_top
pset / top / attribute / zic / 1,0,0/ gt / ZMAX
pset / top / zone / FOUT/ ascii / ZONE

define / ZONE / 2
define / FOUT / boundary_bottom
pset / bottom / attribute / zic / 1,0,0/ lt / ZMIN
pset / bottom / zone / FOUT/ ascii / ZONE

define / ZONE / 3
define / FOUT / boundary_left_w
pset / left_w / attribute/ xic/ 1,0,0 /lt / XMIN
pset / left_w / zone / FOUT/ ascii / ZONE

define / ZONE / 4
define / FOUT / boundary_front_n
pset / front_n / attribute/ yic / 1,0,0 / gt / YMAX
pset / front_n / zone / FOUT/ ascii / ZONE

define / ZONE / 5
define / FOUT / boundary_right_e
pset / right_e / attribute/ xic / 1,0,0/ gt / XMAX
pset / right_e / zone / FOUT/ ascii / ZONE

define / ZONE / 6
define / FOUT / boundary_back_s
pset / back_s / attribute/ yic/ 1,0,0 / lt / YMIN
pset / back_s / zone / FOUT/ ascii / ZONE

"""
        eps = self.h * 10**-3
        parameters = (0.5*self.domain['x'] - eps, -0.5*self.domain['x'] + eps, \
            0.5*self.domain['y'] - eps, -0.5*self.domain['y'] + eps, \
            0.5*self.domain['z'] - eps, -0.5*self.domain['z'] + eps)

        lagrit_input = lagrit_input % parameters

    else:
        lagrit_input = """
cmo / modatt / mo_all / icr1 / ioflag / l
cmo / modatt / mo_all / isn1 / ioflag / l
cmo / modatt / mo_all / itp1 / ioflag / l
#dump / reduced_mesh.gmv / mo_all 
dump / reduced_mesh.inp / mo_all
"""
    lagrit_input += """
quality 
finish
"""
    f.write(lagrit_input)
    f.flush()
    f.close()

    return n_jobs
