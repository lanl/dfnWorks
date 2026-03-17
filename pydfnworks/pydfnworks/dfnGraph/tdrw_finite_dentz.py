import numpy as np
from math import factorial


def _stehfest_coefficients(N=16):
    # Compute Stehfest coefficients V_i for i = 1 ... N. N must be even.
    if N % 2 != 0:
        raise ValueError("Stehfest N must be even.")
    M = N // 2
    V = np.zeros(N)
    for i in range(1, N + 1):
        total = 0.0
        for k in range(int((i + 1) // 2), min(i, M) + 1):
            num = (k ** M) * factorial(2 * k)
            den = (factorial(M - k) * factorial(k) * factorial(k - 1)
                   * factorial(i - k) * factorial(2 * k - i))
            total += num / den
        V[i - 1] = ((-1) ** (i + M)) * total
    return V


def Psi_star(s, eps):
    # Laplace transform of the slab CDF Psi*_eps(s)
    # cosh((1-eps)*sqrt(s)) / (s * cosh(sqrt(s)))
    #
    # Scaled form to avoid cosh overflow at large s:
    # cosh((1-eps)*q) / cosh(q) = exp(-eps*q) * (1 + exp(-2*(1-eps)*q)) / (1 + exp(-2*q))
    # where q = sqrt(s). Both exp terms decay for large q so no overflow.
    q = np.sqrt(s)
    num = np.exp(-eps * q) * (1.0 + np.exp(-2.0 * (1.0 - eps) * q))
    den = 1.0 + np.exp(-2.0 * q)
    return num / (den * s)


def Psi_pdf_star(s, eps):
    # Laplace transform of the slab first-passage time PDF
    # psi*(s) = s * Psi*(s)
    return Psi_star(s, eps) * s


def _stehfest_invert(F, t_arr, V, **kwargs):
    # Invert F at times t_arr using the Stehfest algorithm
    # f(t) ≈ (ln2/t) * sum_i V_i * F(i*ln2/t)
    ln2 = np.log(2.0)
    f   = np.zeros(len(t_arr))
    for idx, ti in enumerate(t_arr):
        s_vals = np.array([(i + 1) * ln2 / ti for i in range(len(V))])
        f[idx] = (ln2 / ti) * np.dot(V, F(s_vals, **kwargs))
    return f


def _make_inverse_cdf_spline_for_times(num_samples=100, eps=1e-4, stehfest_n=16):
    # Precompute the inverse CDF table for slab (Dentz) return-time sampling
    #
    # Replaces the original mpmath.invertlaplace implementation with
    # Stehfest inversion in double precision -- orders of magnitude faster.
    #
    # Scaled cosh formulation avoids overflow for all s values.
    # t_min=1e-10 ensures Stehfest samples s >> 1/eps^2 for correct
    # early-time behavior (eps=1e-4 requires s ~ 1e8, t ~ ln2/1e8 ~ 1e-9).
    #
    # Returns (times, cdf_vals) arrays for use with np.interp

    V     = _stehfest_coefficients(stehfest_n)
    times = np.logspace(-10, 3, num_samples)

    cdf_vals = _stehfest_invert(Psi_star, times, V, eps=eps)

    # sort by cdf value to build the inverse CDF (cdf -> time) lookup
    order      = np.argsort(cdf_vals)
    cdf_sorted = np.clip(cdf_vals[order], 0, 1)
    t_sorted   = np.maximum(times[order], 0)

    # remove duplicate cdf values to ensure monotone interpolation
    cdf_unique, idx = np.unique(cdf_sorted, return_index=True)
    t_unique = np.asarray(t_sorted[idx])

    return t_unique, cdf_unique


def limited_matrix_diffusion_dentz(self, G):
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

    eps = 1e-4
    b = G.edges[self.curr_node, self.next_node]['b']

    # trapping rate
    gamma = (2 * self.matrix_porosity * self.matrix_diffusivity) / (b * eps * self.fracture_spacing)

    # average number of trapping events during this advective step
    average_number_of_trapping_events = self.delta_t * gamma

    # sample number of trapping events from Poisson distribution
    n = np.random.poisson(average_number_of_trapping_events)

    # sample uniform random variables and map to return times via inverse CDF
    xi  = np.random.uniform(size=n)
    tmp = self.tau_D * np.interp(xi, self.trans_prob, self.transfer_time)

    self.delta_t_md = tmp.sum()