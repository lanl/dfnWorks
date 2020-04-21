"""
.. module:: graph_transport.py
   :synopsis: simulate transport on a pipe network representaiton of a DFN 
.. moduleauthor:: Shriram Srinivasan <shrirams@lanl.gov>

"""

import networkx as nx
import numpy as np
import numpy.random
import sys
import math
import scipy.special
import multiprocessing as mp

# pydfnworks modules
import pydfnworks.dfnGraph.graph_flow


def create_neighbor_list(Gtilde):
    """ Create a list of downstream neighbor vertices for every vertex on NetworkX graph obtained after running graph_flow

    Parameters
    ----------
        Gtilde: NetworkX graph 
            obtained from output of graph_flow

    Returns
    -------
        dict : nested dictionary.

    Notes
    -----
    dict[n]['child'] is a list of vertices downstream to vertex n
    dict[n]['prob'] is a list of probabilities for choosing a downstream node for vertex n
    """

    nbrs_dict = {}

    for i in nx.nodes(Gtilde):

        if Gtilde.nodes[i]['outletflag']:
            continue

        node_list = []
        prob_list = []
        nbrs_dict[i] = {}

        for v in nx.neighbors(Gtilde, i):
            delta_p = Gtilde.nodes[i]['pressure'] - Gtilde.nodes[v]['pressure']

            if delta_p > np.spacing(Gtilde.nodes[i]['pressure']):
                node_list.append(v)
                prob_list.append(Gtilde.edges[i, v]['flux'])

        if node_list:
            nbrs_dict[i]['child'] = node_list
            nbrs_dict[i]['prob'] = np.array(prob_list,
                                            dtype=float) / sum(prob_list)
        else:
            nbrs_dict[i]['child'] = None
            nbrs_dict[i]['prob'] = None

    return nbrs_dict


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
    def __init__(self):
        self.frac_seq = {}
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

    def track(self, Gtilde, nbrs_dict, frac_porosity, tdrw_flag,
              matrix_porosity, matrix_diffusivity):
        """ track a particle from inlet vertex to outlet vertex

        Parameters
        ----------
            Gtilde : NetworkX graph
                graph obtained from graph_flow

            nbrs_dict: nested dictionary
                dictionary of downstream neighbors for each vertex

        Returns
        -------

        """

        Inlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['inletflag']]

        curr_v = numpy.random.choice(Inlet)

        while True:

            if Gtilde.nodes[curr_v]['outletflag']:
                self.flag = True
                break

            if nbrs_dict[curr_v]['child'] is None:
                self.flag = False
                break

            next_v = numpy.random.choice(nbrs_dict[curr_v]['child'],
                                         p=nbrs_dict[curr_v]['prob'])

            frac = Gtilde.edges[curr_v, next_v]['frac']

            t = Gtilde.edges[curr_v, next_v]['time'] * frac_porosity

            if tdrw_flag:
                a_nondim = matrix_porosity * math.sqrt(
                    matrix_diffusivity /
                    (12 * Gtilde.edges[curr_v, next_v]['perm']))
                xi = numpy.random.random_sample()
                t_tdrw = t + math.pow(a_nondim * t / scipy.special.erfcinv(xi),
                                      2)
            else:
                t_tdrw = t

            L = Gtilde.edges[curr_v, next_v]['length']
            self.add_frac_data(frac, t, t_tdrw, L)
            curr_v = next_v

    def add_frac_data(self, frac, t, t_tdrw, L):
        """ add details of fracture through which particle traversed

        Parameters
        ----------
            self: object

            frac: int
                index of fracture in graph

            t : double
                time in seconds
            t_tdrw: double
                time in seconds
            L : double
                distance in metres

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
        self.frac_seq[frac]['dist'] += L
        self.time += t
        self.tdrw_time += t_tdrw
        self.dist += L

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
                f1.write("{:3.3E} {:3.3E} {:3.3E} {:3.3E} \n".format(
                    self.time, self.tdrw_time, self.tdrw_time - self.time,
                    self.dist))

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
                "# advective time (s)  advection+diffusion time (s)  diffusion time (s)  total advection distance covered (m)\n"
            )
    except:
        error = "ERROR: Unable to open supplied partime_file file {}\n".format(
            partime_file)
        sys.stderr.write(error)
        sys.exit(1)

    try:
        with open(frac_id_file, "w") as f2:
            f2.write("# List of fractures each particle visits\n")
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
            f1.write("{:3.3E} {:3.3E} {:3.3E} {:3.3E} \n".format(
                particle.time, particle.tdrw_time,
                particle.tdrw_time - particle.time, particle.dist))

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


def track_particle(data):
    """ Tracks a single particle through the graph

        all input parameters are in the dictionary named data 

        Parameters
        ----------
                
            Gtilde : NetworkX graph 
                obtained from graph_flow

            nbrs_dict : dict
                see function  create_neighbor_list

            frac_porosity: float
                porosity of fracture, default is 1.0

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

    particle = Particle()
    particle.set_start_time_dist(0, 0)
    particle.track(data["Gtilde"], data["nbrs_dict"], data["frac_porosity"],
                   data["tdrw_flag"], data["matrix_porosity"],
                   data["matrix_diffusivity"])

    return particle


def run_graph_transport(self,
                        Gtilde,
                        nparticles,
                        partime_file,
                        frac_id_file,
                        frac_porosity=1.0,
                        tdrw_flag=False,
                        matrix_porosity=0.02,
                        matrix_diffusivity=1e-11):
    """ Run  particle tracking on the given NetworkX graph

    Parameters
    ----------
        self : object
            DFN Class
            
        Gtilde : NetworkX graph 
            obtained from graph_flow

        nparticles: int 
            number of particles

        partime_file : string
            name of file to  which the total travel times and lengths will be written for each particle

        frac_id_file : string
            name of file to which detailed information of each particle's travel will be written
        
        frac_porosity: float
            porosity of fracture, default is 1.0
        tdrw_flag : Bool
            if False, matrix_porosity, matrix_diffusivity are ignored
        matrix_porosity: float
            default is 0.02
        matrix_diffusivity: float
            default is 1e-11 in SI units

    Returns
    -------

    Notes
    -----
    Information on individual functions is found therein
    """

    nbrs_dict = create_neighbor_list(Gtilde)

    print("--> Creating downstream neighbor list")

    Inlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['inletflag']]

    pfailcount = 0
    print("--> Starting particle tracking for %d particles" % nparticles)

    if self.ncpu > 1:
        print("--> Using %d processors" % self.ncpu)
        mp_input = []
        for i in range(nparticles):

            data = {}
            data["Gtilde"] = Gtilde
            data["nbrs_dict"] = nbrs_dict
            data["frac_porosity"] = frac_porosity
            data["tdrw_flag"] = tdrw_flag
            data["matrix_porosity"] = matrix_porosity
            data["matrix_diffusivity"] = matrix_diffusivity
            #data["partime_file"] = partime_file
            #data["frac_id_file"] = frac_id_file
            mp_input.append(data)

        pool = mp.Pool(self.ncpu)
        particles = pool.map(track_particle, mp_input)
        pool.close()
        pool.join()
        pool.terminate()
        print("--> Tracking Complete")
        print("--> Writing Data to files: {} and {}".format(
            partime_file, frac_id_file))
        dump_particle_info(particles, partime_file, frac_id_file)
        print("--> Writing Data Complete")

    else:
        prepare_output_files(partime_file, frac_id_file)
        for i in range(nparticles):
            if i % 1000 == 0:
                print("--> Starting particle %d out of %d" % (i, nparticles))
            particle_i = Particle()
            particle_i.set_start_time_dist(0, 0)
            particle_i.track(Gtilde, nbrs_dict, frac_porosity, tdrw_flag,
                             matrix_porosity, matrix_diffusivity)

            if particle_i.flag:
                particle_i.write_file(partime_file, frac_id_file)
            else:
                pfailcount += 1

    if pfailcount == 0:
        print("--> All particles exited")
    else:
        print("--> Out of {} particles, {} particles did not exit".format(
            nparticles, pfailcount))
    return
