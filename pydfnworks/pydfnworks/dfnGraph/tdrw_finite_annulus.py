
import numpy as np
import mpmath as mp


def Psi_star_annulus(lmbda, eps):
    # Laplace transform of the CDF for diffusion return time in an annulus
    # Geometry: absorbing wall at one end, reflecting wall at the other
    # eps = r'/w, dimensionless release position from the absorbing wall (0 < eps <= 1)
    # F(s) = [ exp(-eps*q) + exp(-(2-eps)*q) ] / [ (1 + exp(-2q)) * s ]
    # where q = sqrt(s * tauD);  tauD absorbed into s at call time (s -> s*tauD)
    sqrt_l = mp.sqrt(lmbda)
    numerator   = mp.exp(-eps * sqrt_l) + mp.exp(-(2 - eps) * sqrt_l)
    denominator = (1 + mp.exp(-2 * sqrt_l)) * lmbda
    return numerator / denominator


def Psi_cdf_annulus(t, eps, method="dehoog"):
    # Inverse Laplace transform of Psi_star_annulus at time t
    # Returns cumulative return-time distribution P(T_return <= t)
    if t <= 0:
        return mp.mpf("0.0")
    F = lambda s: Psi_star_annulus(s, eps)
    return mp.invertlaplace(F, t, method=method)


def Psi_pdf_annulus(t, eps, method="dehoog"):
    # Density psi(t) = d/dt Psi(t), the first-passage time PDF
    # Inverts the PDF Laplace transform directly for accuracy
    # psi*(s) = [ exp(-eps*q) + exp(-(2-eps)*q) ] / (1 + exp(-2q))
    if t <= 0:
        return mp.mpf("0.0")
    psi_star = lambda s: (mp.exp(-eps * mp.sqrt(s)) + mp.exp(-(2 - eps) * mp.sqrt(s))) / (1 + mp.exp(-2 * mp.sqrt(s)))
    return mp.invertlaplace(psi_star, t, method=method)


def _make_inverse_cdf_annulus(num_samples=100, eps=1e-4, precision=40):
    # Precompute the inverse CDF table for annulus return-time sampling
    # Returns (times, cdf_vals) arrays for use with np.interp
    mp.mp.dps = precision
    eps = mp.mpf(eps)
    times = [10**x for x in np.linspace(-8, 3, num_samples)]

    cdf_vals = np.zeros(num_samples, dtype=float)

    for i, t in enumerate(times):
        cdf_vals[i] = float(Psi_cdf_annulus(t, eps, method="dehoog"))

    # sort by cdf value to build the inverse CDF (cdf -> time) lookup
    order = np.argsort(cdf_vals)
    cdf_sorted = np.clip(cdf_vals[order], 0, 1)
    t_sorted   = np.maximum(np.array(times)[order], 0)

    # remove duplicate cdf values to ensure monotone interpolation
    cdf_unique, idx = np.unique(cdf_sorted, return_index=True)
    t_unique = np.asarray(t_sorted[idx])

    return t_unique, cdf_unique


def limited_matrix_diffusion_annulus(self, G):
    """ Matrix diffusion with finite annular block geometry

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None

    Notes
    -----
        Samples diffusion return times from a finite annular matrix block
        with one absorbing boundary (fracture-matrix interface) and one
        reflecting boundary (block interior).

        The dimensionless release position eps = r'/w is fixed at 1e-4,
        placing the particle just inside the absorbing wall.

        tauD = w^2 / D_matrix sets the diffusion timescale; it is stored
        on the particle as self.tau_D and used to rescale sampled times.

        The inverse CDF table (self.transfer_time, self.trans_prob) must
        be precomputed via _make_inverse_cdf_annulus and attached to the
        particle before transport begins.

        All other parameters are attached to the particle class.
    """

    eps = 1e-4
    b = G.edges[self.curr_node, self.next_node]['b']

    # trapping rate into the matrix block
    gamma = (2 * self.matrix_porosity * self.matrix_diffusivity) / (b * eps * self.fracture_spacing)

    # average number of trapping events during this advective step
    average_number_of_trapping_events = self.delta_t * gamma

    # sample number of trapping events from Poisson distribution
    n = np.random.poisson(average_number_of_trapping_events)

    # sample uniform random variables and map to return times via inverse CDF
    xi = np.random.uniform(size=n)
    tmp = self.tau_D * np.interp(xi, self.trans_prob, self.transfer_time)

    self.delta_t_md = tmp.sum()
