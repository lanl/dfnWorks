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
from pydfnworks.dfnGraph.particle_class import Particle
from pydfnworks.general.logging import local_print_log

from pydfnworks.dfnGraph.graph_tdrw import _check_tdrw_params, _set_up_limited_matrix_diffusion
from pydfnworks.dfnGraph.graph_transport_setup_functions import _create_neighbor_list, _get_initial_posititions, _check_control_planes


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

    try:
        particle = Particle(particle_number = data["particle_number"], 
                            ip = data["initial_position"],
                            tdrw_flag = data["tdrw_flag"], 
                            tdrw_model = data["tdrw_model"],
                            matrix_porosity = data["matrix_porosity"],
                            matrix_diffusivity = data["matrix_diffusivity"], 
                            fracture_spacing = data["fracture_spacing"],
                            transfer_time = data["transfer_time"],
                            trans_prob = data["trans_prob"], 
                            cp_flag = data["cp_flag"], 
                            control_planes = data["control_planes"],
                            direction = data["direction"])
    except Exception as e:
        local_print_log(f"Issue initializing particle {e}", "warning")

    # # get current process information
    global nbrs_dict
    global G_global
    particle.track(G_global, nbrs_dict)
    if verbose:
        local_print_log(
            f"--> Particle {data['particle_number']} is complete on worker {cpu_id}"
        )
    return particle


def run_graph_transport(self,
                        G,
                        nparticles,
                        partime_file,
                        frac_id_file=None,
                        format='hdf5',
                        initial_positions="uniform",
                        dump_traj=False,
                        tdrw_flag=False,
                        tdrw_model = 'infinite',
                        matrix_porosity=None,
                        matrix_diffusivity=None,
                        fracture_spacing=None,
                        control_planes=None,
                        direction=None,
                        cp_filename='control_planes',
                        verbose = False):
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

    if control_planes is None:
        control_plane_flag = False
    else:
        control_plane_flag = _check_control_planes(
            control_planes=control_planes, direction=direction)
    self.print_log(f"--> Control Plane Flag {control_plane_flag}")

    self.print_log("--> Creating downstream neighbor list")
    global nbrs_dict
    nbrs_dict = _create_neighbor_list(G)

    self.print_log("--> Getting initial Conditions")
    ip, nparticles = _get_initial_posititions(G, initial_positions, nparticles)
    self.print_log(f"--> Starting particle tracking for {nparticles} particles")

    if dump_traj:
        self.print_log(f"--> Writing trajectory information to file")

    # Check parameters for TDRW
    if tdrw_flag:
        _check_tdrw_params(matrix_porosity, matrix_diffusivity,
                          fracture_spacing, tdrw_model)
        
        if tdrw_model in ("roubinet", "dentz"):
            self.print_log(f"--> Using limited matrix block size for TDRW")
            self.print_log(f"--> Fracture spacing {fracture_spacing:0.2e} [m]")
            transfer_time, trans_prob = _set_up_limited_matrix_diffusion(G,
                                                        tdrw_model,
                                                        fracture_spacing,
                                                        matrix_porosity,
                                                        matrix_diffusivity)
        else:
            trans_prob = None
            transfer_time = None           
    else:
        trans_prob = None
        transfer_time = None

    if self.ncpu == 1:
        self.print_log("--> Running in Serial")
        tic = timeit.default_timer()
        particles = []
        for i in range(nparticles):
            if i % 1000 == 0:
                self.print_log(f"--> Starting particle {i} out of {nparticles}")
            particle = Particle(particle_number = i, 
                                ip = ip[i], 
                                tdrw_flag = tdrw_flag, 
                                tdrw_model = tdrw_model, 
                                matrix_porosity = matrix_porosity,
                                matrix_diffusivity = matrix_diffusivity, 
                                fracture_spacing = fracture_spacing,
                                transfer_time = transfer_time, 
                                trans_prob = trans_prob,
                                cp_flag = control_plane_flag,
                                control_planes = control_planes, 
                                direction = direction)
            
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
            data["tdrw_model"] = tdrw_model
            data["matrix_porosity"] = matrix_porosity
            data["matrix_diffusivity"] = matrix_diffusivity
            data["fracture_spacing"] = fracture_spacing
            data["transfer_time"] = transfer_time
            data["trans_prob"] = trans_prob
            data["cp_flag"] = control_plane_flag
            data["control_planes"] = control_planes
            data["direction"] = direction
            pool.apply_async(track_particle,
                             args=(data, verbose),
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