"""
.. module:: graph_transport.py
   :synopsis: simulate transport on a pipe network representaiton of a DFN 
.. moduleauthor:: Shriram Srinivasan <shrirams@lanl.gov>, Jeffrey Hyman <jhyman@lanl.gov>

"""

import sys
# from re import I, X
import networkx as nx
import numpy as np
import scipy.special
import multiprocessing as mp
import timeit

# pydfnworks modules
import pydfnworks.dfnGraph.graph_flow
import pydfnworks.dfnGraph.particle_io as io


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
    def __init__(self, particle_number, ip, tdrw_flag, matrix_porosity,
                 matrix_diffusivity, cp_flag, control_planes, direction):
        self.particle_number = particle_number
        self.ip = ip
        self.curr_node = ip
        self.next_node = None
        self.advect_time = 0
        self.delta_t = 0
        self.matrix_diffusion_time = 0
        self.delta_t_md = 0
        self.total_time = 0
        self.length = 0
        self.delta_l = 0
        self.tdrw_flag = tdrw_flag
        self.matrix_porosity = matrix_porosity
        self.matrix_diffusivity = matrix_diffusivity
        self.cp_flag = cp_flag
        self.control_planes = control_planes
        self.cp_index = 0
        self.direction = direction
        self.exit_flag = False
        self.frac_seq = []
        self.cp_adv_time = []
        self.cp_tdrw_time = []

    def advect(self, G, nbrs_dict):
        """ Advection part of particle transport

        Parameters
        ----------
            G : NetworkX graph
                graph obtained from graph_flow

            nbrs_dict: nested dictionary
                dictionary of downstream neighbors for each vertex

        Returns
        -------
            None
        """

        if G.nodes[self.curr_node]['outletflag']:
            self.exit_flag = True

        elif nbrs_dict[self.curr_node]['child'] is None:
            self.exit_flag = True

        else:
            ## complete mixing to select outflowing node
            self.next_node = np.random.choice(
                nbrs_dict[self.curr_node]['child'],
                p=nbrs_dict[self.curr_node]['prob'])

            self.frac = G.edges[self.curr_node, self.next_node]['frac']
            self.frac_seq.append(self.frac)
            self.delta_t = G.edges[self.curr_node, self.next_node]['time']
            self.delat_l = G.edges[self.curr_node, self.next_node]['length']

    def matrix_diffusion(self, G):

        b = np.sqrt(12.0 * G.edges[self.curr_node, self.next_node]['perm'])
        a_nondim = self.matrix_porosity * np.sqrt(self.matrix_diffusivity) / b
        xi = np.random.uniform(size=1, low=0, high=1)[0]
        self.delta_t_md = ((a_nondim * self.delta_t /
                            scipy.special.erfcinv(xi))**2)

    def cross_control_plane(self, G):

        if G.nodes[self.next_node][self.direction] > self.control_planes[
                self.cp_index]:
            ## get information for interpolation to get the time at point of crossing.
            x0 = self.control_planes[self.cp_index]
            t1 = self.advect_time
            t2 = self.advect_time + self.delta_t
            x1 = G.nodes[self.curr_node][self.direction]
            x2 = G.nodes[self.next_node][self.direction]
            tau = interpolate_time(x0, t1, t2, x1, x2)
            # print(f"--> crossed control plane at {control_planes[cp_index]} {direction} at time {tau}")
            self.cp_adv_time.append(tau)
            if self.tdrw_flag:
                t1 = self.total_time
                t2 = self.total_time + self.delta_t_md + self.delta_t
                tau = interpolate_time(x0, t1, t2, x1, x2)
                self.cp_tdrw_time.append(tau)
            else:
                self.cp_tdrw_time.append(tau)

            self.cp_index += 1
            # if we're crossed all the control planes, turn off cp flag for this particle
            if self.cp_index >= len(self.control_planes):
                self.cp_flag = False

    def update(self):
        self.advect_time += self.delta_t
        self.matrix_diffusion_time += self.delta_t_md
        self.total_time += self.delta_t + self.delta_t_md
        self.length += self.delat_l
        self.frac_seq.append(self.frac)
        self.curr_node = self.next_node

    def track(self, G, nbrs_dict):
        while not self.exit_flag:
            self.advect(G, nbrs_dict)

            if self.exit_flag:
                self.update()
                break

            if self.tdrw_flag:
                self.matrix_diffusion(G)

            if self.cp_flag:
                self.cross_control_plane(G)

            self.update()


def track_particle(data):
    """ Tracks a single particle through the graph

        all input parameters are in the dictionary named data 

        Parameters
        ----------
            data : dict
                Dictionary of parameters the includes particle_number, initial_position, tdrw_flag, matrix_porosity, matrix_diffusivity, cp_flag, control_planes, direction, G, and nbrs_dict.  

        Returns
        -------
            particle : object
                Particle will full trajectory

        """
    particle = Particle(data["particle_number"], data["initial_position"],
                        data["tdrw_flag"], data["matrix_porosity"],
                        data["matrix_diffusivity"], data["cp_flag"],
                        data["control_planes"], data["direction"])

    particle.track(data["G"], data["nbrs_dict"])
    # Current position is initial positions assigned in get_initial_positions

    return particle


def get_initial_posititions(G, initial_positions, nparticles):
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
    if cnt == 0:
        error = "Error. There are no nodes in the inlet.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)

    # Uniform Distribution for particles
    if initial_positions == "uniform":
        print("--> Using uniform initial positions.")
        ip = np.zeros(nparticles).astype(int)
        n = int(np.ceil(nparticles / cnt))
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
        for i, u in enumerate(inlet_nodes):
            for v in G.successors(u):
                flux[i] += G.edges[u, v]['flux']
        flux /= flux.sum()
        flux_cnts = [np.ceil(nparticles * i) for i in flux]
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
        error = f"Error. Unknown initial_positions input {initial_positions}. Options are uniform or flux \n"
        sys.stderr.write(error)
        sys.exit(1)

    return ip, nparticles


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
                        control_planes=None,
                        direction=None):
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
        print(
            f"--> Running particle transport with TDRW. Matrix porosity {matrix_porosity} and Matrix Diffusivity {matrix_diffusivity} m^2/s"
        )

    control_plane_flag = False
    if control_planes != None:
        if not type(control_planes) is list:
            error = f"Error. provided controls planes are not a list\n"
            sys.stderr.write(error)
            sys.exit(1)
        else:
            # add None to indicate the end of the control plane list
            control_plane_flag = True

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
    ip, nparticles = get_initial_posititions(G, initial_positions, nparticles)

    print(f"--> Starting particle tracking for {nparticles} particles")
    pfailcount = 0

    if self.ncpu > 1:
        print(f"--> Using {self.ncpu} processors")
        ## Prepare input data
        inputs = []
        for i in range(nparticles):
            data = {}
            data["G"] = G
            data["nbrs_dict"] = nbrs_dict
            data["particle_number"] = i
            data["tdrw_flag"] = tdrw_flag
            data["matrix_porosity"] = matrix_porosity
            data["matrix_diffusivity"] = matrix_diffusivity
            data["initial_position"] = ip[i]
            data["cp_flag"] = control_plane_flag
            data["control_planes"] = control_planes
            data["direction"] = direction
            inputs.append(data)

        # Run
        tic = timeit.default_timer()

        pool = mp.Pool(min(self.ncpu, nparticles))

        particles = pool.map(track_particle, inputs)
        pool.close()
        pool.join()
        pool.terminate()

        elapsed = timeit.default_timer() - tic
        print(f"--> Tracking Complete. Time Required {elapsed:.2f} seconds\n")

        print(f"--> Writing Data to files: {partime_file} and {frac_id_file}")
        io.dump_particle_info(particles, partime_file, frac_id_file)
        print("--> Writing Data Complete\n")
        if control_plane_flag:
            io.dump_control_planes(particles, control_planes)

    else:

        io.prepare_output_files(partime_file, frac_id_file)
        tic = timeit.default_timer()
        particles = []
        for i in range(nparticles):
            if i % 1000 == 0:
                print("--> Starting particle %d out of %d" % (i, nparticles))
            particle = Particle(i, ip[i], tdrw_flag, matrix_porosity,
                                matrix_diffusivity, control_plane_flag,
                                control_planes, direction)
            particle.track(G, nbrs_dict)
            particles.append(particle)
        elapsed = timeit.default_timer() - tic

        print(f"--> Tracking Complete. Time Required {elapsed:.2f} seconds")

        io.dump_particle_info(particles, partime_file, frac_id_file)
        print("--> Writing Data Complete\n")
        if control_plane_flag:
            io.dump_control_planes(particles, control_planes)

    if pfailcount == 0:
        print("--> All particles exited")
        print("--> Graph Particle Tracking Completed Successfully.")
    else:
        print(
            f"--> Out of {nparticles} particles, {pfailcount} particles did not exit"
        )

    return 0
