import sys
import numpy as np


from pydfnworks.general.logging import local_print_log

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

    from pydfnworks.dfnGraph.graph_tdrw_unlimited import unlimited_matrix_diffusion
    from pydfnworks.dfnGraph.graph_tdrw_cortado import limited_matrix_diffusion_cortado
    from pydfnworks.dfnGraph.graph_tdrw_roubinet import limited_matrix_diffusion_roubinet


    def __init__(self, particle_number, ip, tdrw_flag, tdrw_method, matrix_porosity,
                 matrix_diffusivity, fracture_spacing, trans_prob,
                 transfer_time, cp_flag, control_planes, direction):
        self.particle_number = particle_number
        self.ip = ip
        self.curr_node = ip
        self.curr_velocity = 0
        self.curr_coords = list
        self.next_node = None
        self.advect_time = 0
        self.delta_t = 0
        self.matrix_diffusion_time = 0
        self.delta_t_md = 0
        self.total_time = 0
        self.length = 0
        self.delta_l = 0
        self.beta = 0
        self.delta_beta = 0
        self.tdrw_flag = tdrw_flag
        self.tdrw_method = tdrw_method
        self.matrix_porosity = matrix_porosity
        self.matrix_diffusivity = matrix_diffusivity
        self.fracture_spacing = fracture_spacing
        self.trans_prob = trans_prob
        self.transfer_time = transfer_time
        self.cp_flag = cp_flag
        self.control_planes = control_planes
        self.cp_index = 0
        self.direction = direction
        self.exit_flag = False
        self.frac = int()
        self.frac_seq = []
        self.cp_adv_time = []
        self.cp_tdrw_time = []
        self.velocity = []
        self.lengths = []
        self.times = []
        self.coords = []


    def initalize(self,G):
        self.frac = (G.nodes[self.curr_node]['frac'][1])

    def interpolate_time(self, x0, t1, t2, x1, x2):
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
                
        """
        return t1 + (t2 - t1) / (x2 - x1) * (x0 - x1)

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
            self.delta_beta = (
                2.0 * G.edges[self.curr_node, self.next_node]['length']) / (
                    G.edges[self.curr_node, self.next_node]['b'] *
                    G.edges[self.curr_node, self.next_node]['velocity'])
            self.curr_velocity = G.edges[self.curr_node,
                                         self.next_node]['velocity']
            self.curr_coords = (G.nodes[self.curr_node]['x'],
                                G.nodes[self.curr_node]['y'],
                                G.nodes[self.curr_node]['z'])

    def cross_control_plane(self, G):
        """ Check if a particle crossed the control plane

        Parameters
        ----------
            G : NetworkX graph
                graph obtained from graph_flow

        Returns
        -------
            None
        """

        while G.nodes[self.next_node][self.direction] > self.control_planes[
                self.cp_index]:
            ## get information for interpolation to get the time at point of crossing.
            x0 = self.control_planes[self.cp_index]
            t1 = self.advect_time
            t2 = self.advect_time + self.delta_t
            x1 = G.nodes[self.curr_node][self.direction]
            x2 = G.nodes[self.next_node][self.direction]
            tau = self.interpolate_time(x0, t1, t2, x1, x2)
            # print(f"control plane: {x0:0.2f}, x1: {x1:0.2f}, x2:{x2:0.2f}, t1: {t1:0.2e}. t2: {t2:0.2e}, tau: {tau:0.2e}")
            if tau < 0:

                local_print_log(
                    f"control plane: {x0:0.2f}, x1: {x1:0.2f}, x2:{x2:0.2f}, t1: {t1:0.2e}. t2: {t2:0.2e}, tau: {tau:0.2e}"
                )
                error = "Error. Interpolated negative travel time."
                local_print_log(error,'error')
            # print(f"--> crossed control plane at {control_planes[cp_index]} {direction} at time {tau}")
            self.cp_adv_time.append(tau)
            if self.tdrw_flag:
                t1 = self.total_time
                t2 = self.total_time + self.delta_t_md + self.delta_t
                tau = self.interpolate_time(x0, t1, t2, x1, x2)
                self.cp_tdrw_time.append(tau)
            else:
                self.cp_tdrw_time.append(tau)

            self.cp_index += 1
            # if we're crossed all the control planes, turn off cp flag for this particle
            if self.cp_index >= len(self.control_planes):
                self.cp_flag = False
                break

    def update(self):
        """ Update particles trajectory information

        Parameters
        ----------
            particle object

        Returns
        -------
            None
        """
        self.advect_time += self.delta_t
        self.matrix_diffusion_time += self.delta_t_md
        self.total_time += self.delta_t + self.delta_t_md
        self.length += self.delat_l
        self.beta += self.delta_beta
        self.frac_seq.append(self.frac)
        self.curr_node = self.next_node

        self.velocity.append(self.curr_velocity)
        self.lengths.append(self.delat_l)
        self.times.append(self.delta_t)
        self.coords.append(self.curr_coords)
        # self.fracs.append(self.frac)

    def cleanup_frac_seq(self):
        frac_seq = [self.frac_seq[0]]
        for frac in self.frac_seq:
            if frac != frac_seq[-1]:
                frac_seq.append(frac)

        self.frac_seq = frac_seq

    def track(self, G, nbrs_dict):
        """ Track particle. Breaks up advection and matrix diffusion

        Parameters
        ----------
            G : NetworkX graph
                graph obtained from graph_flow

        Returns
        -------
            None
        """
        np.random.seed(self.particle_number)
        self.initalize(G)
        while not self.exit_flag:
            self.advect(G, nbrs_dict)
            if self.exit_flag:
                self.update()
                self.cleanup_frac_seq()
                break

            if self.tdrw_flag:
                if self.fracture_spacing is None:
                    self.unlimited_matrix_diffusion(G)
                else:
                    if self.tdrw_method == "cortado":
                        self.limited_matrix_diffusion_cortado(G)
                    elif self.tdrw_method == "roubinet":
                        self.limited_matrix_diffusion_roubinet(G)
                    else:
                        print("unknown method")

            if self.cp_flag:
                self.cross_control_plane(G)
            self.update()
