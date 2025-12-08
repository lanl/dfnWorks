

from scipy.interpolate import PchipInterpolator
import numpy as np
import matplotlib.pyplot as plt
import mpmath as mp


def Psi_star(lmbda, eps):
    # Laplace transform of the CDF Ψ*_ε(λ)
    # eps must satisfy 0 < eps < 1 for a slab of unit width in the note
    sqrt_l = mp.sqrt(lmbda)
    return mp.cosh((1 - eps) * sqrt_l) / (lmbda * mp.cosh(sqrt_l))

def Psi_cdf(t, eps, method="dehoog"):
    # Inverse Laplace transform of Ψ*_ε at time t
    # method can be "dehoog" or "talbot"
    if t <= 0:
        return mp.mpf("0.0")
    F = lambda s: Psi_star(s, eps)
    return mp.invertlaplace(F, t, method=method)

def Psi_pdf(t, eps, method="dehoog", h=None):
    # Density ψ_ε(t) = d/dt Ψ_ε(t)
    # You can either invert ψ*_ε directly or differentiate the CDF numerically
    # This version inverts ψ*_ε for accuracy
    if t <= 0:
        return mp.mpf("0.0")
    psi_star = lambda s: mp.cosh((1 - eps) * mp.sqrt(s)) / mp.cosh(mp.sqrt(s))
    return mp.invertlaplace(psi_star, t, method=method)


def _make_inverse_cdf_spline_for_times(num_samples = 100, eps = 1e-4, precision = 40):
    # --- compute CDF and PDF values ---
    mp.mp.dps = precision
    num_samples = num_samples
    eps = mp.mpf(eps)
    times = [10**x for x in np.linspace(-8, 3, num_samples)]

    cdf_vals = np.zeros(num_samples, dtype=float)

    for i, t in enumerate(times):
        cdf_vals[i] = float(Psi_cdf(t, eps, method="dehoog"))

    # --- build inverse CDF spline (t vs cdf) ---
    order = np.argsort(cdf_vals)
    cdf_sorted = np.clip(cdf_vals[order], 0, 1)
    t_sorted = np.maximum(np.array(times)[order], 0)

    # remove duplicates
    cdf_unique, idx = np.unique(cdf_sorted, return_index=True)
    t_unique = np.asarray(t_sorted[idx])

    finite_md_times = t_unique
    finite_md_cdf = cdf_unique

    return finite_md_times, finite_md_cdf 


def limited_matrix_diffusion_dentz(self,G):
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


