

from scipy.interpolate import PchipInterpolator
import numpy as np
import matplotlib.pyplot as plt
import mpmath as mp
import os 
from pydfnworks.general.logging import local_print_log

def _load_finite_time_cdf(tdrw_filename):

    data = np.genfromtxt(tdrw_filename)

    if data.ndim != 2 or data.shape[1] < 2:
        local_print_log(f"Error. File {tdrw_filename} does not contain at least two columns.", "error")

    finite_md_times = data[:, 0]
    finite_md_cdf = data[:, 1]

    return finite_md_times, finite_md_cdf


def limited_matrix_diffusion_from_file(self, G):
    """ Matrix diffusion with limited block size

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None

    Notes
    -----------
        All parameters are attached to the particle class 
    """

    # print(self.total_time,self.advect_time,self.matrix_diffusion_time)
    # print("\nsegment limited sampling")
    eps = 1e-4
    # print(self.advect_time, self.delta_t )
    # b = (2*self.delta_t) / self.beta
    b = G.edges[self.curr_node, self.next_node]['b']
    # print(f"b: {b_eff}")
    # # traping rate 
    gamma = (2*self.matrix_porosity*self.matrix_diffusivity)/(b * eps * self.fracture_spacing)
    # gamma = (2*self.matrix_porosity*self.matrix_diffusivity)/(b * eps) 
    #print(f"gamma: {gamma}")
    # average number of trapping events in gamma * advective time
    average_number_of_trapping_events = self.delta_t * gamma
    #print(f"average_number_of_trapping_events: {average_number_of_trapping_events}")
    # number of trapping events in sampled from a poisson distribution
    n = np.random.poisson(average_number_of_trapping_events)
    # print(f"n: {n}")
    xi = np.random.uniform(size = n)
    # print(xi)
    # 
    tmp = self.tau_D * np.interp(xi, self.trans_prob, self.transfer_time)
    # print("*")
    # print(self.transfer_time)
    # print(self.trans_prob)
    # print(tmp)
    # exit(1) 
    # tmp = self.tau_D * self.inv_spline(xi)
    self.delta_t_md = tmp.sum() 
    #print(self.delta_t_md)
    #print("\n")
    # self.total_time = self.advect_time + self.matrix_diffusion_time
    #print(self.total_time,self.advect_time,self.matrix_diffusion_time)


