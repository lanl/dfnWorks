# contains global variables
class Poisson_Variables():
    def __init__(self, fracture_id, path_to_polygon, path_to_intersections, H, R, A, F,
                 concurrent_samples, occupancy_factor, well_flag):
        import numpy as np
        """ Takes in input-parameters and contains all variables derived from
            those, that are used by multiple functions.
            Parameters
            ---------
                path_to_polygons : string
                    path to the file containing the vertices of the polygon to be sampled
                path_to_intersections : string
                    path to the intersections-file
                H : float
                    double the min distance of the system. defined in params.txx
                R : float
                    Range over which the min-distance between nodes increases (in units of H)
                    named max_dist in mesh_dfn.py
                A : float
                    slope of min-distance. Named slope in mesh_dfn.py
                F : float
                    Range of constant min-distance around an intersection (in units of H). 
                    Named min_dist in mesh_dfn.py
                concurrent_samples : int
                    number of new candidates sampled around an accepted node at a time.
                occupancy_factor : float
                    side length of the occupancy grid is given by H/occupancy_factor
                    named grid_size in mesh_dfn.py
                Notes
                -----
        """
        # Input parameters
        ###############################################################
        self.fracture_id = fracture_id
        self.path_poly = path_to_polygon
        self.path_inter = path_to_intersections
        self.k = concurrent_samples
        self.R = R
        self.H = H
        self.A = min(A, .95)  # sine of min angle in a triangulation
        # is bounded by (1-A)/2, require 1-A>eps>0
        self.F = F
        self.occupancy_grid_side_length = self.H / occupancy_factor
        self.well_flag = well_flag

        # Derived from input
        ###################################
        # maximal- minimal distance between nodes
        self.max_exclusion_radius = (self.A * self.R + .5) * self.H
        self.z_plane = 0.0
        # z-coordinate of the polygon, only needed for output
        self.current_node = 0
        # number of the next already accepted node to be center of
        # a sampling. Stored here, so main_sampling can continue,
        # where it left off, if interrupted.
        self.no_of_nodes = 0  # current length of Coordinate-list
        self.coordinates = []
        # list of coordinates. Every entry is an array with the first
        # two components being x/y-coordinates and the third entry being
        # the local exclusion radius of the node.

        # Geometry of Polygon
        self.vertices = []  # corner vertices of the polygon,
        # clockwise order is required!!
        self.no_of_vertices = len(self.vertices)
        self.vertices_x = []  # x-coordinates of vertices
        self.vertices_y = []
        self.x_min, self.x_max = 0, 0
        self.y_min, self.y_max = 0, 0
        self.first_x_min_index = 0
        # vertex-index of the vertex with the smallest y-value of the
        # vertices with x-value x_min, used to define upper and lower
        # boundary function. requires convexity of polygon to be well-def
        self.last_x_min_index = 0
        # vertex-index of the vertex with the smallest y-value of the
        # vertices with x-value x_min, used to define upper and lower
        # boundary function. requires convexity of polygon to be well-def
        self.slope_lower_boundary = 0  # boundaries of polygon are piecewise linear
        self.slope_upper_boundary = 0

        # Neighbor-grid variables
        self.neighbor_cell_size = self.H / 2 / np.sqrt(2)
        self.neighbor_cell_size_inv = 1 / self.neighbor_cell_size
        self.no_of_horizontal_neighbor_cells = 1
        self.no_of_horizontal_neighbor_cells = 1
        self.neighbor_grid = np.zeros(1)

        # Intersection-related variables
        self.intersect_range_sq = ((self.R + self.F) * self.H)**2
        # distance along which an intersection affects the local
        # exclusion radius  (squared)
        if (self.intersect_range_sq) != 0:
            self.intersect_grid_inv = 1 / (self.R * self.H + self.F * self.H)
            # inverse cell-size of intersection-grid
        else:
            self.intersect_grid_inv = 1
            # inverse cell-size of intersection-grid
        self.intersect_endpts = []
        self.intersect_cells = {}
        # key (i,j) contains numbers of intersection within a distance
        # of intersect-range or less to the intersect-cell (i,j)
        self.square_nodes = np.array([[1, 0], [1, 1], [0, 1], [0, 0], [1, 0]])
        # (k-1)-th and k-th row contain nodes of a square bounding the
        # edge of that square in direction k, where k in [1,2,3,4]
        # and the numbers corresponding to directions as follows:
        # 1->right, 3->left, 2->up, 4->down.

        # Occupancy-grid variables
        self.occupancy_grid_side_length_inv = 1 / self.occupancy_grid_side_length
        self.no_of_horizontal_occupancy_cells = 1
        self.no_of_horizontal_occupancy_cells = 1
        self.occupancy_grid = np.zeros(1)
