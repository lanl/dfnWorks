
import numpy as np
from scipy.special import ive, kve
from math import factorial


def _stehfest_coefficients(N=16):
    # Compute Stehfest coefficients V_i for i = 1 ... N
    # N must be even. N=16 recommended for double precision.
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


def Psi_star_annulus(s, eps, tau0, tau1):
    # Laplace transform of the CDF for diffusion return time in a cylindrical annulus
    #
    # Geometry: cylindrical annulus with inner radius r0 (absorbing, fracture-matrix
    # interface) and outer radius r1 (reflecting, block interior).
    # A particle is released at r' = r0*(1+eps), just inside the absorbing wall.
    #
    # Parameters:
    #   eps  = (r' - r0) / r1   dimensionless release position  (0 < eps < 1)
    #   tau0 = r0^2 / D         inner-radius timescale ratio r0^2/r1^2
    #   tau1 = r1^2 / D         outer-radius timescale (reference = 1)
    #
    # Uses scipy scaled Bessel functions throughout:
    #   ive(n, x) = exp(-x) * In(x)   matches MATLAB besseli(n, x, 1)
    #   kve(n, x) = exp(x)  * Kn(x)   matches MATLAB besselk(n, x, 1)
    #
    # Exponential compensation factors normalize by exp(2*q0 - 2*q1) so
    # the ratio goes correctly to 0 as s -> inf:
    #   F_psi(s->0)   = 1
    #   F_psi(s->inf) = 0
    #
    # F_cdf(s) = F_psi(s) / s

    q0     = np.sqrt(s * tau0)
    q0_eps = (1.0 + eps) * q0
    q1     = np.sqrt(s * tau1)

    I0e_eps = ive(0, q0_eps)
    K0e_eps = kve(0, q0_eps)
    I0e_0   = ive(0, q0)
    K0e_0   = kve(0, q0)
    I1e_1   = ive(1, q1)
    K1e_1   = kve(1, q1)

    # exponential compensation factors, clipped to avoid overflow
    e1 = np.exp(np.clip( eps * q0,               -500, 500))
    e2 = np.exp(np.clip(-eps * q0 - 2*q0 + 2*q1, -500, 500))
    e3 = np.exp(np.clip(-(2*q0 - 2*q1),           -500, 500))

    numerator   = e1 * I0e_eps * K1e_1 + e2 * K0e_eps * I1e_1
    denominator = I0e_0 * K1e_1        + e3 * K0e_0   * I1e_1

    return numerator / (denominator * s)


def Psi_pdf_star_annulus(s, eps, tau0, tau1):
    # Laplace transform of the first-passage time PDF
    # psi*(s) = s * F_cdf(s)
    return Psi_star_annulus(s, eps, tau0, tau1) * s


def _stehfest_invert(F, t_arr, V, **kwargs):
    # Invert F at times t_arr using the Stehfest algorithm
    # f(t) ≈ (ln2/t) * sum_i V_i * F(i*ln2/t)
    ln2 = np.log(2.0)
    f   = np.zeros(len(t_arr))
    for idx, ti in enumerate(t_arr):
        s_vals = np.array([(i + 1) * ln2 / ti for i in range(len(V))])
        f[idx] = (ln2 / ti) * np.dot(V, F(s_vals, **kwargs))
    return f


def _make_inverse_cdf_annulus(num_samples=100, eps=0.5, tau0=0.5, tau1=1.0, stehfest_n=16):
    # Precompute the inverse CDF table for cylindrical annulus return-time sampling
    #
    # Parameters:
    #   eps  = (r'-r0)/r1   dimensionless release position  (0 < eps < 1)
    #   tau0 = r0^2/r1^2    inner-radius timescale ratio
    #   tau1 = 1.0          outer-radius reference timescale
    #
    # Defaults are physically meaningful values that produce a well-behaved CDF.
    # Update once Marco Dentz confirms the physical parameter mapping.
    #
    # Returns (times, cdf_vals) arrays for use with np.interp

    V     = _stehfest_coefficients(stehfest_n)
    times = np.logspace(-3, 3, num_samples)

    cdf_vals = _stehfest_invert(Psi_star_annulus, times, V,
                                eps=eps, tau0=tau0, tau1=tau1)

    # sort by cdf value to build the inverse CDF (cdf -> time) lookup
    order      = np.argsort(cdf_vals)
    cdf_sorted = np.clip(cdf_vals[order], 0, 1)
    t_sorted   = np.maximum(times[order], 0)

    # remove duplicate cdf values to ensure monotone interpolation
    cdf_unique, idx = np.unique(cdf_sorted, return_index=True)
    t_unique = np.asarray(t_sorted[idx])

    return t_unique, cdf_unique


def limited_matrix_diffusion_annulus(self, G):
    """ Matrix diffusion with finite cylindrical annular block geometry

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None

    Notes
    -----
        Samples diffusion return times from a finite cylindrical annular
        matrix block. The inner radius r0 is the absorbing fracture-matrix
        interface; the outer radius r1 is the reflecting block interior.
        A particle is released at r' = r0*(1 + eps), just inside the
        absorbing wall.

        The Laplace-domain solution uses modified Bessel functions I0, I1,
        K0, K1 from the cylindrical geometry, unlike the slab (Dentz) model
        which uses hyperbolic functions. Scaled scipy Bessel functions
        (ive, kve) are used with explicit exponential compensation factors
        to ensure numerical stability for all parameter values.

        tau1 = r1^2 / D is stored on the particle as self.tau_D and used
        to rescale dimensionless sampled return times to physical times [s].

        The inverse CDF table (self.transfer_time, self.trans_prob) must
        be precomputed via _make_inverse_cdf_annulus and attached to the
        particle before transport begins.

        All other parameters are attached to the particle class.
    """

    eps = 0.5
    b = G.edges[self.curr_node, self.next_node]['b']

    # trapping rate into the cylindrical matrix block
    gamma = (2 * self.matrix_porosity * self.matrix_diffusivity) / (b * eps * self.fracture_spacing)

    # average number of trapping events during this advective step
    average_number_of_trapping_events = self.delta_t * gamma

    # sample number of trapping events from Poisson distribution
    n = np.random.poisson(average_number_of_trapping_events)

    # sample uniform random variables and map to return times via inverse CDF
    # self.tau_D = r1^2 / D rescales dimensionless times to physical times
    xi  = np.random.uniform(size=n)
    tmp = self.tau_D * np.interp(xi, self.trans_prob, self.transfer_time)

    self.delta_t_md = tmp.sum()
