
import timeit
import os
import shutil
import multiprocessing as mp
from pydfnworks.dfnGen.meshing.poisson_disc import cfg as cfg 
from pydfnworks.dfnGen.meshing.poisson_disc import poisson_functions as pf

def single_fracture_poisson(fracture_id, h, R = 100, A = 0.1, F = 1, concurrent_samples = 5, grid_size = 100):

    # print(f"--> Starting Fracture Number {params['fracture_id']}")
    # c = cfg.Pseudo_Globals(f"polys/poly_{params['fracture_id']}.inp",\
    #                        f"intersections/intersections_{params['fracture_id']}.inp", \
    #                         params['h'], params["R"], params["A"], params["F"],\
    #                         params["concurrent_samples"], params["grid_size"])

    print(f"--> Starting Poisson Sampling for Fracture Number {fracture_id}")
    c = cfg.Pseudo_Globals(f"polys/poly_{fracture_id}.inp",\
                           f"intersections/intersections_{fracture_id}.inp", \
                            2*h, R, A, F,concurrent_samples, grid_size)

    start = timeit.default_timer()
    ############################################
    ###########___Core-Algorithm___#############
    ############################################
    # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    pf.main_init(c)
    # Reads geometry from input files, sets all derived parameters and
    # creates inital set of nodes on the boundary(could be done within
    # Pseudo_Globals)

    pf.main_sample(c)
    # samples in majority of domain      (1)

    pf.search_undersampled_cells(c)

    # fills in holes in the sampling to guarantee maximality

    pf.main_sample(c)
    # Takes off sampling from where it stopped at (1) to increase density
    # in previously undersampled regions to average.

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ############################################
    ############################################

    # Uncomment to store Coordinates in .xyz file
#    output_file_name = f'points/points_{params["fracture_id"]}.xyz'
    output_file_name = f'points/points_{fracture_id}.xyz'
    pf.print_coordinates(c, output_file_name)

    runtime = timeit.default_timer() - start
    print(f"--> Fracture Number {fracture_id} Poisson Sampling Complete. Time: {runtime:0.2f} seconds")

def single_worker(work_queue, params):
    """ Worker function for parallelized meshing 
    
    Parameters
    ----------
        work_queue : multiprocessing queue
            Queue of fractures to be meshed
        visual_mode : bool
            True/False for reduced meshing
        num_poly : int
            Total Number of Fractures

    Returns
    -------
        True : bool
            If job is complete

"""
    #try:
    for fracture_id in iter(work_queue.get, 'STOP'):
        single_fracture_poisson(params[fracture_id-1])
#except:
#    print('Error on Fracture ',fracture_id)
#    pass
    return True

def prepare_poisson_points(num_poly, ncpu, h, R = 100, A = 0.1, F = 1, concurrent_samples = 5, grid_size = 100):
   # This class is a container for variables used by many functions and subfunctions of this script.
    # Its inputs with default value are as follows:
    # input_1 = path to the polygon to be sampled                            (required)
    # input_2 = path to the intersections of this polygon                    (currently required !!! Fix, if no intersection provided?)
    # input_3 = 2*min-distance (H)                                           (default = tbd)
    # input_4 = Range of increasing min-distance in units of H  (R)          (default = tbd)
    # input_5 = slope of min-distance (A)                                    (default = tbd)
    # input_6 = Range of constant min-distance around an intersection (F)    (default = tbd)
    # input_7 = number of concurrent samples (k)                             (default = tbd)
    #input_8 = occupancy-grid-size (H/input_8)   

    print('=' * 80)
    print(f"--> Creating Points using Poisson Disc Sampling: Starting")

    if os.path.isdir("points"):
        shutil.rmtree("points")
        os.mkdir("points")
    else:
        os.mkdir("points")

    params = []
    for i in range(1,num_poly+1):
        job = {"fracture_id":i,"h":2*h,"R":R,"A":A,"F":F,\
        "concurrent_samples":concurrent_samples,"grid_size":grid_size}
        params.append(job)
   
    for i in range(num_poly):
        single_fracture_poisson(i+1,h)

   #  work_queue = mp.Queue()  # reader() reads from queue
   #  processes = []

   #  for i in range(1,num_poly+1):
   #      work_queue.put(i)

   #  for i in range(ncpu):
   #      p = mp.Process(target=single_worker, args=(work_queue,params))
   #      p.daemon = True
   #      p.start()
   #      processes.append(p)
   #      work_queue.put('STOP')

   #  for p in processes:
   #      p.join()

   #  del(processes)

    print(f"--> Creating Points using Poisson Disc Sampling: Complete\n\n")
    print('=' * 80)

