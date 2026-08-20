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

# Default (maximum) dimensionless release position next to the absorbing
# wall. The sampler's trapping rate and the inverse CDF table must use the
# same value. The TDRW approximation is only valid for retardation times
# well beyond the artifact scale (eps * B)^2 / D_m (the shortest matrix
# excursion the discretization can represent), so eps is reduced below this
# value when the block half-width B is large -- see choose_release_eps().
RELEASE_EPS = 1e-4

# Smallest eps the adaptive rule may select. Trapping events per particle
# scale as 1/eps, so this floor bounds the cost of a single run.
MIN_RELEASE_EPS = 1e-8

# The artifact scale (eps * B)^2 / D_m is kept below this fraction of the
# characteristic advective time.
ARTIFACT_TIME_FRACTION = 1e-3


def choose_release_eps(t_char, half_width, matrix_diffusivity):
    """ Choose the release position eps for the slab (Dentz) model.

    The model reproduces the continuum solution only for retardation times
    t >> (eps * B)^2 / D_m. This picks eps so that artifact scale is at
    most ARTIFACT_TIME_FRACTION of the characteristic advective time
    t_char, capped at RELEASE_EPS (small blocks keep the default) and
    floored at MIN_RELEASE_EPS (cost control; a warning is in order if the
    floor binds).

    Parameters
    ----------
        t_char : float
            Characteristic advective time of the network [s], e.g. the
            shortest-path travel time from inlet to outlet.

        half_width : float
            Matrix block half-width B = fracture_spacing / 2 [m].

        matrix_diffusivity : float
            Matrix diffusivity [m^2/s].

    Returns
    -------
        eps : float
            Release position for the table and the trapping rate.
    """
    eps = np.sqrt(
        ARTIFACT_TIME_FRACTION * matrix_diffusivity * t_char) / half_width
    return float(min(RELEASE_EPS, max(MIN_RELEASE_EPS, eps)))


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
    The lower end of the time range scales with eps: Stehfest must sample
    s >> 1/eps^2 for correct early-time behavior, so t_min << eps^2 in the
    dimensionless units of tau_D.

    Parameters
    ----------
        num_samples : int
            Minimum number of points in the logspace time array. Default
            100. The actual count grows with the eps-dependent time range
            so the density stays at >= 8 points per decade.

        eps : float
            Dimensionless release position. Default RELEASE_EPS.

        stehfest_n : int
            Number of Stehfest coefficients. Default 16.

    Returns
    -------
        (times, cdf_vals) : tuple of np.ndarray
            Inverse CDF lookup arrays for use with np.interp.
    """
    t_lo = min(1e-10, 0.01 * eps**2)
    decades = np.log10(1e3) - np.log10(t_lo)
    num_samples = max(num_samples, int(8 * decades))
    times = np.logspace(np.log10(t_lo), 3, num_samples)
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
        tau_D = (fracture_spacing/2)^2 / matrix_diffusivity rescales the
        dimensionless sampled return times to physical times [s].
    """
    eps = self.release_eps if self.release_eps is not None else RELEASE_EPS
    self.delta_t_md = poisson_trapping_diffusion_time(self, G, eps)
