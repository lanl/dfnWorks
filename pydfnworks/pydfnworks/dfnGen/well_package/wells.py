import os
import numpy as np
import shutil

from pydfnworks import *


def tag_well_in_mesh(self, wells):
    """ Identifies nodes in a DFN for nodes the intersect a well with radius r [m]\n
    1. Well coordinates in well["filename"] are converted to a polyline that are written into "well_{well['name']}_line.inp"\n
    2. Well is expanded to a volume with radius well["r"] and written into the avs file well_{well["name"]}_volume.inp\n
    3. Nodes in the DFN that intersect with the well are written into the zone file well_{well["name"]}.zone\n
    4. If using PFLOTRAN, then an ex file is created from the well zone file\n

    Parameters    
    -----------
        self : object
            DFN Class
        well: Dictionary
            Dictionary of information about the well that contains the following attributes

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates with the following format
                x0 y0 z0\n
                x1 y1 z1\n
                ...\n
                xn yn zn\n

            well["r"] : float 
                radius of the well
    Returns
    --------
        None
    Notes
    --------
        Wells can be a list of well dictionaries

    """

    if type(wells) is dict:
        well = wells
        print(
            f"\n\n--> Identifying nodes in the DFN intersecting with a vertical well named {well['name']}."
        )

        # 1) convert well into polyline AVS if it doesn't exist
        if not os.path.isfile(f"well_{well['name']}_line.inp"):
            convert_well_to_polyline_avs(well, self.h)

        # 2) expand the polyline of the well into a volume with radius r
        expand_well(well)

        # 3) find the nodes in the well that corresponds / intersect the well
        get_well_zone(well, self.inp_file)

        # 4) convert the zone file to ex files for PFLTORAN
        if self.flow_solver == "PFLOTRAN":
            self.zone2ex(zone_file=f"well_{well['name']}.zone", face='well')

        if self.flow_solver == "FEHM":
            print(f"--> Well nodes are in well_{well['name']}.zone")

            print(f"--> Well creation for {well['name']} complete\n\n")

    if type(wells) is list:
        for well in wells:
            print(
                f"\n\n--> Identifying nodes in the DFN intersecting with a vertical well named {well['name']}."
            )

            # 1) convert well into polyline AVS if it doesn't exist
            if not os.path.isfile(f"well_{well['name']}_line.inp"):
                convert_well_to_polyline_avs(well, self.h)

            # 2) expand the polyline of the well into a volume with radius r
            expand_well(well)

            # 3) find the nodes in the well that corresponds / intersect the well
            get_well_zone(well, self.inp_file)

            # 4) convert the zone file to ex files for PFLTORAN
            if self.flow_solver == "PFLOTRAN":
                self.zone2ex(zone_file=f"well_{well['name']}.zone",
                             face='well')

            if self.flow_solver == "FEHM":
                print(f"--> Well nodes are in well_{well['name']}.zone")

            print(f"--> Well creation for {well['name']} complete\n\n")


def convert_well_to_polyline_avs(well, h = None):
    """  Identifies converts well coordinates into a polyline avs file. Distance between 
    point on the polyline are h/2 apart. Polyline is written into "well_{well['name']}_line.inp"

    Parameters    
    -----------
        well: dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well
        h : float
            h parameter for meshing. 

    Returns
    --------
        None

    Notes
    --------
        If flow solver is set to PFLOTRAN, the zone file dumped by LaGriT will be converted to 
        an ex file. 

    """
    print("--> Interpolating well coordinates into a polyline")


    # read in well coordinates
    pts = np.genfromtxt(f"{well['filename']}")
    n, _ = np.shape(pts)

    # Linear interpolation of well into a polyline
    new_pts = []
    new_pts.append(pts[0])
    new_idx = 0

    for i in range(1, n):
        distance = np.linalg.norm(pts[i, :] - pts[i - 1, :])
        if distance < h:
            new_pts.append(pts[i, :])
            new_idx += 1
        else:
            # discretized to less than h
            m = int(np.ceil(distance / h))
            dx = (pts[i, 0] - pts[i - 1, 0]) / m
            dy = (pts[i, 1] - pts[i - 1, 1]) / m
            dz = (pts[i, 2] - pts[i - 1, 2]) / m
            for j in range(m):
                interp = np.zeros(3)
                interp[0] = new_pts[new_idx][0] + dx
                interp[1] = new_pts[new_idx][1] + dy
                interp[2] = new_pts[new_idx][2] + dz
                new_pts.append(interp)
                del interp
                new_idx += 1

    print("--> Interpolating well coordinates into a polyline: Complete")
    # Write interpolated polyline into an AVS file
    avs_filename = f"well_{well['name']}_line.inp"
    print(f"--> Writing polyline into avs file : {avs_filename}")

    num_pts = new_idx + 1
    pt_digits = len(str(num_pts))

    num_elem = new_idx
    elem_digits = len(str(num_elem))

    favs = open(avs_filename, "w")
    favs.write(f"{num_pts}\t{num_elem}\t0\t0\t0\n")
    for i in range(num_pts):
        favs.write(
            f"{i+1:0{pt_digits}d} {new_pts[i][0]:12e} {new_pts[i][1]:12e} {new_pts[i][2]:12e}\n"
        )
    for i in range(num_elem):
        favs.write(f"{i+1} 1 line {i+1} {i+2}\n")
    favs.close()
    print(f"--> Writing polyline into avs file : {avs_filename} : Complete")


def expand_well(well):
    """  Expands the polyline defining the well into a volume with radius r [m]. 
    A sphere of points around each point is created and then connected.
    Volume is written into the avs file well_{well["name"]}_volume.inp

    Parameters    
    -----------
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well
                
            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well

    Returns
    --------
        None

    Notes
    --------
        Mesh of the well is written into the avs file {well["name"][:-4]}.inp 

    """

    print("--> Expanding well into a volume.")

    r = well["r"]

    convert_well_to_polyline_avs(well, r)

    angle_r = r / np.sqrt(2)

    lagrit_script = f"""
    ## read in polyline of well
    read / well_{well['name']}_line.inp / mo_line
    cmo / printatt / mo_line / -xyz- / minmax

    ## expand every point in the polyline into a discrete sphere
    ## with radius r
    cmo / create / mo_well / / / tet
        copypts / mo_well / mo_line 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / {well["r"]} 0 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / -{well["r"]} 0 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 {well["r"]} 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 -{well["r"]} 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 0 {well["r"]} 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 0 -{well["r"]} 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / {angle_r} {angle_r} 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / {angle_r} -{angle_r} 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / -{angle_r} {angle_r} 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / -{angle_r} -{angle_r} 0 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 {angle_r} {angle_r} 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 {angle_r} -{angle_r} 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 -{angle_r} {angle_r} 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / 0 -{angle_r} -{angle_r} 
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / {angle_r} 0 {angle_r}
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / {angle_r} 0 -{angle_r}
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / -{angle_r} 0 {angle_r}
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    cmo / create / mo_tmp / / / line
    copypts / mo_tmp / mo_line
    cmo / select / mo_tmp
    trans / 1 0 0 / 0. 0. 0. / -{angle_r} 0 -{angle_r}
    copypts / mo_well / mo_tmp
    cmo / delete / mo_tmp 

    ## Could add more permutations, but this looks good enough right now
    ## JDH 9 Sept. 2020

    ################## DEBUG ########################### 
    # dump / well_pts.inp / mo_well
    ################## DEBUG ########################### 

    # filter out point that are too close
    cmo / select / mo_well
    filter / 1 0 0 / {0.1*r}
    rmpoint / compress
    cmo / setatt / mo_well / imt / 1 0 0 / 1

    # connect the point cloud and make a volume mesh
    connect / delaunay
    resetpts / itp

    ################## DEBUG ########################### 
    # dump / well_{well["name"]}.inp / mo_well
    ################## DEBUG ########################### 

    # add edge_max attribute and remove elements with big edges
    quality / edge_max / y
    eltset /big/ edgemax / gt / {np.sqrt(2)*r}
    cmo / setatt / mo_well / itetclr /  eltset, get, big / 2
    rmmat / 2 
    rmpoint / compress

    dump / well_{well["name"]}_volume.inp / mo_well

    ################## DEBUG ########################### 
    # # extract the surface of the well 
    # # This is done to remove internal points and reduce
    # # the total number of elements in the mesh
    # # This speeds up the intersection checking later on
    # # I couldn't get this to work in a robust way.
    # # There were some weird LaGriT errors if I deleted 
    # # mesh object.
    # # Works if we stop before this, but I'm leaving it to 
    # # revisit if need be. 
    # # JDH 10/9/2020

    # extract / surfmesh / 1,0,0 /mo_shell / mo_well
    # cmo / select / mo_shell
    # cmo / delete / mo_well

    # ################## DEBUG ########################### 
    # dump / well_{well["name"]}_shell.inp / mo_shell
    # ################## DEBUG ########################### 

    # # Copy the surface of the well into a tet mesh
    # cmo / create / mo_well2 / / / tet
    # copypts / mo_well2 / mo_shell 
    # cmo / select / mo_well2
    # # cmo / delete / mo_shell

    # # filter out point that are too close
    # filter / 1 0 0 / {0.1*r}
    # rmpoint / compress
    # cmo / setatt / mo_well2 / imt / 1 0 0 / 1

    # # connect the point cloud and make a volume mesh
    # connect / delaunay
    # resetpts / itp

    # # add edge_max attribute and remove elements with big edges
    # quality / edge_max / y
    # eltset /big/ edgemax / gt / {np.sqrt(2)*r}
    # cmo / setatt / mo_well2 / itetclr /  eltset, get, big / 2
    # rmmat / 2 
    # rmpoint / compress

    # # write out final well mesh
    # dump / well_{well["name"]}_volume.inp / mo_well2

    finish

    """
    # Write LaGriT commands to file
    with open(f"expand_well_{well['name']}.lgi", "w") as fp:
        fp.write(lagrit_script)
        fp.flush()

    # Execute LaGriT
    mh.run_lagrit_script(f"expand_well_{well['name']}.lgi",
                         output_file=f"expand_well_{well['name']}",
                         quiet=False)

    print("--> Expanding well complete.")


def get_well_zone(well, inp_file):
    """Identifies nodes in a DFN for nodes the intersect a well with radius r [m]
    First, all elements that intersect the well are identified. 
    Second, all nodes of those elements are tagged. 
    Third, that collection of nodes are dumped as a zone file (well_{well["name"]}.zone)

    Parameters    
    -----------
        self : object
            DFN Class
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                File format:  
                x0 y0 z0
                x1 y1 z1
                ...
                xn yn zn

            well["r"] : float 
                radius of the well

    Returns
    --------
        None

    Notes
    --------
        None
        
    """
    # # if the well has not been converted to AVS, do that first
    # if not os.path.isfile(f"well_{well['name']}_line.inp"):
    #     convert_well_to_polyline_avs(well,h)
    # # if the well has not been expanded
    # if not os.path.isfile(f"well_{well['name']}_volume.inp"):
    #     expand_well(well)

    lagrit_script = f"""

# read in well volume
read / well_{well["name"]}_volume.inp / mo_well

# read in DFN 
read / {inp_file} / mo_dfn

# find intersecting cells
cmo / select / mo_dfn
intersect_elements / mo_dfn / mo_well / well_{well["name"]}_inter 

eltset / ewell / well_{well["name"]}_inter / gt / 0

# dump dfn mesh with intersections tagged
#dump / avs / {inp_file[:-3]}_tagged.inp / mo_dfn

# gather nodes of intersecting cells
pset / well_{well["name"]} / eltset / ewell

# dump nodes from intersecting cells
pset / well_{well["name"]} / zone / well_{well["name"]}.zone

finish

"""
    # Write LaGriT commands to file
    with open(f"get_well_{well['name']}_zone.lgi", "w") as fp:
        fp.write(lagrit_script)
        fp.flush()

    # Execute LaGriT
    mh.run_lagrit_script(f"get_well_{well['name']}_zone.lgi",
                         output_file=f"create_well_{well['name']}",
                         quiet=False)

    with open(f"well_{well['name']}.zone", "r") as fp:
        number_of_nodes = int(fp.readlines()[3])
        if number_of_nodes > 0:
            print(f"--> There are {number_of_nodes} nodes in the well zone")
        else:
            print("--> WARNING!!! The well did not intersect the DFN!!!")


def find_well_intersection_points(self, wells):
    """ Identifies points on a DFN where the well intersects the network. 
    These points are used in meshing the network to have higher resolution  in the mesh in these points.
    Calls a sub-routine run_find_well_intersection_points. 

    Parameters    
    -----------
        self : object
            DFN Class
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well

    Returns
    --------
        None

    Notes
    --------
        Wells can be a list of well dictionaries.
        Calls the subroutine run_find_well_intersection_points to remove redundant code.

    """
    # check for reduced mesh, if it doesn't exists, make it
    print("--> Checking for reduced_mesh.inp")
    if not os.path.isfile("reduced_mesh.inp"):
        print("--> reduced_mesh.inp not found. Creating it now.")
        self.mesh_network()
    else:
        print("--> reduced_mesh.inp found. Moving on.")

    # if using a single well
    if type(wells) is dict:
        run_find_well_intersection_points(wells, self.h)
    # using a list of wells, loop over them.
    elif type(wells) is list:
        for well in wells:
            run_find_well_intersection_points(well, self.h)

    # Run cross check
    cross_check_pts(self.h)


def run_find_well_intersection_points(well, h):
    """ Runs the workflow for finding the point of intersection of the DFN with the well. 

    Parameters    
    -----------
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well
        h : float
            Minimum h length scale in the network

    Returns
    --------
        None

    Notes
    --------
        This function was designed to minimize redundancy in the workflow. It's called
        within find_well_intersection_points()
    """

    print(f"\n\n--> Working on well {well['name']}")

    # 1) convert well into polyline AVS
    if not os.path.isfile(f"well_{well['name']}_line.inp"):
        convert_well_to_polyline_avs(well, h)

    # run LaGriT scripts to dump information
    find_segments(well)

    well_point_of_intersection(well)


def find_segments(well):
    """ LaGriT script to identify the points of intersection between the DFN and the well.

    Parameters    
    -----------
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well

    Returns
    --------
        None

    Notes
    --------
        points of intersection are written into the avs file well_{well['name']}_intersect.inp
        
        OUTPUT: well_segments_intersect.inp is a subset of the well line segments that intersect fractures.
                 The segments are tagged so itetclr and imt are set to the value of the fracture they intersect.
    """

    lagrit_script = f"""
#
# OUTPUT: intersected_fracture.list tells you the list of fractures intersected by the well.
# OUTPUT: well_segments_intersect.inp is a subset of the well line segments that intersect fractures.
#         The segments are tagged so itetclr and imt are set to the value of the fracture they intersect.
#
define / INPUT_DFN  / reduced_mesh.inp
define / INPUT_WELL / well_{well['name']}_line.inp
define / OUTPUT_WELL_SEGMENTS / well_{well['name']}_intersect.inp
# define / OUTPUT_FRACTURE_LIST / {well['name']}_fracture.list
#
read / avs / INPUT_DFN  / mo_tri
read / avs / INPUT_WELL / mo_line
#
# Find the triangles of the DFN mesh that intersect the well lines.
# Get rid of all the non-intersecting triangles.
#
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect
#
# dump / avs / reduced_reduced_mesh.inp / mo_tri
cmo / addatt / mo_tri / id_fracture / vint / scalar / nelements
cmo / copyatt / mo_tri / mo_tri / id_fracture / itetclr
# dump / avs / OUTPUT_FRACTURE_LIST / mo_tri / 0 0 0 1
#
# Find the segments of the well (line object) that intersect the fracture planes (triangles)
#
intersect_elements / mo_line / mo_tri / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_line / if_intersect
# BEGIN DEBUG
# dump / avs / OUTPUT_WELL_SEGMENTS / mo_line
# END DEBUG
#
# Reduce the size of the triangles so interpolation works.
#
cmo / select / mo_tri
# Refine 2**7  128
refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

refine2d
intersect_elements / mo_tri / mo_line / if_intersect
eltset / e_not_intersect / if_intersect / eq / 0
rmpoint / element / eltset get e_not_intersect
rmpoint / compress
cmo / DELATT / mo_tri / if_intersect

# BEGIN DEBUG
# dump / avs / tmp_refine.inp / mo_tri
# END DEBUG

interpolate / voronoi / mo_line itetclr / 1 0 0 / mo_tri imt
interpolate / voronoi / mo_line imt     / 1 0 0 / mo_tri imt

cmo / modatt / mo_line / itp / ioflag / l
cmo / modatt / mo_line / icr / ioflag / l
cmo / modatt / mo_line / isn / ioflag / l

dump / avs / OUTPUT_WELL_SEGMENTS / mo_line

finish


"""
    # Write LaGriT commands to file
    with open(f"find_well_{well['name']}_segment.lgi", "w") as fp:
        fp.write(lagrit_script)
        fp.flush()

    # Execute LaGriT
    mh.run_lagrit_script(f"find_well_{well['name']}_segment.lgi",
                         output_file=f"find_well_{well['name']}_segment",
                         quiet=False)


def well_point_of_intersection(well):
    """ Takes the well points found using find_segments and projects the points onto the fracture plane. These points are written into well_points.dat file. During meshing, these points are read in and a higher resolution mesh is created near by them. well_points.dat has the format

    fracture_id x y z
    ...

    for every intersection point. 

    Parameters    
    -----------
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well

    Returns
    --------
        None

    Notes
    --------

    """

    print(f"--> Finding well points on DFN for {well['name']}")
    # create file to keep well points if it doesn't exist. Otherwise set to append.
    if not os.path.isfile("well_points.dat"):
        fwell = open("well_points.dat", "w")
        fwell.write("fracture_id x y z\n")
    else:
        fwell = open("well_points.dat", "a")

    well_line_file = f"well_{well['name']}_intersect.inp"

    pts, elems, fracture_list = get_segments(well_line_file)

    if len(fracture_list) == 0:
        print(
            f"\n--> WARNING!!! The well {well['name']} did not intersect the DFN!!!\n"
        )

    for elem in elems:  # Parameterize the line center of the well
        l0 = np.zeros(3)
        l0[0] = pts[elem["pt1"] - 1]["x"]
        l0[1] = pts[elem["pt1"] - 1]["y"]
        l0[2] = pts[elem["pt1"] - 1]["z"]
        l1 = np.zeros(3)
        l1[0] = pts[elem["pt2"] - 1]["x"]
        l1[1] = pts[elem["pt2"] - 1]["y"]
        l1[2] = pts[elem["pt2"] - 1]["z"]
        l = l1 - l0

        f = elem["frac"]
        # get the plane on which the fracture lies
        n = get_normal(f)
        p0 = get_center(f)
        R = rotation_matrix(n, [0, 0, 1])

        # find the point of intersection between the well line and the plane
        d = np.dot((p0 - l0), n) / (np.dot(l, n))
        p = l0 + l * d
        v = rotate_point(p, R)
        fwell.write(f"{f} {v[0]} {v[1]} {v[2]}\n")
    fwell.close()


def cross_check_pts(h):
    """ Sometimes multiple points of intersection are identified on the same fracture. This can occur if the discretized well has points close to the fracture plane. This function walks through well_points.dat and removes duplicate points that are within h of one another and on the same fracture plane. 


    Parameters    
    -----------
        h : float
            Minimum length scale in the network.

    Returns
    --------
        None

    Notes
    --------
        None
    """

    print("\n--> Cross Checking well points")
    pts = np.genfromtxt("well_points.dat", skip_header=1)
    num_pts, _ = np.shape(pts)

    # Walk through well points and see if they are too close together,
    # This can happen due to machine precision in LaGriT.
    # We only keep 1 point per fracture per well.
    remove_idx = []
    for i in range(num_pts):
        fracture_number = pts[i, 0]
        for j in range(i + 1, num_pts):
            # Check if points are on the same fracture to reduce number of distance checks
            if fracture_number == pts[j, 0]:
                dist = abs(pts[i, 1] - pts[j, 1]) + abs(
                    pts[i, 2] - pts[j, 2]) + abs(pts[i, 3] - pts[j, 3])
                # if the points are closure that h/2, mark one to be removed.
                if dist < h / 2:
                    remove_idx.append(j)

    # Find the id of those points to keep
    keep_pt_indes = list(set(range(num_pts)) - set(remove_idx))
    # keep only those points
    pts = pts[keep_pt_indes]
    num_pts = len(pts)
    # write to file
    # os.remove("well_points.dat")
    with open("well_points.dat", "w") as fwell:
        fwell.write("fracture_id x y z\n")
        for i in range(num_pts):
            fwell.write(f"{int(pts[i,0])} {pts[i,1]} {pts[i,2]} {pts[i,3]}\n")
    print("--> Cross Checking Complete")


def get_segments(well_line_file):
    """ Parses well_line_file (avs) to get point information, element information, and list of fractures that intersect the well.

    Parameters    
    -----------
        well_line_file : string
            filename of well_line_file written by find_segments()

    Returns
    --------
        pts : list
            list of dictionaries of intersection points. dictionary contains fracture id and x,y,z coordinates
        elems: list of dictionaries
            Information about elements of the discretized well that intersect the DFN
        fracture_list : list
            list of fractures that the well intersects

    Notes
    --------
        None
    """

    with open(well_line_file, "r") as fp:
        header = fp.readline().split()
        num_pts = int(header[0])
        num_elem = int(header[1])
        pts = []
        for i in range(num_pts):
            pt = fp.readline().split()
            tmp = {"id": None, "x": None, "y": None, "z": None}
            tmp["id"] = int(pt[0])
            tmp["x"] = float(pt[1])
            tmp["y"] = float(pt[2])
            tmp["z"] = float(pt[3])
            pts.append(tmp)
        elems = []
        for i in range(num_elem):
            elem = fp.readline().split()
            tmp = {"pt1": None, "pt2": None, "frac": None}
            tmp["pt1"] = int(elem[3])
            tmp["pt2"] = int(elem[4])
            tmp["frac"] = int(elem[1])
            elems.append(tmp)
    # get fracture list
    fracture_list = []
    for i in range(num_elem):
        if not elems[i]["frac"] in fracture_list:
            fracture_list.append(elems[i]["frac"])

    return pts, elems, fracture_list


def get_normal(self, fracture_id):
    """ Returns Normal vector of a fracture

    Parameters    
    -----------
        fracture_id : int
            fracture number

    Returns
    --------
        normal : numpy array
            normal vector of a fracture

    Notes
    --------
        None
    """

    normals = self.normal_vectors #np.genfromtxt("normal_vectors.dat")
    return normals[fracture_id - 1, :]


def get_center(fracture_id):
    """ Returns center of a fracture

    Parameters    
    -----------
        fracture_id : int
            fracture number

    Returns
    --------
        points : numpy array
            x,y,z coordinates of a fracture

    Notes
    --------
        None
    """
    with open('translations.dat') as old, open('points.dat', 'w') as new:
        old.readline()
        for line in old:
            if not 'R' in line:
                new.write(line)
    points = np.genfromtxt('points.dat', skip_header=0, delimiter=' ')
    return points[fracture_id - 1, :]


def rotation_matrix(normalA, normalB):
    """ Create a Rotation matrix to transform normal vector A to normal vector B

    Parameters    
    -----------
        normalA : numpy array
            normal vector
        normalB : numpy array
            normal vector
              

    Returns
    --------
        R : numpy array
            Rotation matrix

    Notes
    --------
        None
    """
    # Check if normals are the same.
    comparison = normalA == normalB
    equal_arrays = comparison.all()

    # If they are equal, Return the Identity Matrix
    if equal_arrays:
        R = np.zeros(9)
        R[0] = 1
        R[1] = 0
        R[2] = 0
        R[3] = 0
        R[4] = 1
        R[5] = 0
        R[6] = 0
        R[7] = 0
        R[8] = 1
    # If they are not equal, construct and return a Rotation Matrix
    else:

        xProd = np.cross(normalA, normalB)
        sin = np.sqrt(xProd[0] * xProd[0] + xProd[1] * xProd[1] +
                      xProd[2] * xProd[2])
        cos = np.dot(normalA, normalB)
        v = np.zeros(9)
        v = [
            0, -xProd[2], xProd[1], xProd[2], 0, -xProd[0], -xProd[1],
            xProd[0], 0
        ]
        scalar = (1.0 - cos) / (sin * sin)
        vSquared = np.zeros(9)
        vSquared[0] = (v[0] * v[0] + v[1] * v[3] + v[2] * v[6]) * scalar
        vSquared[1] = (v[0] * v[1] + v[1] * v[4] + v[2] * v[7]) * scalar
        vSquared[2] = (v[0] * v[2] + v[1] * v[5] + v[2] * v[8]) * scalar
        vSquared[3] = (v[3] * v[0] + v[4] * v[3] + v[5] * v[6]) * scalar
        vSquared[4] = (v[3] * v[1] + v[4] * v[4] + v[5] * v[7]) * scalar
        vSquared[5] = (v[3] * v[2] + v[4] * v[5] + v[5] * v[8]) * scalar
        vSquared[6] = (v[6] * v[0] + v[7] * v[3] + v[8] * v[6]) * scalar
        vSquared[7] = (v[6] * v[1] + v[7] * v[4] + v[8] * v[7]) * scalar
        vSquared[8] = (v[6] * v[2] + v[7] * v[5] + v[8] * v[8]) * scalar
        R = np.zeros(9)
        R[0] = 1 + v[0] + vSquared[0]
        R[1] = 0 + v[1] + vSquared[1]
        R[2] = 0 + v[2] + vSquared[2]
        R[3] = 0 + v[3] + vSquared[3]
        R[4] = 1 + v[4] + vSquared[4]
        R[5] = 0 + v[5] + vSquared[5]
        R[6] = 0 + v[6] + vSquared[6]
        R[7] = 0 + v[7] + vSquared[7]
        R[8] = 1 + v[8] + vSquared[8]

    return R


def rotate_point(p, R):
    """ Apply Rotation matrix R to the point p

    Parameters    
    -----------
        p : numpy array
            point in 3D space
        R : numpy array
            Rotation matrix
    Returns
    --------
        v : numpy array
            The point p with the rotation matrix applied

    Notes
    --------
        None
    """
    v = np.zeros(3)
    v[0] = p[0] * R[0] + p[1] * R[1] + p[2] * R[2]
    v[1] = p[0] * R[3] + p[1] * R[4] + p[2] * R[5]
    v[2] = p[0] * R[6] + p[1] * R[7] + p[2] * R[8]
    return v


def cleanup_wells(self, wells):
    """ Moves working files created while making wells into well_data directory

    Parameters    
    -----------
        self : object
            DFN Class
        well:
            dictionary of information about the well. Contains the following:

            well["name"] : string 
                name of the well

            well["filename"] : string 
                filename of the well coordinates. "well_coords.dat" for example.
                 Format is :
                 x0 y0 z0
                 x1 y1 z1
                 ...
                 xn yn zn

            well["r"] : float 
                radius of the well

    Returns
    --------
        None

    Notes
    --------
        Wells can be a list of well dictionaries
    """
    print("--> Cleaning up well files: Starting")

    if not os.path.isdir("well_data"):
        os.mkdir("well_data")

    files = ["well_{0}_line.inp", "expand_well_{0}.lgi", \
        "well_{0}_volume.inp","expand_well_{0}.out",\
        "get_well_{0}_zone.lgi", "create_well_{0}.out",\
        "well_{0}_intersect.inp","create_well_{0}.dump",\
        "create_well_{0}.log"]

    if type(wells) is dict:
        well = wells
        for file in files:
            try:
                shutil.move(file.format(well['name']),
                        "well_data/" + file.format(well['name']))
            except:
                print("Error moving " + file.format(well['name']))
                pass


    if type(wells) is list:
        for well in wells:
            for file in files:
                try:
                    shutil.move(file.format(well['name']),
                                "well_data/" + file.format(well['name']))
                except:
                    print("Error moving " + file.format(well['name']))
                    pass
    print("--> Cleaning up well files: Complete")

def combine_well_boundary_zones(self, wells):
    """ Processes zone files for particle tracking. All zone files are combined into allboundaries.zone 
    
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
    # If there is only 1 well, make a symbolic link
    if type(wells) is dict:
        os.symlink(f"well_{well['name']}.zone", "well_nodes.zone")

    if type(wells) is list:
        number_of_wells = len(wells)
        fall = open("well_nodes.zone", "w")
        for index, well in enumerate(wells):
            if index == 0:
                print(f"Working on well {well['name']}")
                fzone = open(f"well_{well['name']}.zone", "r")
                lines = fzone.readlines()
                lines = lines[:-2]
                fall.writelines(lines)
            if index > 0 and index < number_of_wells - 1:
                print(f"Working on well {well['name']}")
                fzone = open(f"well_{well['name']}.zone", "r")
                lines = fzone.readlines()
                lines = lines[1:-2]
                lines[0] = f"{index+1:06d}\t\t{well['name']}\n"
                fzone.close()
                fall.writelines(lines)
            if index == number_of_wells - 1:
                print(f"Working on well {well['name']}")
                fzone = open(f"well_{well['name']}.zone", "r")
                lines = fzone.readlines()
                lines = lines[1:]
                lines[0] = f"{index+1:06d}\t\t{well['name']}\n"
                fzone.close()
                fall.writelines(lines)
        fall.close()
