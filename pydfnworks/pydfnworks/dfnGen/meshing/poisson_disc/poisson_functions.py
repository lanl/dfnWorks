# func.py
from pydfnworks.dfnGen.meshing.poisson_disc import poisson_class as pc
from pydfnworks.general.logging import local_print_log, print_log

from numpy import arange, array, ogrid, nonzero, zeros, append
from random import random, shuffle
from math import sqrt, floor, ceil, cos, sin, pi
from matplotlib import pyplot as plt
from scipy.sparse import lil_matrix
import timeit
import pickle

#from memory_profiler import profile
#######################################################################
#######################################################################
"""
This file contains all functions called by main.py
The contained functions in order are:

*called directly by main:
    - main_init()
    - intersect_sample()
    - main_sample()
    - search_undersampled_cells()
    - dump_coordinates()
    - plot_coordinates()
    - print()

*called by other functions:
    - neighbor_cell()
    - neighbor_grid_init()
    - new_candidate()
    - accept_candidate()
    - exclusion_radius()
    - intersect_distance()
    - not_in_domain()
    - neighboring_cells()
    - read_vertices()
    - read_intersections()
    - boundary_sampling()
    - sampling_along_line()
    - intersect_cell()
    - intersect_grid_init()
    - intersect_mark_start_cells()
    - intersect_direction()
    - intersect_mark_next_cells()
    - intersect_crossing_cell_wall()
    - intersect_cell_sign()
    - occupancy_cell()
    - occupancy_undersampled()
    - occupancy_grid_update()
    - occupancy_mark()
    - resample()
    - lower_boundary()
    - upper_boundary()
    - distance()
    - distance_sq()
    - norm_sq()
    - dot_product()
"""

#######################################################################
#######################################################################
###########___Functions called directly by main.py____#################


#@profile
def main_init(c):  # polygons, intersections):
    """ Reads inputs and initializes variables in c, i.e. initialized the polygon,
    the intersections, samples along the boundary and initializes
    neighbor-grid.

    Parameters
    ---------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        None

    Notes
    -----

        """

    # initializes all geometry variables
    c.vertices = read_vertices(c, c.path_poly)
    c.intersect_endpts = read_intersections(c, c.path_inter)

    if c.well_flag:
        well_pts = read_well_points(c)
        for i in range(len(well_pts)):
            c.intersect_endpts.append(well_pts[i])
            #print(c.intersect_endpts)

    intersect_grid_init(c)
    c.coordinates = boundary_sampling(c)
    c.neighbor_grid = neighbor_grid_init(c)
    c.no_of_nodes = len(c.coordinates)


#####################################################################


#@profile
def main_sample(c):
    """ Runs over already accepted nodes and samples new candidates  on an
    annulus around them. valid candidates are added to c.coordinates
    c.k candidates are sampled at once. If all k
    are rejected, move on to next already accepted node. Terminate
    after their are no new already accepted nodes.


    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        None

    Notes
    -----
        Proceeds from, where it terminated the previous time, if called
        more than once.
    """
    while c.current_node < c.no_of_nodes:  # sample around all accepted nodes
        next_node = False
        while not next_node:
            next_node = True
            for j in range(0, c.k):  # sample k candidates around node
                candidate = new_candidate(c, c.coordinates[c.current_node])
                if accept_candidate(c, candidate):
                    c.no_of_nodes = c.no_of_nodes + 1
                    next_node = False  # stay at  node unless all k candidates are rejected
        c.current_node = c.current_node + 1


#######################################################################


#@profile
def search_undersampled_cells(c):
    """ Creates the occupancy-grid, searches for empty cells in it and
    uniformly samples candidates in those empty cells. Accepted cells
    are added to c.coordinates.

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        None

    Notes
    -----
    """

    undersampled_x, undersampled_y = occupancy_undersampled(c)
    # indices of empty cells
    no_of_undersampled = len(undersampled_x)
    random_permutation = [m for m in range(0, no_of_undersampled)]
    shuffle(random_permutation)
    # go through empty cells in random order
    # (due to the way empty cells defined, nodes sampled into
    # empty cells only conflict with each other not any nodes
    # sampled in main_sample)
    while random_permutation:
        random_integer = random_permutation.pop()
        candidate = resample(c, undersampled_x[random_integer],
                             undersampled_y[random_integer])
        if accept_candidate(c, candidate):
            c.no_of_nodes = c.no_of_nodes + 1


#######################################################################
def dump_coordinates(c, output_file="points.xyz"):
    """ Prints accepted coordinates to file

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        output_file : string
            coordinates will be printed to a file with this name

    Returns
    ---------
        None

    Notes
    -----
        None

        """

    col_format = "{:<30}" * 3 + "\n"
    z = c.z_plane
    with open(output_file, 'w') as file_o:
        for element in c.coordinates:
            file_o.write(col_format.format(*[element[0], element[1], z]))


#######################################################################


def plot_coordinates(c, output_file=""):
    """ Plots accepted nodes to screen or file

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        output_file : string
            name of the file in which c.coordinated-plot will be saved.
            c.coordinates are plotted to screen, if empty.

    Returns
    ---------
        None

    Notes
    -----
        creates the file "output_file", if this string is not empty.

    """

    xcoord = [x[0] for x in c.coordinates]
    ycoord = [x[1] for x in c.coordinates]
    plt.axis([
        c.x_min - c.max_exclusion_radius, c.x_max + c.max_exclusion_radius,
        c.y_min - c.max_exclusion_radius, c.y_max + c.max_exclusion_radius
    ])
    plt.scatter(xcoord, ycoord, s=.5)
    if len(output_file) == 0:
        plt.show()
    else:
        plt.savefig(output_file + 'png', dpi=150)
        plt.close()


#######################################################################
#############___Functions related to look up grid___###################


def neighbor_cell(c, X):
    """ Returns look up-Grid index of the point X

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            2D coordinates of a point inside the neighbor-grid

    Returns
    ---------
        (x,y) : tuple(int,int)
            horizontal and vertical neighbor-cell number

    Notes
    -----

    """
    x = floor((X[0] - c.x_min) * c.neighbor_cell_size_inv)
    y = floor((X[1] - c.y_min) * c.neighbor_cell_size_inv)
    return x, y


#######################################################################


def neighbor_grid_init(c):
    """ Initializes background grid

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        neighbor_grid : ndarray(int)
            array, where each components corresponds to a neighbor cell.
            0, if corresponding cell is empty
            i, if c.coordinate[i-1] occupies corresponding cell.

    Notes
    -----

    """

    #!!!consider using sparse matrix instead to save space
    #!!!slicing might be slower though

    c.no_horizontal_neighbor_cells = ceil(
        (c.x_max - c.x_min) * c.neighbor_cell_size_inv)
    c.no_vertical_neighbor_cells = ceil(
        (c.y_max - c.y_min) * c.neighbor_cell_size_inv)
    neighbor_grid = zeros((c.no_horizontal_neighbor_cells + 1,
                           c.no_vertical_neighbor_cells + 1)).astype(int)
    for node_number in range(0, len(c.coordinates)):
        neighbor_grid[neighbor_cell(
            c, c.coordinates[node_number])] = node_number + 1
        # every occupied cells is labelled with the node-number (start at 1)
        # of the node occupying it. empty cells are 0.
    return neighbor_grid


#######################################################################
###########___Functions related to primary Sampling___#################


def new_candidate(c, X):
    """ Returns a random point in a annular neighborhood of X

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            first two entries: x,y-coordinates of a already accepted node.
            last entry: local exclusion_radius of that node.

    Returns
    ---------
        candidate : ndarray(float)
            x,y- coordinates of a potential new node.

    Notes
    -----

    """
    radius = random() * c.max_exclusion_radius + X[2]
    # last entry of an element of c.coordinates
    # contains its local exclusion radius
    # Note: setting radius to X[2]+epsilon gives denser samplings
    # resulting in a per-node-speedup
    angle = random() * pi * 2
    candidate = X[0:2] + [radius * cos(angle), radius * sin(angle)]
    return candidate


#######################################################################


def accept_candidate(c, candidate):
    """ accepts a candidate p, if no conflicts with domain or already accepted nodes arise

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        candidate : ndarray(float)
            x,y-coordinates of a potential new node

    Returns
    ---------
        True/False : bool
            True, if candidate is accepted as new node
            False otherwise

    Notes
    -----
        If the candidate is accepted, it is added to c.coordinates
        (including its local_exclusion_radius) and the neighbor grid
        is updated.

    """

    # Checks if candidate is within rectangle defined by polygon
    if candidate[0] < c.x_min:
        return False
    if candidate[0] > c.x_max:
        return False
    if candidate[1] < c.y_min:
        return False
    if candidate[1] > c.y_max:
        return False
        # neighbor_grid[neigbor_cell(...)] causes error if candidate
        # is outside of rectangle bounded by x/y_min/max.

    # Checks if neighbor-cell is already occupied
    candidates_neighbor_cell = neighbor_cell(c, candidate)
    if c.neighbor_grid[candidates_neighbor_cell] != 0:
        return False

    # Checks if p is within polygon
    if not in_domain(c, candidate):
        return False

    # Checks if any closeby points conflict
    candidates_ex_rad = exclusion_radius(c, candidate)
    candidates_ex_rad_sq = candidates_ex_rad**2
    for node_number in neighboring_cells(c, candidates_neighbor_cell,
                                         candidates_ex_rad):

        closeby_node = c.coordinates[node_number - 1]

        # last entry contains loc. ex_rad.
        closeby_ex_rad_sq = closeby_node[2]**2
        if distance_sq(candidate, closeby_node) < min(candidates_ex_rad_sq,
                                                      closeby_ex_rad_sq):
            return False

    # Appends candidate and its loc. ex-rad to accepted nodes and updates
    # neighbor-cells
    c.coordinates.append(append(candidate, candidates_ex_rad))
    c.neighbor_grid[candidates_neighbor_cell] = c.no_of_nodes + 1
    return True


#######################################################################


def exclusion_radius(c, X):
    """ returns the local min-distance of particle X

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            first two entries: x,y-coordinates of a node

    Returns
    ---------
        local_exclusion_radius : float
            exclusion radius at point X
    Notes
    -----
        X can have more than 2 entries. Anything, but the first
        two will be ignored

        """

    try:
        closeby_intersections = c.intersect_cells[intersect_cell(c, X)]
        # if accessing c.intersect_cells raises a KeyError nothing was
        # assigned to the key intersect_cell(c,X) i.e. no intersection is
        # close enough to influence the exclusion radius at X
        # otherwise a list of intersection numbers is returned.
        closest_intersect_distance_sq = intersect_distance_sq(
            c, X, closeby_intersections)
        if closest_intersect_distance_sq >= c.intersect_range_sq:
            local_exclusion_radius = c.max_exclusion_radius
            return local_exclusion_radius
        else:
            D = sqrt(closest_intersect_distance_sq)
            # delaying this sqrt till here, means many cases didn't pass the
            # if-statements reducing the overall times a sqrt is calculated
            local_exclusion_radius = max(c.A * (D - c.F * c.H) + .5 * c.H,
                                         .5 * c.H)
            return local_exclusion_radius
    except KeyError:
        local_exclusion_radius = c.max_exclusion_radius
        return local_exclusion_radius


###################################################################


def intersect_distance_sq(c, X, closeby_intersections):
    """ returns square distance to closest intersection

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            x,y-coordinates of a node
        
        closeby_intersections : list(int)
            numbers of intersections, that pass X in a distance of 2*(H*(R+F)) or less

    Returns
    ---------
        suqare_dist : float
            square of the distance to the closest intersection
            of 'inf', if no intersection is closeby.

    Notes
    -----
    """
    possible_output = []  # min of this list will be output
    for i in closeby_intersections:
        intersect_start = c.intersect_endpts[2 * i]
        intersect_end = c.intersect_endpts[2 * i + 1]
        projection_on_intersection = dot_product(
            X - intersect_start, intersect_end - intersect_start)
        length_of_intersection_sq = distance_sq(intersect_end, intersect_start)
        if projection_on_intersection <= 0 or projection_on_intersection >= length_of_intersection_sq:
            # If one of the endpoints is closest to X
            possible_output = possible_output + \
                [distance_sq(intersect_start, X), distance_sq(intersect_end, X)]
            # put distances to either end point on poss.output list
        else:
            dist_to_line_sq = norm_sq((X - intersect_start) -
                                      (intersect_end - intersect_start) *
                                      projection_on_intersection /
                                      (length_of_intersection_sq))
            # square distance from point to infinite line defined by start and
            # end point
            possible_output.append(dist_to_line_sq)

    square_dist = min(possible_output)
    return square_dist


####################################################################


def in_domain(c, X):
    """ Tests if the node X is within the polyon defined by c.vertices.

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            x,y-coordinates of a node

    Returns
    ---------
        True/False : bool
            False if X lies within the polygon
            True otherwise
    
    Notes
    -----



    """
    # Checks if below lower bounding function
    i = c.last_x_min_index  # start at index of the vertex of the polygon
    # with the smalles y-value out of the vertices
    # with x-value x_min
    while c.vertices_x[i] < c.x_max:
        # Go through the x-coordinates of the  vertices along the lower
        # boundary to see between, which two the x-value of X lies
        # Remember vertices are ordered clockwise
        if X[0] >= c.vertices_x[i] and X[0] <= c.vertices_x[(i + 1) %
                                                            c.no_of_vertices]:
            if X[1] < c.vertices_y[i] + \
                    c.slope_lower_boundary[i] * (X[0] - c.vertices_x[i]):
                # See if the y-value of X lies below the lower boundary
                # Since the boundary is piecewise linear, it was enough
                # to find the two vertices in the previous step
                return False
            else:
                break
        i = (i + 1) % c.no_of_vertices

    # Checks if above upper bounding function
    i = c.first_x_min_index  # start at index of vertex of polygon
    # with highest y-value out of the vertices with
    # x-value x_min
    while c.vertices_x[i] < c.x_max:
        # Go through the x-coordinates of the  vertices along the upper
        # boundary to see between, which two the x-value of X lies
        # Remember vertices are ordered clockwise
        if X[0] >= c.vertices_x[i] and X[0] <= c.vertices_x[(i - 1) %
                                                            c.no_of_vertices]:
            if X[1] > c.vertices_y[i] + \
                    c.slope_upper_boundary[i] * (X[0] - c.vertices_x[i]):
                # See if the y-value of X lies above the upper boundary
                # Since the boundary is piecewise linear, it was enough
                # to find the two vertices in the previous step
                return False
            else:
                return True
        i = (i - 1) % c.no_of_vertices


#######################################################################


def neighboring_cells(c, center_cell, exclusion_radius):
    """ Returns the coordinate number of all non-empty cells neighboring
    the input-index

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        center_cell : ndarray(int)
            neighbor-cell index (x,y) of candidate
        
        exclusion_radius : float
            local exclusion radius of candidate

    Returns
    ---------
        closeby_nodes : list(int)
            node numbers of all close by nodes

    Notes
    -----

    """
    max_cell_distance = ceil(exclusion_radius * c.neighbor_cell_size_inv)
    # furthest number of cells a cell still containing a conflicting node
    # could be away in x or y-direction
    subgrid = c.neighbor_grid[
        max(center_cell[0] -
            max_cell_distance, 0):min(center_cell[0] + max_cell_distance +
                                      1, c.no_horizontal_neighbor_cells + 1),
        max(center_cell[1] -
            max_cell_distance, 0):min(center_cell[1] + max_cell_distance +
                                      1, c.no_vertical_neighbor_cells + 1)]
    # slice neighboring cells out of grid
    #sub=subgrid#.toarray()
    closeby_nodes = subgrid[nonzero(subgrid)]

    return closeby_nodes


#######################################################################
#################___Initializing functions___##########################
#@profile
def read_vertices(c, path_to_polygon):
    """ Reads polygon vertices from file, initializes all variables related to
    geometry of polygon (z_plane, x_min, x_max,y_min, y_max, lower and upper slope of polygon, ...)

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        path_to_polygon : string
            file containing coordinates of vertices

    Returns
    ---------
        vertices : list(ndarray(float))
            list of coordinates of the polygon vertices

    Notes
    -----

    """
    with open(path_to_polygon) as inputfile:
        lines = inputfile.readlines()
    c.no_of_vertices = int(lines[0].split()[0])
    vertices = [
        array([float(Y) for Y in X.split()[1:3]])
        for X in lines[1:1 + c.no_of_vertices]
    ]
    c.z_plane = float((lines[1]).split()[3])
    c.vertices_x = [X[0] for X in vertices]
    c.vertices_y = [X[1] for X in vertices]
    c.x_min, c.x_max = min(c.vertices_x), max(c.vertices_x)
    c.y_min, c.y_max = min(c.vertices_y), max(c.vertices_y)

    # Initialises upper and lower bound-functions for domain check
    c.first_x_min_index = c.vertices_x.index(c.x_min)
    # index of the vertex with the highest y-value out of all
    # vertices with x value x_min
    c.last_x_min_index = c.first_x_min_index
    # index of the vertex with lowest y-value out of all
    # vertices with x value x_min
    # using clockwise ordering of vertices to find those indices
    while c.vertices_x[(c.first_x_min_index - 1) %
                       c.no_of_vertices] == c.vertices_x[c.first_x_min_index]:
        c.first_x_min_index = (c.first_x_min_index - 1) % c.no_of_vertices
    while c.vertices_x[(c.last_x_min_index + 1) %
                       c.no_of_vertices] == c.vertices_x[c.last_x_min_index]:
        c.last_x_min_index = (c.last_x_min_index + 1) % c.no_of_vertices

    c.slope_lower_boundary = zeros(c.no_of_vertices)
    c.slope_upper_boundary = zeros(c.no_of_vertices)
    i = c.last_x_min_index
    while c.vertices_x[i] < c.x_max:
        c.slope_lower_boundary[i] = (c.vertices_y[
            (i + 1) % c.no_of_vertices] - c.vertices_y[i]) / (c.vertices_x[
                (i + 1) % c.no_of_vertices] - c.vertices_x[i])
        i = (i + 1) % c.no_of_vertices
    i = c.first_x_min_index
    while c.vertices_x[i] < c.x_max:
        c.slope_upper_boundary[i] = (c.vertices_y[
            (i - 1) % c.no_of_vertices] - c.vertices_y[i]) / (c.vertices_x[
                (i - 1) % c.no_of_vertices] - c.vertices_x[i])
        i = (i - 1) % c.no_of_vertices
    del lines
    return vertices


#######################################################################


#@profile
def read_intersections(c, path_to_intersections):
    """ reads Intersection endpoints from file

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        path_to_intersections : string
            file containing intersection points

    Returns
    ---------
        end_pts : list(ndarray(floats))
            list of coordinates of start and end points of intersections
            ordered by intersection:   [start_1,end_1,start_2,end_2,...]

    Notes
    -----
    sets neighbor_grid width to max_exclusion_radius/sqrt(2), if there's
    no intersections.


    """
    end_pts = []
    #short edges require smaller closer nodes to guarantee good triangles
    for i in range(c.no_of_vertices):
        if distance_sq(c.vertices[i], c.vertices[
            (i + 1) % c.no_of_vertices]) < c.max_exclusion_radius**2:
            if c.A != 0:
                edge = c.vertices[i] - c.vertices[(i + 1) % c.no_of_vertices]
                edge_length = sqrt(norm_sq(edge))
                orthogonal = array([-edge[0], edge[1]]) / edge_length
                shift = (edge_length - c.H * c.F) / c.A
            else:
                orthogonal = array[0, 0]
                shift = 0
            end_pts.append(c.vertices[i] + shift * orthogonal)
            end_pts.append(c.vertices[(i + 1) % c.no_of_vertices] +
                           shift * orthogonal)

    with open(path_to_intersections) as inputfile:
        lines = inputfile.readlines()
    if len(lines) != 0:
        line_0 = lines[0].split()
        no_of_pts = int(line_0[0])
        no_of_lines = int(line_0[1])
        no_of_intersections = no_of_pts - no_of_lines
        intersect_labels = [
            int(X.split()[2]) for X in lines[no_of_pts + no_of_lines + 4:]
        ]
        # .inp-file contains labels to which intersection a point belongs
        # listed after points, line-commands and 4 lines of text.
        first_line_intersect_j = 1
        for j in range(0, no_of_intersections):
            start_j = array(
                [float(Y) for Y in lines[first_line_intersect_j].split()[1:3]])
            # find first line that contains current label add it as start
            end_pts.append(start_j)
            last_line_intersect_j = no_of_pts - \
                intersect_labels[::-1].index(intersect_labels[first_line_intersect_j])
            # look backwards through the file to find last line with current
            # label
            end_j = array(
                [float(Y) for Y in lines[last_line_intersect_j].split()[1:3]])
            # add it as end
            end_pts.append(end_j)

            first_line_intersect_j = last_line_intersect_j + 1
            # next line has different label
    if end_pts == []:
        c.neighbor_cell_size = c.max_exclusion_radius / sqrt(2)
        c.neighbor_cell_size_inv = 1 / c.neighbor_cell_size
        # if there's no intersections, the neighbor-cells can be defined
        # via the max distance, saving time
    del lines
    return end_pts


def read_well_points(c):

    pts = []

    with open("well_points.dat", "r") as fwell:
        fwell.readline()  # ignore header (fracture_id, x, y, z)
        for line in fwell.readlines():
            if c.fracture_id == int(line.split()[0]):
                pt = zeros(2)
                pt[0] = float(line.split()[1])
                pt[1] = float(line.split()[2])
                pts.append(pt)
                pt[0] += c.H
                pt[1] += c.H
                pts.append(pt)
                del pt
    return pts


######################################################################
#@profile
def boundary_sampling(c):
    """ Samples points around the boundary

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        boundary_points : list(ndarray(float))
            coordinates of a poisson-disk sampling along
            the boundary of the polygon.
    Notes
    -----

    """

    # Could be written more efficient, but will only be called a few times
    # anyway

    boundary_points = []
    for i in range(0, c.no_of_vertices):
        #sampling along all line segments that make up the boundary
        prev_line = c.vertices[(i - 1) % c.no_of_vertices] - c.vertices[i]
        current_line = c.vertices[i] - c.vertices[(i + 1) % c.no_of_vertices]
        next_line = c.vertices[(i + 2) % c.no_of_vertices] - c.vertices[
            (i + 1) % c.no_of_vertices]

        cos_start_angle = dot_product(prev_line, current_line) / sqrt(
            norm_sq(prev_line) * norm_sq(current_line))
        cos_end_angle = dot_product(current_line, next_line) / sqrt(
            norm_sq(next_line) * norm_sq(current_line))

        r_start = max(exclusion_radius(c,
                                       c.vertices[i]), (cos_start_angle > .5) *
                      c.H * .25 / sqrt(1 - cos_end_angle**2))
        r_end = max(
            exclusion_radius(c, c.vertices[(i + 1) % c.no_of_vertices]),
            (cos_end_angle > .5) * c.H * .25 / sqrt(1 - cos_end_angle**2))
        #if angle between sides of the polygon are smaller than 60deg
        #the distance between points on the boundary needs to be considered
        #if the angle is biggher than 60deg it is sufficient to guarantee
        #appropriate distance to the vertices.

        if sqrt(norm_sq(current_line)) - r_start - r_end > 0:
            #is there space for at least two samples on the boundary?
            start = c.vertices[i] - r_start * \
                current_line / sqrt(norm_sq(current_line))
            end = c.vertices[(i + 1) % c.no_of_vertices] + \
                r_end * current_line / sqrt(norm_sq(current_line))
            if distance(start, end) > min(exclusion_radius(c, start),
                                          exclusion_radius(c, end)):

                boundary_points = boundary_points + \
                    sampling_along_line(c, start, end)
            else:
                #If just two samples on the boundary are already too close
                #pick random point between them instead
                r = random() * (sqrt(norm_sq(current_line)) - r_start - r_end)
                start = c.vertices[i] - (r_start + r) * \
                    current_line / sqrt(norm_sq(current_line))
                boundary_points.append(
                    append(start, exclusion_radius(c, start)))
        elif sqrt(norm_sq(current_line)) - r_start - r_end == 0:
            #just enough space for one sample on the boundary?
            start = c.vertices[i] - r_start * \
                current_line / sqrt(norm_sq(current_line))
            boundary_points.append(append(start, exclusion_radius(c, start)))
    vertices = [append(v, exclusion_radius(c, v)) for v in c.vertices]
    return vertices + boundary_points


#######################################################################


def sampling_along_line(c, x, y):
    """ Samples points on a line with min distance r and max distance 1.3r
    (Poisson disk sampling on a line)

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        x,y : ndarray(float)
            coordinates of start and end point of the line to be sampled

    Returns
    ---------
        line_sample : list(ndarray(float))
            coordinates of a Poisson disk sampling along the line from x to  y

    Notes
    -----
    choosing new points in distance between r and 1.3r is rather arbitrary.
    However greater than r is necessary to maintain Poisson-disk sampling
    and significantly greater distances  of boundary nodes
    decrease the quality of the triangulation.
    """

    previous_sample = x
    direction = (y - x) / distance(y, x)
    ex_rad = exclusion_radius(c, previous_sample)
    line_sample = [append(previous_sample, ex_rad)]
    while distance(previous_sample, y) > 2.3 * ex_rad:
        # distance to endpoint still large enough to use full range
        increment = .3 * random() * ex_rad + ex_rad
        previous_sample = previous_sample + direction * increment
        ex_rad = exclusion_radius(c, previous_sample)
        line_sample.append(append(previous_sample, ex_rad))
    ex_rad = min(exclusion_radius(c, previous_sample), exclusion_radius(c, y))
    while distance(previous_sample, y) >= 2 * ex_rad:
        # place for another sample, but in more restricted area
        increment = random() * (distance(previous_sample, y) -
                                2 * ex_rad) + ex_rad
        previous_sample = previous_sample + direction * increment
        ex_rad = min(exclusion_radius(c, previous_sample),
                     exclusion_radius(c, y))
        line_sample.append(append(previous_sample, ex_rad))
    line_sample.append(append(y, exclusion_radius(c, y)))
    return line_sample


#######################################################################
###########___Functions related to Intersection look up___#############


def intersect_cell(c, X):
    """ Returns Intersect-Grid index of the point X

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            x,y-coordinates of the point C

    Returns
    ---------
        x,y : int
            horizontal and vertical intersection_cell_index

    Notes
    -----
    """
    x = floor((X[0] - c.x_min) * c.intersect_grid_inv)
    y = floor((X[1] - c.y_min) * c.intersect_grid_inv)
    return x, y


#########################################################################


#@profile
def intersect_grid_init(c):
    """ Initialize Intersect-Grid, looks at all intersections as 
    directed arrows from start to end and marks cell that are crossed by it and neighboring cells

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        None

    Notes
    -----
        The domain is split into square-cells of side length intersect_range.
        The cells are numbered by integer indexes (i,j). This function add the
        number (i,j):m to the dictionary c.intersect_cells if the m-th intersection
        crosses the cell with index (i,j) are a neighboring cell.

    """
    c.intersect_cells = {}
    for intersect_number in range(0, int(len(c.intersect_endpts) / 2)):
        Start, End = c.intersect_endpts[
            2 * intersect_number], c.intersect_endpts[2 * intersect_number + 1]
        current_intersect_cell = intersect_cell(c, Start)
        final_intersect_cell = intersect_cell(c, End)
        intersect_mark_start_cells(c, current_intersect_cell, intersect_number)
        delta_x, delta_y = End[0] - Start[0], End[1] - Start[1]
        if delta_x != 0:
            y_intercept = Start[1] - Start[0] * delta_y / delta_x
        else:
            y_intercept = Start[0]
            # if the intersection is parallel to the y-axis, its x-value is
            # stored
        directions = intersect_direction(c, delta_x, delta_y)
        # Does intersection point north, west, northwest,... ?
        while (current_intersect_cell[0] != final_intersect_cell[0]
               or current_intersect_cell[1] != final_intersect_cell[1]):
            for direction in directions:
                if intersect_crossing_cell_wall(c, direction,
                                                current_intersect_cell,
                                                delta_x, delta_y, y_intercept):
                    current_intersect_cell = intersect_mark_next_cells(
                        c, direction, current_intersect_cell, intersect_number)
                    # next cell the intersection passes
                    break


#######################################################################


def intersect_mark_start_cells(c, center_cell, intersect_number):
    """ Adds the intersection number to the center cell and all its 8 neighbor cells in
    the dictionary c.intersect_cells. Marks 3x3 cells

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        center_cell : ndarrya(int)
            index-pair of an intersection-cell
        
        intersect_number : int
            contains the number of an intersection if the are enumerated starting at 1.

    Returns
    ---------

    Notes
    -----
        Adds the intersection number to the center cell and all its 8 neighbor cells in
        the dictionary c.intersect_cells
    """

    for j in range(0, 9):  # loop through 3x3 grid around center cell
        try:
            c.intersect_cells[center_cell[0] - 1 + floor(j / 3),
                              center_cell[1] - 1 +
                              (j % 3)].append(intersect_number)
            # if key already contains a list append current intersection number
            # else exception is raised and a list is created for that key.
        except BaseException:
            c.intersect_cells[center_cell[0] - 1 + floor(j / 3),
                              center_cell[1] - 1 +
                              (j % 3)] = [intersect_number]


#######################################################################


def intersect_direction(c, delta_x, delta_y):
    """ Determines the direction and intersection is pointing if interpreted as an arrow from start to end.( right, left, up, down, combinations possible)

    Parameters
    ---------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        delta_x/delta_y : float
            x/y distance between start and end point of an intersection

    Returns
    ---------
        directions : list(int)
            up to 2 numbers between 1 and 4 corresponding to the directions
            1-> right, 3->left, 2->up and 4->down.

    Notes
    -----
    This is used to determine which sides of a intersect-cell an intersection
    could cross.

    """

    directions = []
    if delta_x > 0:
        directions.append(1)  # right
    elif delta_x < 0:
        directions.append(3)  # left
    if delta_y > 0:
        directions.append(2)  # up
    elif delta_y < 0:
        directions.append(4)  # down
    return directions


#######################################################################


def intersect_mark_next_cells(c, direction, center_cell, intersect_number):
    """ Determines the next intersect-cell the current intersection is crossing
    and adds all neighboring cells of that cell to the dictionary
    c.intersect_cells.

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        direction : list(int)
            integer between 1 and 4 corresponding to directions
                right,left,up,down (1,3,2,4)
        
        center_cell : ndarray(int)
            index-pair of an intersection-cell
        
        intersect_number : int
            number of an intersection if they were enumerated starting at 1

    Returns
    ---------
        new_center_cell : ndarray(int)
            index-pair of the most recent cell known to be crossed by the
            current intersection

    Notes
    -----
        5 of the 8 neighboring cells of new_center_cell are already added to
        c.intersect_cells, so it is sufficient to only add the remaining 3.

    """

    x_shift = (direction % 2) * (-1)**(int((direction - 1) / 2))
    y_shift = ((direction - 1) % 2) * (-1)**(int(direction / 2) + 1)
    # x_shift =+-1 for left/right movement, y_shift =+-1 for up/down movement
    if x_shift == 0:
        for j in range(0, 3):
            # label the 3 cells below/above the 3x3 grid around current cell
            try:
                c.intersect_cells[center_cell[0] - 1 + j, center_cell[1] +
                                  2 * y_shift].append(intersect_number)
                # if the key for any of those cells already contains a list the
                # current intersection number is added otherwise an exception is
                # raised an a list is created for that key instead
            except BaseException:
                c.intersect_cells[center_cell[0] - 1 + j, center_cell[1] +
                                  2 * y_shift] = [intersect_number]
    else:
        for j in range(0, 3):
            # label the 3 cells left/right of the the 3x3 grid around current
            # cell
            try:
                c.intersect_cells[center_cell[0] + 2 * x_shift,
                                  center_cell[1] - 1 +
                                  j].append(intersect_number)
                # if the key for any of those cells already contains a list the
                # current intersection number is added otherwise an exception is
                # raised an a list is created for that key instead
            except BaseException:
                c.intersect_cells[center_cell[0] + 2 * x_shift,
                                  center_cell[1] - 1 + j] = [intersect_number]
    new_center_cell = center_cell + array([x_shift, y_shift])
    return new_center_cell


#######################################################################


def intersect_crossing_cell_wall(c, direction, current_cell, delta_x, delta_y,
                                 y_intercept):
    """ Determines if intersection crosses cell in given direction

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        direction : list(int)
            integer between 1 and 4 corresponding to the
            directions right,left,up,down (1,3,2,4)
        
        delta_x/delta_y : ndarray(float)
            x/y distance between start and end point of current intersection
        
        y_intercept : float
            y-value of the y-axis interception of the intersection if extended
            to an infinite line.
            x-value of the intersection, if it is parallel to the y-axis

    Returns
    ---------
        True/False : bool
            True if the two nodes of the current intersection-cell into the
            input direction are on different sides of the intersection
            (or if one of those nodes lies on the intersection), i.e. if the
            intersection crosses the side of the cell in that direction.
            False otherwise.

    Notes
    -----


     """

    cell_nodes_k = c.square_nodes[direction - 1:direction + 1, :]
    # c.square contains nodes of a unit square
    # we select the two nodes at the edge of the cell, that
    # bounds it in the direction the intersection is moving.
    square_node_1 = (array(current_cell) + cell_nodes_k[0, :]) * (c.R * c.H +
                                                                  c.F * c.H)
    square_node_2 = (array(current_cell) + cell_nodes_k[1, :]) * (c.R * c.H +
                                                                  c.F * c.H)
    # translates unit-square node into actual nodes of the cell
    return intersect_cell_sign(c, square_node_1 + array([c.x_min, c.y_min]),
                               square_node_2 + array([c.x_min, c.y_min]),
                               delta_x, delta_y, y_intercept)


#######################################################################


def intersect_cell_sign(c, X, Y, dx, dy, yshift):
    """ Check intersection cell sign. Returns True if X& Y are on the same side of the line determined by dx,dy and yshift
    
    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X/Y : ndarray(float)
            coordinates of two points
        
        dx/dy : float
            x/y distance between start and end points of a line segment
        
        yshift : float
            y-intercept of an infinite line in 2d or x-value of line
             is parallel to y axis
    Returns
    ---------
        True/False : bool
            True, if X and Y are on the same side of the line determined by dx,dy,yshift
            or if one of the points lies on the line
            False otherwise.
    Notes
    -----

    """
    if dx != 0:
        sgn_x = dy * (X[0]) - dx * (X[1] - yshift)
        # right-hand side ==0 if X lies on intersection
        # <0 if above and >0 of below intersection
        sgn_y = dy * (Y[0]) - dx * (Y[1] - yshift)
    else:
        # if intersection is parallel to y-axis just check if
        # X, Y are left or right of it
        sgn_x = X[0] - yshift
        sgn_y = Y[0] - yshift
    if sgn_x == 0 or sgn_y == 0:
        return True
    if (sgn_x < 0 and sgn_y < 0) or (sgn_x > 0 and sgn_y > 0):
        return False
    else:
        return True


#######################################################################
#############___Functions related to Occupancy Grid___#################


def occupancy_cell(c, X):
    """ Returns Occupancy-Grid index of the point X

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        X : ndarray(float)
            x,y-coordinats of a points

    Returns
    ---------
        x,y : int
            index-pair of the occupancy-grid-cell, in which X lies

    Notes
    -----

    """
    x = floor((X[0] - c.x_min) * c.occupancy_grid_side_length_inv)
    y = floor((X[1] - c.y_min) * c.occupancy_grid_side_length_inv)
    return x, y


#######################################################################


#@profile
def occupancy_undersampled(c):
    """ Determines and fills the occupancy grid and returns the indices of
    empty cells. A cell is considered occupied if the disk centered at any
    node with a radius of the local exclusion radius of that node overlaps
    with said cell.

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables

    Returns
    ---------
        undersampled_cells : list(ndarray(int))
            indices of emtpy occupancy-grid-cells
    Notes
    -----



    """
    c.no_horizontal_occupancy_cells = ceil(
        (c.x_max - c.x_min) * c.occupancy_grid_side_length_inv)
    c.no_vertical_occupancy_cells = ceil(
        (c.y_max - c.y_min) * c.occupancy_grid_side_length_inv)
    c.occupancy_grid = zeros((c.no_horizontal_occupancy_cells + 1,
                              c.no_vertical_occupancy_cells + 1)).astype(bool)
    c.occupancy_grid[:, -1] = True  #c.occupancy_grid[:, -1] + 1
    c.occupancy_grid[:, 0] = True  #c.occupancy_grid[:, 0] + 1
    c.occupancy_grid[-1, :] = True  #c.occupancy_grid[-1, :] + 1
    c.occupancy_grid[0, :] = True  #c.occupancy_grid[0, :] + 1
    # Boundary cells should are either occupied or outside of the domain
    # Takes care of rare cases, where x_max is not in the last boundary cell
    # (x_max a multiple of the grid size.)

    xs = arange(
        c.x_min, c.x_min +
        c.no_horizontal_occupancy_cells * c.occupancy_grid_side_length,
        .5 * c.occupancy_grid_side_length)
    # create array of x, values such that at least on falls in every column
    # of the grid
    for points in xs:
        try:
            boundary_cell = occupancy_cell(c, upper_boundary(c, points))
        except BaseException:
            local_print_log(f"error {points}", 'error')
        if boundary_cell[0] < c.no_horizontal_occupancy_cells:
            # for every x-value find the two boundary-cells and mark
            # everything above/below, i.w. outside of the domain as
            # occupied, otherwise the algorithm tries to fill in
            # holes outside of the domain, which wastes a lot of time
            c.occupancy_grid[boundary_cell[0], (boundary_cell[1]):] = True  #(
            #c.occupancy_grid[boundary_cell[0], (boundary_cell[1]):]) + 1
            boundary_cell = occupancy_cell(c, lower_boundary(c, points))
            (c.occupancy_grid[boundary_cell[0], :(
                boundary_cell[1])]) = True  # (
            #c.occupancy_grid[boundary_cell[0], :(boundary_cell[1])]) + 1
    # marks cells around boundary points
    for i in range(0, len(c.coordinates)):
        occupancy_mark(c, c.coordinates[i])
    undersampled_cells = nonzero(c.occupancy_grid == 0)
    del c.occupancy_grid
    return undersampled_cells


#######################################################################


def occupancy_mark(c, node):
    """marks circular region around  as occupied. Region is chosen such,
    that cells overlapping with a circle of radius r(C) around C are
    marked, hence Cells that are unmarked are guaranteed to be empty.

    Parameters
    ------------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        node : ndarray(float)
            x,y coordinates of an accepted node

    Returns
    ---------

    Notes
    -----

    """
    center_cell = occupancy_cell(c, node[0:2])
    occupied_radius = ceil(node[2] * c.occupancy_grid_side_length_inv)
    # furthest number of cells that could still contain a node conflicting
    # with a node in center cell.
    X, Y = ogrid[
        max(center_cell[0] -
            occupied_radius, 0):min(center_cell[0] + occupied_radius +
                                    1, c.no_horizontal_occupancy_cells + 1),
        max(center_cell[1] -
            occupied_radius, 0):min(center_cell[1] + occupied_radius +
                                    1, c.no_vertical_occupancy_cells + 1)]
    distance_from_center = ((X - center_cell[0])**2 + (Y - center_cell[1])**2)
    occupied_by_node = (distance_from_center <= (occupied_radius + 1)**2)
    # create a circular mask of ones of cells occupied by center node.
    c.occupancy_grid[X, Y] = (c.occupancy_grid[X, Y]) | occupied_by_node
    # add circilar mask to grid, to mark cells occupied by center node
    # unoccupied cells remain 0.


#######################################################################


def resample(c, cell_x, cell_y):
    """ Uniformly samples a point from an under-sampled cell

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        cell_x/cell_y : int
            x,y index of an empty occupancy cell

    Returns
    ---------
        candidate : ndarray(float)
            coordinates of a point within the empty occupancy cell

    Notes
    -----
        by choice of the empty cells, points sampled by this function
        can only conflict with each other.
    """
    candidate = array([
        c.x_min + (cell_x + random()) * c.occupancy_grid_side_length,
        c.y_min + (cell_y + random()) * c.occupancy_grid_side_length
    ])
    return candidate


#######################################################################


def lower_boundary(c, x):
    """ lower bounding function at x

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        x : float
            x-value between c.x_min and c.x_max

    Returns
    ---------
        x,y : ndarray(float)
            coordinates of apoint on the upper boundary with x-
            coordinate x.

    Notes
    -----

    """
    i = c.last_x_min_index

    while c.vertices_x[i] < c.x_max:
        if x >= c.vertices_x[i] and x <= c.vertices_x[(i + 1) %
                                                      c.no_of_vertices]:
            y = c.vertices_y[i] + \
                c.slope_lower_boundary[i] * (x - c.vertices_x[i])
            return array([x, y])
        i = (i + 1) % c.no_of_vertices
    return array([x, c.y_max])


#######################################################################


def upper_boundary(c, x):
    """ upper bounding function at x

    Parameters
    -----------
        c : Poisson Disc Class
            contains input parameters and widely used variables
        
        x : float
            x-value between c.x_min and c.x_max

    Returns
    ---------
        x,y : ndarray(float)
            coordinates of a point on the upper boundary with x-
            coordinate x.

    Notes
    -----

    """

    i = c.first_x_min_index
    while c.vertices_x[i] < c.x_max:
        if x >= c.vertices_x[i] and x <= c.vertices_x[(i - 1) %
                                                      c.no_of_vertices]:
            y = c.vertices_y[i] + \
                c.slope_upper_boundary[i] * (x - c.vertices_x[i])
            return array([x, y])
        i = (i - 1) % c.no_of_vertices
    return array([x, c.y_min])


#######################################################################
#####################___2D-Numpy replacements___#######################
"""The following turned out to be faster then their numpy counterpart """


def distance(X, Y):
    """ Returns the Euclidean distance between X and Y

    Parameters
    -----------
        X/Y : ndarrya(float)
            2d coordinates of points X and Y

    Returns
    ---------
        distance : float
            euclidean distance

    Notes
    -----
    faster than numpy equivalent for 2d
    """
    return sqrt((X[0] - Y[0]) * (X[0] - Y[0]) + (X[1] - Y[1]) * (X[1] - Y[1]))


def distance_sq(X, Y):
    """ Returns the square of the Euclidean distance between X and Y

    Parameters
    ------------
        X/Y : ndarrya(float)
            2d coordinates of points X and Y

    Returns
    ---------
        distance_sq : float
            euclidean distance squared

    Notes
    -----
    faster than numpy equivalent for 2d


    """
    return (X[0] - Y[0]) * (X[0] - Y[0]) + (X[1] - Y[1]) * (X[1] - Y[1])


def norm_sq(X):
    """ returns euclidean square norm of X

    Parameters
    ------------
        X : ndarrya(float)
            2d coordinates of points X and Y

    Returns
    ---------
        norm_sq : float
            euclidean norm squared

    Notes
    -----
    faster than numpy equivalent for 2d

    """
    return X[0] * X[0] + X[1] * X[1]


def dot_product(X, Y):
    """returns dotproduct of X and Y

    Parameters
    -----------
        X/Y : ndarrya(float)
            2d coordinates of points X and Y

    Returns
    ---------
        dot_product : float
            euclidean dotproduct

    Notes
    -----
    faster than numpy equivalent for 2d

    """
    return X[0] * Y[0] + X[1] * Y[1]


#######################################################################
def dump_poisson_params(h, coarse_factor, slope, min_dist, max_dist,
                        concurrent_samples, grid_size, well_flag):
    """ Writes the parameters used for Poisson point generation to a pickled python dictionary 
    named 'poisson_params.p'. 

    Checks if parameters are within acceptable ranges. If not, they are returned to default values. 

    If coarse_factor is not default (8), then the parameters used in coarsening are 

    Parameters
    ------------
        h : float
            Min distance of the system. defined in params.txt
        
        coarse_factor: float
            Maximum resolution of the mesh. Given as a factor of h
        
        slope : float
            slope of variable coarsening resolution. 
        
        min_dist : float 
            Range of constant min-distance around an intersection (in units of h). 
        
        max_dist : float 
            Range over which the min-distance between nodes increases (in units of h)
        
        concurrent_samples : int
            number of new candidates sampled around an accepted node at a time.
        
        grid_size : float
            side length of the occupancy grid is given by H/occupancy_factor
        
        well_flag : bool
            boolean if wells are included in the meshing.

    Returns
    ---------
        None

    Notes
    -----
        Variable names here are not consistent with those used in the function called to construct
        the Poisson Samples. Below is a conversion table:

        min_dist = F
        max_dist = R
        slope = A
        grid_size = occupancy_factor

    """
    local_print_log("--> Writing Poisson Disc Parameters")
    # Check parameter ranges
    if 0 <= slope < 1:
        pass
    else:
        local_print_log(f"--> Slope Parameter is outside correct range [0,1)")
        local_print_log(f"--> Value provided: {slope}")
        local_print_log("--> Setting to default: 0.1")
        slope = 0.1

    if min_dist < 0:
        local_print_log("--> Warning: Provided min_dist greater 0")
        local_print_log(f"--> min_dist provided: {min_dist}")
        local_print_log("--> Setting to default: 1")
        min_dist = 1

    if min_dist > max_dist:
        local_print_log("--> Warning: Provided min_dist greater than max_dist")
        local_print_log(f"--> min_dist provided: {min_dist}")
        local_print_log(f"--> max_dist provided: {max_dist}")
        local_print_log("Setting to default: min_dist=1, max_dist=40")
        min_dist = 1
        max_dist = 40

    if coarse_factor != 8:
        slope = 0.1
        max_dist = (coarse_factor - 1) / (2 * slope)

    ## Write information to screen about meshing parameters
    local_print_log("--> Poisson Sampling Parameters:")
    local_print_log(f"--> h: {h}")
    local_print_log(f"--> coarse_factor: {coarse_factor}")
    local_print_log(f"--> min_dist: {min_dist}")
    local_print_log(f"--> max_dist: {max_dist}")
    local_print_log(f"--> concurrent_samples: {concurrent_samples}")
    local_print_log(f"--> grid_size: {grid_size}\n")
    local_print_log(f"--> Lower bound on mesh size: {h/2:0.2e}")
    local_print_log(f"--> Upper bound on mesh size: {2*slope*h*max_dist + h:0.2e}\n")

    params = {"h":h,"R":max_dist,"A":slope,"F":min_dist,\
        "concurrent_samples":concurrent_samples,"grid_size":grid_size,"well_flag": well_flag}
    pickle.dump(params, open("poisson_params.p", "wb"))


def single_fracture_poisson(fracture_id):
    """ Generates a point distribution for meshing fracture {fracture_id} using Poisson Disc
    Sampling. Resulting points are written into 'points/points_{fracture_id}.xyz' file with format:

    x_0 y_0 z_0
    x_1 y_1 z_1
    ...
    x_n y_n z_n

    Parameters
    -----------
        fracture_id : int
            fracture index

    Returns
    ---------
        None

    Notes
    -----
        Parameters for point generation are in a pickled python dictionary "poisson_params.p"
        created by dump_poisson_params. 

        """

    local_print_log(f"--> Starting Poisson sampling for fracture number {fracture_id}")
    params = pickle.load(open("poisson_params.p", "rb"))
    c = pc.Poisson_Variables(fracture_id, f"polys/poly_{fracture_id}.inp",\
                           f"intersections/intersections_{fracture_id}.inp", \
                            params["h"], params["R"], params["A"],\
                            params["F"],params["concurrent_samples"],\
                            params["grid_size"],params["well_flag"])

    start = timeit.default_timer()
    ############################################
    ###########___Core-Algorithm___#############
    ############################################

    # Reads geometry from input files, sets all derived parameters and
    # creates initial set of nodes on the boundary
    main_init(c)

    # samples in majority of domain      (1)
    main_sample(c)

    # fills in holes in the sampling to guarantee maximality
    search_undersampled_cells(c)

    # Takes off sampling from where it stopped at (1) to increase density
    # in previously under-sampled regions to average.
    main_sample(c)

    ############################################
    ############################################

    # write coordinates to file
    dump_coordinates(c, f'points/points_{fracture_id}.xyz')

    runtime = timeit.default_timer() - start
    local_print_log(
        f"--> Poisson sampling for fracture {fracture_id} took {runtime:0.2f} seconds"
    )
