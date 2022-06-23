"""
.. module:: graph_transport.py
   :synopsis: simulate transport on a pipe network representaiton of a DFN 
.. moduleauthor:: Shriram Srinivasan <shrirams@lanl.gov>, Jeffrey Hyman <jhyman@lanl.gov>

"""

from re import X
import networkx as nx
import numpy as np
import numpy.random
import sys
import math
import scipy.special
import multiprocessing as mp

import timeit
import os

# pydfnworks modules
import pydfnworks.dfnGraph.graph_flow


def interpolate_time(x0, t1, t2, x1, x2):
    """ interpolates time between t1 and t2 at location x0 which is between x1 and x2

    Parameters
    ----------
        x0 : float
            current location
        t1 : float
            previous time step
        t2 : float
            next time step
        x1 : float
            previous location
        x2 : float
            next location

    Returns
    -------
        time at location x0
            

    Notes
    -----

    """

    return t1 + (t2 - t1) / (x2 - x1) * (x0 - x1)

class Particle():
    ''' 
    Class for graph particle tracking, instantiated for each particle


    Attributes:
        * time : Total advective time of travel of particle [s]
        * tdrw_time : Total advection+diffusion time of travel of particle [s]
        * dist : total distance travelled in advection [m]
        * flag : True if particle exited system, else False
        * frac_seq : Dictionary, contains information about fractures through which the particle went
    '''
    def __init__(self, particle_number):
        self.particle_number = particle_number
        self.frac_seq = {}
        self.cp_seq = []
        self.time = float
        self.tdrw_time = float
        self.dist = float
        self.flag = bool
    

    def set_start_time_dist(self, t, L):
        """ Set initial value for travel time and distance

        Parameters
        ----------
            self: object
            t : double
                time in seconds
            L : double
                distance in metres

        Returns
        -------

        """

        self.time = t
        self.tdrw_time = t
        self.dist = L

    def track(self, G, nbrs_dict, ip, tdrw_flag,
              matrix_porosity, matrix_diffusivity, control_planes, direction):
        """ track a particle from inlet vertex to outlet vertex

        Parameters
        ----------
            G : NetworkX graph
                graph obtained from graph_flow

            nbrs_dict: nested dictionary
                dictionary of downstream neighbors for each vertex

        Returns
        -------

        """
        # Current position is initial positions assigned in get_initial_positions
        curr_v = ip
        cp_index = 0
        while True:

            if G.nodes[curr_v]['outletflag']:
                self.flag = True
                break

            if nbrs_dict[curr_v]['child'] is None:
                self.flag = False
                break

            next_v = numpy.random.choice(nbrs_dict[curr_v]['child'],
                                         p=nbrs_dict[curr_v]['prob'])

            frac = G.edges[curr_v, next_v]['frac']

            t = G.edges[curr_v, next_v]['time']

            if tdrw_flag:
                a_nondim = matrix_porosity * math.sqrt(
                    matrix_diffusivity /
                    (12.0 * G.edges[curr_v, next_v]['perm']))
                xi = numpy.random.random_sample()
                t_tdrw = t + math.pow(a_nondim * t / scipy.special.erfcinv(xi),
                                      2)
            else:
                t_tdrw = t

            l = G.edges[curr_v, next_v]['length']

            if G.nodes[next_v][direction] > control_planes[cp_index]:
                x0 = control_planes[cp_index]  
                t1 = self.time
                t2 = t 
                x1 = G.nodes[curr_v][direction] 
                x2 = G.nodes[next_v][direction] 
                tau  = interpolate_time(x0, t1, t2, x1, x2)
                print(f"--> crossed control plane at {control_planes[cp_index]} {direction} at time {tau}")
                self.cp_seq.append(tau)
                cp_index += 1

            self.add_frac_data(frac, t, t_tdrw, l)
            curr_v = next_v

    def add_frac_data(self, frac, t, t_tdrw, l):
        """ add details of fracture through which particle traversed

        Parameters
        ----------
            self: object

            frac: int
                index of fracture in graph

            t : double
                advective time (seconds)

            t_tdrw: double
                time diffusiving into matrix (seconds)

            l : double
                distance traveled by the particle

            x : double 
                current x position

        Returns
        -------

        """

        self.frac_seq.update(
            {frac: {
                'time': 0.0,
                'tdrw_time': 0.0,
                'dist': 0.0
            }})
        self.frac_seq[frac]['time'] += t
        self.frac_seq[frac]['tdrw_time'] += t_tdrw
        self.frac_seq[frac]['dist'] += l
        self.time += t
        self.tdrw_time += t_tdrw
        self.dist += l

    def write_file(self, partime_file=None, frac_id_file=None):
        """ write particle data to output files, if supplied

        Parameters
        ----------
            self: object

            partime_file : string
                name of file to  which the total travel times and lengths will be written for each particle, default is None

            frac_id_file : string
                name of file to which detailed information of each particle's travel will be written, default is None
        
        Returns
        -------
        """

        if partime_file is not None:
            with open(partime_file, "a") as f1:
                # f1.write("{:3.3E} {:3.3E} {:3.3E} {:3.3E} \n".format(
                #     self.time, self.tdrw_time, self.tdrw_time - self.time,
                #     self.dist))

                f1.write(f"{self.time:.12e},{self.tdrw_time - self.time:.12e},{self.tdrw_time:.12e},{self.dist:.12e}\n")


        if frac_id_file is not None:
            data1 = []
            data1 = [
                key for key in self.frac_seq if isinstance(key, dict) is False
            ]
            n = len(data1)
            with open(frac_id_file, "a") as f2:
                for i in range(n):
                    f2.write("{:d}  ".format(data1[i]))
                f2.write("\n")
                # f2.write("{:d}".format(n))
                # for i in range(0, 4 * n):
                #     if i < n:
                #         f2.write("{3:d}  ".format(data1[i]))
                #     elif n - 1 < i < 2 * n:
                #         f2.write("{:3.2E}  ".format(
                #             self.frac_seq[data1[i - n]]['time']))
                #     elif 2 * n - 1 < i < 3 * n:
                #         f2.write("{:3.2E}  ".format(
                #             self.frac_seq[data1[i - 2 * n]]['tdrw_time']))
                #     else:
                #         f2.write("{:3.2E}  ".format(
                #             self.frac_seq[data1[i - 3 * n]]['dist']))
                # f2.write("\n")


def prepare_output_files(partime_file, frac_id_file):
    """ opens the output files partime_file and frac_id_file and writes the
        header for each

        Parameters
        ----------

            partime_file : string
                name of file to  which the total travel times and lengths will be written for each particle

            frac_id_file : string
                name of file to which detailed information of each particle's travel will be written

        Returns
        -------
            None
    """

    try:
        with open(partime_file, "w") as f1:
            f1.write(
                "# Total Advective time (s), Total diffusion time (s), Total travel time (Adv.+Diff) (s),total pathline distance (m)\n"
            )
    except:
        error = "ERROR: Unable to open supplied partime_file file {}\n".format(
            partime_file)
        sys.stderr.write(error)
        sys.exit(1)

    try:
        with open(frac_id_file, "w") as f2:
            f2.write("# List of fractures that a particle visits\n")
            #f2.write(
            #    "# Line has (n+n+n+n) entries, consisting of all frac_ids (from 0), advective times (s), advective+diffusion times (s), advection dist covered (m)\n"
            #)
    except:
        error = "ERROR: Unable to open supplied frac_id_file file {}\n".format(
            frac_id_file)
        sys.stderr.write(error)
        sys.exit(1)


def dump_particle_info(particles, partime_file, frac_id_file):
    """ If running graph transport in parallel, this function dumps out all the
        particle information is a single pass rather then opening and closing the
        files for every particle


        Parameters
        ----------
            particles : list
                list of particle objects 

            partime_file : string
                name of file to  which the total travel times and lengths will be written for each particle

            frac_id_file : string
                name of file to which detailed information of each particle's travel will be written

        Returns
        -------
            pfailcount : int 
                Number of particles that do not exit the domain

        """

    prepare_output_files(partime_file, frac_id_file)

    f1 = open(partime_file, "a")
    f2 = open(frac_id_file, "a")

    pfailcount = 0

    for particle in particles:
        if particle.flag:
            # f1.write("{:3.3E} {:3.3E} {:3.3E} {:3.3E} \n".format(
            #     particle.time, particle.tdrw_time,
            #     particle.tdrw_time - particle.time, particle.dist))
            f1.write(f"{particle.time:.12e},{particle.tdrw_time - particle.time:.12e},{particle.tdrw_time:.12e},{particle.dist:.12e}\n")

            data1 = [
                key for key in particle.frac_seq
                if isinstance(key, dict) is False
            ]
            n = len(data1)

            for i in range(n):
                f2.write("{:d}  ".format(data1[i]))
            f2.write("\n")
            # f2.write("{:d}".format(n))
            # for i in range(0, 4 * n):
            #     if i < n:
            #         f2.write("{3:d}  ".format(data1[i]))
            #     elif n - 1 < i < 2 * n:
            #         f2.write("{:3.2E}  ".format(
            #             self.frac_seq[data1[i - n]]['time']))
            #     elif 2 * n - 1 < i < 3 * n:
            #         f2.write("{:3.2E}  ".format(
            #             self.frac_seq[data1[i - 2 * n]]['tdrw_time']))
            #     else:
            #         f2.write("{:3.2E}  ".format(
            #             self.frac_seq[data1[i - 3 * n]]['dist']))
            # f2.write("\n")
        else:
            pfailcount += 1

    f1.close()
    f2.close()
    return pfailcount

def dump_control_planes(particles, control_planes):
    with open('control_planes.dat', "w") as fp:
        fp.write(f"cp,")        
        for cp in control_planes[:-1]:
            fp.write(f"{cp},")
        fp.write(f"{control_planes[-1]}\n")
        for particle in particles:
            fp.write(f"{particle.particle_number},")
            for tau in particle.cp_seq[:-1]:
                fp.write(f"{tau},")
            fp.write(f"{particle.cp_seq[-1]}\n")

def track_particle(data):
    """ Tracks a single particle through the graph

        all input parameters are in the dictionary named data 

        Parameters
        ----------
                
            G : NetworkX graph 
                obtained from graph_flow

            nbrs_dict : dict
                see function  create_neighbor_list

            tdrw_flag : Bool
                if False, matrix_porosity, matrix_diffusivity are ignored

            matrix_porosity: float
                default is 0.02

            matrix_diffusivity: float
                default is 1e-11 m^2/s

        Returns
        -------
            particle : object
                particle trajectory information 

        """
    particle = Particle(data["particle_number"])
    particle.set_start_time_dist(0, 0)
    particle.track(data["G"], data["nbrs_dict"], data["initial_position"], 
                   data["tdrw_flag"], data["matrix_porosity"],
                   data["matrix_diffusivity"], data["control_planes"], 
                   data["direction"])

    return particle

def get_initial_posititions(G,initial_positions,nparticles):
    """ Distributes initial particle positions 

        Parameters
        ----------
                
            G : NetworkX graph 
                obtained from graph_flow

        initial_positions : str
            distribution of initial conditions. options are uniform and flux (flux-weighted)

        nparticles : int
            requested number of particles

        Returns
        -------
            ip : numpy array
                array nparticles long. Each element is the initial position for each particle

        """


    inlet_nodes = [v for v in nx.nodes(G) if G.nodes[v]['inletflag']]
    cnt = len(inlet_nodes)
    print(f"--> There are {cnt} inlet nodes")

    # Uniform Distribution for particles
    if initial_positions == "uniform":
        print("--> Using uniform initial positions.")
        ip = np.zeros(nparticles).astype(int)
        n = int(np.ceil(nparticles/cnt))
        print(f"--> {n} particles will be placed at every inflow node.\n")
        ## this could be cleaned up using clever indexing
        inflow_idx = 0
        inflow_cnt = 0
        for i in range(nparticles):
            ip[i] = inlet_nodes[inflow_idx]
            inflow_cnt += 1
            if inflow_cnt >= n:
                inflow_idx += 1
                inflow_cnt = 0

    ## flux weighted initial positions for particles
    elif initial_positions == "flux":
        print("--> Using flux-weighted initial positions.\n")
        flux = np.zeros(cnt)
        for i,u in enumerate(inlet_nodes):
            for v in G.successors(u):
                flux[i] += G.edges[u,v]['flux']
        flux /= flux.sum()
        flux_cnts = [np.ceil(nparticles*i) for i in flux]
        nparticles = int(sum(flux_cnts))
        ip = np.zeros(nparticles).astype(int)
        ## Populate ip with Flux Cnts
        ## this could be cleaned up using clever indexing
        inflow_idx = 0
        inflow_cnt = 0
        for i in range(nparticles):
            ip[i] = inlet_nodes[inflow_idx]
            inflow_cnt += 1
            if inflow_cnt >= flux_cnts[inflow_idx]:
                inflow_idx += 1
                inflow_cnt = 0

    # Throw error if unknown initial position is provided
    else: 
        error = f"Unknown initial_positions input {initial_positions}. Options are uniform or flux \n"
        sys.stderr.write(error)
        sys.exit(1)

    return ip,nparticles


def create_neighbor_list(G):
    """ Create a list of downstream neighbor vertices for every vertex on NetworkX graph obtained after running graph_flow

    Parameters
    ----------
        G: NetworkX graph 
            Directed Graph obtained from output of graph_flow

    Returns
    -------
        dict : nested dictionary.

    Notes
    -----
    dict[n]['child'] is a list of vertices downstream to vertex n
    dict[n]['prob'] is a list of probabilities for choosing a downstream node for vertex n
    """

    nbrs_dict = {}

    for u in nx.nodes(G):

        if G.nodes[u]['outletflag']:
            continue

        node_list = []
        prob_list = []
        nbrs_dict[u] = {}

        for v in G.successors(u):

            node_list.append(v)
            prob_list.append(G.edges[u, v]['flux'])

        if node_list:
            nbrs_dict[u]['child'] = node_list
            nbrs_dict[u]['prob'] = np.array(prob_list,
                                            dtype=float) / sum(prob_list)
        else:
            nbrs_dict[u]['child'] = None
            nbrs_dict[u]['prob'] = None

    return nbrs_dict
    
def run_graph_transport(self,
                        G,
                        nparticles,
                        partime_file,
                        frac_id_file,
                        initial_positions="uniform",
                        tdrw_flag=False,
                        matrix_porosity=None,
                        matrix_diffusivity=None,
                        control_planes = None,
                        direction = None):
    """ Run  particle tracking on the given NetworkX graph

    Parameters
    ----------
        self : object
            DFN Class
            
        G : NetworkX graph 
            obtained from graph_flow

        nparticles: int 
            number of particles

        initial_positions : str
            distribution of initial conditions. options are uniform and flux (flux-weighted)

        partime_file : string
            name of file to  which the total travel times and lengths will be written for each particle

        frac_id_file : string
            name of file to which detailed information of each particle's travel will be written
        
        tdrw_flag : Bool
            if False, matrix_porosity and matrix_diffusivity are ignored

        matrix_porosity: float
            Matrix Porosity used in TDRW

        matrix_diffusivity: float
            Matrix Diffusivity used in TDRW (SI units m^2/s)

        control_planes : list of floats
            list of control plane locations to dump travel times. Only in primary direction of flow. 

        primary direction : string (x,y,z)
            string indicating primary direction of flow 

    Returns
    -------
        O if completed correctly 

    Notes
    -----
    Information on individual functions is found therein
    """
    print("\n--> Running Graph Particle Tracking")
    # Check parameters for TDRW
    if tdrw_flag:
        if matrix_porosity is None:
            error = f"Error. Requested TDRW but no value for matrix_porosity was provided\n"
            sys.stderr.write(error)
            sys.exit(1)
        elif matrix_porosity < 0 or matrix_porosity > 1: 
            error = f"Error. Requested TDRW but value for matrix_porosity provided is outside of [0,1]. Value provided {matrix_porosity}\n"
            sys.stderr.write(error)
            sys.exit(1)
        if matrix_diffusivity is None:
            error = f"Error. Requested TDRW but no value for matrix_diffusivity was provided\n"
            sys.stderr.write(error)
            sys.exit(1)
        print(f"--> Running particle transport with TDRW. Matrix porosity {matrix_porosity} and Matrix Diffusivity {matrix_diffusivity} m^2/s")

    control_plane_flag = False
    if control_planes != None:
        if not type(control_planes) is list:
            error = f"Error. provided controls planes are not a list\n"
            sys.stderr.write(error)
            sys.exit(1)
        else: 
            control_planes.append(7.5)
            control_planes_flag = True

        if direction is None:
            error = f"Error. Primary direction not provided. Required for control planes\n"
            sys.stderr.write(error)
            sys.exit(1)
        elif direction not in ['x', 'y', 'z']:
            error = f"Error. Primary direction is not known. Acceptable values are x,y, and z\n"
            sys.stderr.write(error)
            sys.exit(1)

    print("--> Creating downstream neighbor list")
    nbrs_dict = create_neighbor_list(G)

    print("--> Getting initial Conditions")
    ip,nparticles = get_initial_posititions(G, initial_positions, nparticles)

    print(f"--> Starting particle tracking for {nparticles} particles")
    pfailcount = 0
    
    if self.ncpu > 1:
        print(f"--> Using {self.ncpu} processors")
        ## Prepare input data
        inputs = []
        for i in range(nparticles):
            data = {}
            data["G"] = G
            data["particle_number"] = i
            data["nbrs_dict"] = nbrs_dict
            data["tdrw_flag"] = tdrw_flag
            data["matrix_porosity"] = matrix_porosity
            data["matrix_diffusivity"] = matrix_diffusivity
            data["initial_position"] = ip[i]
            data["control_planes"] = control_planes
            data["direction"] = direction
            inputs.append(data)

        # Run 
        tic = timeit.default_timer()
        pool = mp.Pool(self.ncpu)
        particles = pool.map(track_particle, inputs)
        pool.close()
        pool.join()
        pool.terminate()

        elapsed = timeit.default_timer() - tic
        print(f"--> Tracking Complete. Time Required {elapsed:.2f} seconds\n")

        print(f"--> Writing Data to files: {partime_file} and {frac_id_file}")
        dump_particle_info(particles, partime_file, frac_id_file)
        print("--> Writing Data Complete\n")
        if control_planes_flag:
            dump_control_planes(particles, control_planes)

    else:

        prepare_output_files(partime_file, frac_id_file)
        tic = timeit.default_timer()
        for i in range(nparticles):
            if i % 1000 == 0:
                print("--> Starting particle %d out of %d" % (i, nparticles))
            particle_i = Particle()
            particle_i.set_start_time_dist(0, 0)
            particle_i.track(G, nbrs_dict, ip[i], tdrw_flag,
                             matrix_porosity, matrix_diffusivity, 
                             control_planes, direction)

            if particle_i.flag:
                particle_i.write_file(partime_file, frac_id_file)
            else:
                pfailcount += 1
        elapsed = timeit.default_timer() - tic
        print(f"--> Tracking Complete. Time Required {elapsed:.2f} seconds")

    if pfailcount == 0:
        print("--> All particles exited")
        print("--> Graph Particle Tracking Completed Successfully.")
    else:
        print(f"--> Out of {nparticles} particles, {pfailcount} particles did not exit")


    return 0 
