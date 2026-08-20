"""
.. module:: dentz.py
   :synopsis: Finite matrix diffusion in a slab geometry (Dentz model).
              Return times are sampled from the first-passage time CDF of
              diffusion in a finite slab, inverted from the Laplace domain
              with the Stehfest algorithm.
"""

import numpy as np

from pydfnworks.dfnGraph.transport.tdrw.stehfest import build_inverse_cdf_table
from pydfnworks.dfnGraph.transport.tdrw.trapping import poisson_trapping_diffusion_time

# Dimensionless release position next to the absorbing wall. The sampler's
# trapping rate and the inverse CDF table must use the same value.
RELEASE_EPS = 1e-4


def Psi_star(s, eps):
    """ Laplace transform of the slab CDF Psi*_eps(s)

    cosh((1-eps)*sqrt(s)) / (s * cosh(sqrt(s)))

    Scaled form to avoid cosh overflow at large s:
    cosh((1-eps)*q) / cosh(q) = exp(-eps*q) * (1 + exp(-2*(1-eps)*q)) / (1 + exp(-2*q))
    where q = sqrt(s). Both exp terms decay for large q so no overflow.
    """
    q = np.sqrt(s)
    num = np.exp(-eps * q) * (1.0 + np.exp(-2.0 * (1.0 - eps) * q))
    den = 1.0 + np.exp(-2.0 * q)
    return num / (den * s)


def Psi_pdf_star(s, eps):
    """ Laplace transform of the slab first-passage time PDF: psi*(s) = s * Psi*(s) """
    return Psi_star(s, eps) * s


def make_inverse_cdf(num_samples=100, eps=RELEASE_EPS, stehfest_n=16):
    """ Precompute the inverse CDF table for slab (Dentz) return-time sampling.

    Replaces the original mpmath.invertlaplace implementation with
    Stehfest inversion in double precision -- orders of magnitude faster.

    The scaled cosh formulation avoids overflow for all s values.
    t_min=1e-10 ensures Stehfest samples s >> 1/eps^2 for correct
    early-time behavior (eps=1e-4 requires s ~ 1e8, t ~ ln2/1e8 ~ 1e-9).

    Parameters
    ----------
        num_samples : int
            Number of points in the logspace time array. Default 100.

        eps : float
            Dimensionless release position. Default RELEASE_EPS.

        stehfest_n : int
            Number of Stehfest coefficients. Default 16.

    Returns
    -------
        (times, cdf_vals) : tuple of np.ndarray
            Inverse CDF lookup arrays for use with np.interp.
    """
    times = np.logspace(-10, 3, num_samples)
    return build_inverse_cdf_table(Psi_star, times, stehfest_n=stehfest_n, eps=eps)


def limited_matrix_diffusion_dentz(self, G):
    """ Matrix diffusion with a finite slab matrix block (Dentz model)

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None

    Notes
    -----
        All parameters are attached to the particle class.
        tau_D = fracture_spacing^2 / matrix_diffusivity rescales the
        dimensionless sampled return times to physical times [s].
    """
    self.delta_t_md = poisson_trapping_diffusion_time(self, G, RELEASE_EPS)
