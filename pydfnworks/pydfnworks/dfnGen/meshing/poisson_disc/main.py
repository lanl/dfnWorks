import cfg
import timeit
from func import *

c = cfg.Pseudo_Globals('polys/poly_1.inp',
                       'intersections/intersections_1.inp', 0.1, 100, 0.1, 1, 5, 10)
# This class is a container for variables used by many functions and subfunctions of this script.
# Its inputs with default value are as follows:
# input_1 = path to the polygon to be sampled                            (required)
# input_2 = path to the intersections of this polygon                    (currently required !!! Fix, if no intersection provided?)
#input_3 = 2*min-distance (H)                                           (default = tbd)
# input_4 = Range of increasing min-distance in units of H  (R)          (default = tbd)
# input_5 = slope of min-distance (A)                                    (default = tbd)
# input_6 = Range of constant min-distance around an intersection (F)    (default = tbd)
# input_7 = number of concurrent samples (k)                             (default = tbd)
#input_8 = occupancy-grid-size (H/input_8)                              (default = tbd)


start = timeit.default_timer()
############################################
###########___Core-Algorithm___#############
############################################
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

main_init(c)
# Reads geometry from input files, sets all derived parameters and
# creates inital set of nodes on the boundary(could be done within
# Pseudo_Globals)

main_sample(c)
# samples in majority of domain      (1)

search_undersampled_cells(c)
# fills in holes in the sampling to guarantee maximality

main_sample(c)
# Takes off sampling from where it stopped at (1) to increase density
# in previously undersampled regions to average.


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
############################################
############################################

runtime = timeit.default_timer() - start
print("Sampling",
      len(c.coordinates),
      "nodes on the polygon stored in",
      c.path_poly,
      "took",
      runtime,
      "seconds.")


# Uncomment to store Coordinates in .xyz file
output_file_name = 'points/points_'
print_coordinates(c, output_file_name + '.xyz')


# Uncomment to plot Coordinates to screen or file
# plot_coordinates(c)
# plot_coordinates(c,'./pics2/'+poly[l][-10:-3])
