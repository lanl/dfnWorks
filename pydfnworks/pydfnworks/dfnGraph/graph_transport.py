"""
.. module:: graph_transport.py
   :synopsis: simulate transport on a pipe network representaiton of a DFN 
.. moduleauthor:: Shriram Srinivasan <shrirams@lanl.gov>, Jeffrey Hyman <jhyman@lanl.gov>

"""

import timeit
import sys
import networkx as nx
import numpy as np
import multiprocessing as mp

# pydfnworks graph modules modules
import pydfnworks.dfnGraph.particle_io as io
from pydfnworks.dfnGraph.graph_tdrw import set_up_limited_matrix_diffusion
from pydfnworks.dfnGraph.particle_class import Particle
from pydfnworks.general.logging import local_print_log


def track_particle(data, verbose=False):
    """ Tracks a single particle through the graph

        all input parameters are in the dictionary named data 

        Parameters
        ----------
            data : dict
                Dictionary of parameters the includes particle_number, initial_position, 
                tdrw_flag, matrix_porosity, matrix_diffusivity, cp_flag, control_planes,
                 direction, G, and nbrs_dict. 

            verbose : bool
                Toggles verbosity 

        Returns
        -------
            particle : object
                Particle will full trajectory

    """
    if verbose:
        p = mp.current_process()
        _, cpu_id = p.name.split("-")
        cpu_id = int(cpu_id)
        local_print_log(
            f"--> Particle {data['particle_number']} is starting on worker {cpu_id}"
        )

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
        local_print_log(
            f"--> Particle {data['particle_number']} is complete on worker {cpu_id}"
        )
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
    local_print_log(f"--> There are {cnt} inlet nodes")
    if cnt == 0:
        error = "Error. There are no nodes in the inlet.\nExiting"
        local_print_log(error, 'error')

    # Uniform Distribution for particles
    if initial_positions == "uniform":
        local_print_log("--> Using uniform initial positions.")
        ip = np.zeros(nparticles).astype(int)
        n = int(np.ceil(nparticles / cnt))
        local_print_log(f"--> {n} particles will be placed at every inflow node.\n")
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
        local_print_log("--> Using flux-weighted initial positions.\n")
        vol_flow_rate = np.zeros(cnt)
        for i, u in enumerate(inlet_nodes):
            for v in G.successors(u):
                vol_flow_rate[i] += G.edges[u, v]['vol_flow_rate']

        vol_flow_rate /= vol_flow_rate.sum()
        vol_flow_rate_cnts_ceil = [np.ceil(nparticles * i) for i in vol_flow_rate]
        vol_flow_rate_cnts = [np.floor(nparticles * i) for i in vol_flow_rate]
        nparticles = int(sum(vol_flow_rate_cnts))
        nparticles_ceil = int(sum(vol_flow_rate_cnts_ceil))
        print(f"particle compare: {nparticles}\t{nparticles_ceil}\n")
        ip = np.zeros(nparticles).astype(int)
        ## Populate ip with Flux Cnts
        ## this could be cleaned up using clever indexing
        inflow_idx = 0
        inflow_cnt = 0
        for i in range(nparticles):
            ip[i] = inlet_nodes[inflow_idx]
            inflow_cnt += 1
            if inflow_cnt >= vol_flow_rate_cnts[inflow_idx]:
                inflow_idx += 1
                inflow_cnt = 0
        np.savetxt("inflow_vol_flow_rates.dat", vol_flow_rate)
    # Throw error if unknown initial position is provided
    else:
        error = f"Error. Unknown initial_positions input {initial_positions}. Options are uniform or flux \n"
        local_print_log(error, 'error')

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
        local_print_log(error, 'error')
    elif matrix_porosity < 0 or matrix_porosity > 1:
        error = f"Error. Requested TDRW but value for matrix_porosity provided is outside of [0,1]. Value provided {matrix_porosity}\n"
        local_print_log(error, 'error')
    if matrix_diffusivity is None:
        error = f"Error. Requested TDRW but no value for matrix_diffusivity was provided\n"
        local_print_log(error, 'error')

    if fracture_spacing is not None:
        if fracture_spacing <= 0:
            error = f"Error. Non-positive value for fracture_spacing was provided.\nValue {fracture_spacing}\nExiting program"
            local_print_log(error, 'error')


def check_control_planes(control_planes, direction):
    control_plane_flag = False
    if not type(control_planes) is list:
        error = f"Error. provided controls planes are not a list\n"
        local_print_log(error, 'error')
    else:
        # add None to indicate the end of the control plane list
        control_plane_flag = True

    if direction is None:
        error = f"Error. Primary direction not provided. Required for control planes\n"
        local_print_log(error, 'error')
    elif direction not in ['x', 'y', 'z']:
        error = f"Error. Primary direction is not known. Acceptable values are x,y, and z\n"
        local_print_log(error, 'error')

    local_print_log(f"--> Control Planes: {control_planes}")
    local_print_log(f"--> Direction: {direction}")
    return control_plane_flag


def run_graph_transport(self,
                        G,
                        nparticles,
                        partime_file,
                        frac_id_file=None,
                        format='hdf5',
                        initial_positions="uniform",
                        dump_traj=False,
                        tdrw_flag=False,
                        matrix_porosity=None,
                        matrix_diffusivity=None,
                        fracture_spacing=None,
                        control_planes=None,
                        direction=None,
                        cp_filename='control_planes'):
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
    ## the flow graph needs to be a global variable so all processors can access it
    ## without making a copy of it.
    global G_global
    G_global = nx.Graph()
    G_global = G.copy()

    if not format in ['ascii', 'hdf5']:
        error = (
            f"--> Error. Unknown file format provided in run_graph_transport.\n\n--> Provided value is {format}.\n--> Options: 'ascii' or 'hdf5'.\n\nExitting\n\n"
        )
        self.print_log(error, 'error')

    self.print_log("--> Running Graph Particle Tracking")
    
    # Check parameters for TDRW
    if tdrw_flag:
        check_tdrw_params(matrix_porosity, matrix_diffusivity,
                          fracture_spacing)
        self.print_log(
            f"--> Running particle transport with TDRW.\n--> Matrix porosity {matrix_porosity}.\n--> Matrix Diffusivity {matrix_diffusivity} m^2/s"
        )

    if control_planes is None:
        control_plane_flag = False
    else:
        control_plane_flag = check_control_planes(
            control_planes=control_planes, direction=direction)
    self.print_log(f"--> Control Plane Flag {control_plane_flag}")

    self.print_log("--> Creating downstream neighbor list")
    global nbrs_dict
    nbrs_dict = create_neighbor_list(G)

    self.print_log("--> Getting initial Conditions")
    ip, nparticles = get_initial_posititions(G, initial_positions, nparticles)

    self.print_log(f"--> Starting particle tracking for {nparticles} particles")

    if dump_traj:
        self.print_log(f"--> Writing trajectory information to file")

    if fracture_spacing is not None:
        self.print_log(f"--> Using limited matrix block size for TDRW")
        self.print_log(f"--> Fracture spacing {fracture_spacing:0.2e} [m]")
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
                self.print_log(f"--> Starting particle {i} out of {nparticles}")
            particle = Particle(i, ip[i], tdrw_flag, matrix_porosity,
                                matrix_diffusivity, fracture_spacing,
                                trans_prob, transfer_time, control_plane_flag,
                                control_planes, direction)
            particle.track(G, nbrs_dict)
            particles.append(particle)

        elapsed = timeit.default_timer() - tic
        self.print_log(
            f"--> Main Tracking Loop Complete. Time Required {elapsed:0.2e} seconds"
        )
        stuck_particles = io.dump_particle_info(particles, partime_file,
                                                frac_id_file, format)
        if control_plane_flag:
            io.dump_control_planes(particles, control_planes, cp_filename,
                                   format)

        if dump_traj:
            io.dump_trajectories(particles, 1)

    if self.ncpu > 1:
        self.print_log(f"--> Using {self.ncpu} processors")
        ## Prepare input data
        inputs = []

        tic = timeit.default_timer()
        pool = mp.Pool(min(self.ncpu, nparticles))

        particles = []

        def gather_output(output):
            particles.append(output)

        for i in range(nparticles):
            data = {}
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
            pool.apply_async(track_particle,
                             args=(data, ),
                             callback=gather_output)

        pool.close()
        pool.join()
        pool.terminate()

        elapsed = timeit.default_timer() - tic
        self.print_log(
            f"--> Main Tracking Loop Complete. Time Required {elapsed:0.2e} seconds"
        )

        stuck_particles = io.dump_particle_info(particles, partime_file,
                                                frac_id_file, format)
        if control_plane_flag:
            io.dump_control_planes(particles, control_planes, cp_filename,
                                   format)

        if dump_traj:
            io.dump_trajectories(particles, min(self.ncpu, nparticles))

    if stuck_particles == 0:
        self.print_log("--> All particles exited the network")
        self.print_log("--> Graph Particle Tracking Completed Successfully.")
    else:
        self.print_log(
            f"--> Out of {nparticles} particles, {stuck_particles} particles did not exit"
            'warning')

    # Clean up and delete the global versions
    del G_global
    del nbrs_dict

    return particles