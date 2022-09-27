"""
.. module:: graph_transport.py
   :synopsis: simulate transport on a pipe network representaiton of a DFN 
.. moduleauthor:: Shriram Srinivasan <shrirams@lanl.gov>, Jeffrey Hyman <jhyman@lanl.gov>

"""

import sys
import networkx as nx
import numpy as np

import multiprocessing as mp
import timeit


# pydfnworks graph modules modules
import pydfnworks.dfnGraph.particle_io as io
from pydfnworks.dfnGraph.graph_tdrw import set_up_limited_matrix_diffusion
from pydfnworks.dfnGraph.particle_class import Particle



def track_particle(data, verbose = False):
    """ Tracks a single particle through the graph

        all input parameters are in the dictionary named data 

        Parameters
        ----------
            data : dict
                Dictionary of parameters the includes particle_number, initial_position, 
                tdrw_flag, matrix_porosity, matrix_diffusivity, cp_flag, control_planes,
                 direction, G, and nbrs_dict.  

        Returns
        -------
            particle : object
                Particle will full trajectory

    """
    if verbose:
        p = mp.current_process()
        _, cpu_id = p.name.split("-")
        cpu_id = int(cpu_id)
        print(f"--> Particle {data['particle_number']} is starting on worker {cpu_id}")

    particle = Particle(data["particle_number"], data["initial_position"],
                        data["tdrw_flag"], data["matrix_porosity"],
                        data["matrix_diffusivity"], data["fracture_spacing"],
                        data["trans_prob"], data["transfer_time"],
                        data["cp_flag"], data["control_planes"],
                        data["direction"])

    # # get current process information
    global nbrs_dict
    global G_global
    particle.track(G_global, nbrs_dict)
    if verbose:
        print(f"--> Particle {data['particle_number']} is complete on worker {cpu_id}")
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
            prob_list.append(G.edges[u, v]['vol_flow_rate'])
        if node_list:
            nbrs_dict[u]['child'] = node_list
            nbrs_dict[u]['prob'] = np.asarray(prob_list) / sum(prob_list)
        else:
            nbrs_dict[u]['child'] = None
            nbrs_dict[u]['prob'] = None

    return nbrs_dict


def check_tdrw_params(matrix_porosity, matrix_diffusivity, fracture_spacing):
    """ Check that the provided tdrw values are physiscal


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

    if fracture_spacing is not None:
        if fracture_spacing <= 0:
            error = f"Error. Non-positive value for fracture_spacing was provided.\nValue {fracture_spacing}\nExiting program"
            sys.stderr.write(error)
            sys.exit(1)


def check_control_planes(control_planes, direction):
    control_plane_flag = False
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

    print(f"--> Control Planes: {control_planes}")
    print(f"--> Direction: {direction}")
    return control_plane_flag


def run_graph_transport(self,
                        G,
                        nparticles,
                        partime_file,
                        frac_id_file=None,
                        initial_positions="uniform",
                        dump_traj=False,
                        tdrw_flag=False,
                        matrix_porosity=None,
                        matrix_diffusivity=None,
                        fracture_spacing=None,
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
        
        dump_flag: bool
            on/off to write full trajectory information to file

        tdrw_flag : Bool
            if False, matrix_porosity and matrix_diffusivity are ignored

        matrix_porosity: float
            Matrix Porosity used in TDRW

        matrix_diffusivity: float
            Matrix Diffusivity used in TDRW (SI units m^2/s)

        fracture_spaceing : float
            finite block size for limited matrix diffusion

        control_planes : list of floats
            list of control plane locations to dump travel times. Only in primary direction of flow. 

        primary direction : string (x,y,z)
            string indicating primary direction of flow 

    Returns
    -------
        particles : list
            list of particles objects

    Notes
    -----
    Information on individual functions is found therein
    """
    global G_global 
    G_global = nx.Graph()
    G_global = G.copy()

    print("\n--> Running Graph Particle Tracking")
    # Check parameters for TDRW
    if tdrw_flag:
        check_tdrw_params(matrix_porosity, matrix_diffusivity,
                          fracture_spacing)
        print(
            f"--> Running particle transport with TDRW.\n--> Matrix porosity {matrix_porosity}.\n--> Matrix Diffusivity {matrix_diffusivity} m^2/s"
        )

    if control_planes is None:
        control_plane_flag = False
    else:
        control_plane_flag = check_control_planes(
            control_planes=control_planes, direction=direction)

    print(f"--> Control Plane Flag {control_plane_flag}")

    print("--> Creating downstream neighbor list")
    global nbrs_dict 
    nbrs_dict = create_neighbor_list(G)

    print("--> Getting initial Conditions")
    ip, nparticles = get_initial_posititions(G, initial_positions, nparticles)

    print(f"--> Starting particle tracking for {nparticles} particles")

    if dump_traj:
        print(f"--> Writing trajectory information to file")

    if fracture_spacing is not None:
        print(f"--> Using limited matrix block size for TDRW")
        print(f"--> Fracture spacing {fracture_spacing:0.2e} [m]")
        trans_prob = set_up_limited_matrix_diffusion(G, fracture_spacing,
                                                     matrix_porosity,
                                                     matrix_diffusivity)
        # This doesn't change for the system.
        # Transfer time diffusing between fracture blocks
        transfer_time = fracture_spacing**2 / (2 * matrix_diffusivity)
    else:
        trans_prob = None
        transfer_time = None
    ## main loop
    if self.ncpu == 1:
        tic = timeit.default_timer()
        particles = []
        for i in range(nparticles):
            if i % 1000 == 0:
                print(f"--> Starting particle {i} out of {nparticles}")
            particle = Particle(i, ip[i], tdrw_flag, matrix_porosity,
                                matrix_diffusivity, fracture_spacing,
                                trans_prob, transfer_time, control_plane_flag,
                                control_planes, direction)
            particle.track(G, nbrs_dict)
            particles.append(particle)

        elapsed = timeit.default_timer() - tic
        print(
            f"--> Main Tracking Loop Complete. Time Required {elapsed:0.2e} seconds"
        )
        stuck_particles = io.dump_particle_info(particles, partime_file,
                                                frac_id_file)
        if control_plane_flag:
            io.dump_control_planes(particles, control_planes)

        if dump_traj:
            io.dump_trajectories(particles, 1)

    if self.ncpu > 1:
        print(f"--> Using {self.ncpu} processors")
        ## Prepare input data
        inputs = []

        tic = timeit.default_timer()
        pool = mp.Pool(min(self.ncpu, nparticles))

        particles = []
        def gather_output(output):
            particles.append(output)

        for i in range(nparticles):
            data = {}
            # data["G"] = G
            # data["nbrs_dict"] = nbrs_dict
            data["particle_number"] = i
            data["initial_position"] = ip[i]
            data["tdrw_flag"] = tdrw_flag
            data["matrix_porosity"] = matrix_porosity
            data["matrix_diffusivity"] = matrix_diffusivity
            data["fracture_spacing"] = fracture_spacing
            data["transfer_time"] = transfer_time
            data["trans_prob"] = trans_prob
            data["cp_flag"] = control_plane_flag
            data["control_planes"] = control_planes
            data["direction"] = direction
            # inputs.append(data)
            pool.apply_async(track_particle, args=(data,), callback=gather_output)

        # pool = mp.Pool(min(self.ncpu, nparticles))
        # particles = pool.map(track_particle, inputs)
        #for data in inputs:
        #    pool.apply_async(track_particle, args=(data,), callback=gather_output)
        pool.close()
        pool.join()
        pool.terminate()

        elapsed = timeit.default_timer() - tic
        print(
            f"--> Main Tracking Loop Complete. Time Required {elapsed:0.2e} seconds"
        )

        stuck_particles = io.dump_particle_info(particles, partime_file,
                                                frac_id_file)
        if control_plane_flag:
            io.dump_control_planes(particles, control_planes)

        if dump_traj:
            io.dump_trajectories(particles, min(self.ncpu, nparticles))

    if stuck_particles == 0:
        print("--> All particles exited the network")
        print("--> Graph Particle Tracking Completed Successfully.")
    else:
        print(
            f"--> Out of {nparticles} particles, {stuck_particles} particles did not exit"
        )

    return particles
