"""
.. module:: annulus.py
   :synopsis: Finite matrix diffusion in a cylindrical annulus geometry.
              Return times are sampled from the first-passage time CDF of
              diffusion in an annular block, inverted from the Laplace
              domain with the Stehfest algorithm.
"""

import numpy as np
from scipy.special import ive, kve, iv, kv

from pydfnworks.dfnGraph.transport.tdrw.stehfest import build_inverse_cdf_table
from pydfnworks.dfnGraph.transport.tdrw.trapping import poisson_trapping_diffusion_time

# Dimensionless release position (r' - r0)/r0 next to the absorbing inner
# wall, so the release point is r' = r0*(1 + eps). The sampler's trapping
# rate and the inverse CDF table must use the same value.
RELEASE_EPS = 1e-2


def Psi_star_annulus(s, eps, tau0, tau1):
    """ Laplace transform of the CDF for diffusion return time in a cylindrical annulus.

    Geometry: cylindrical annulus with inner radius r0 (absorbing, fracture-matrix
    interface) and outer radius r1 (reflecting, block interior).
    Particle released at r' = r0*(1+eps), just inside the absorbing wall.

    Parameters
    ----------
        s : np.ndarray
            Laplace variable values.

        eps : float
            (r' - r0) / r0, dimensionless release position.

        tau0 : float
            r0^2 / D, inner-radius diffusion timescale.

        tau1 : float
            r1^2 / D, outer-radius diffusion timescale.

    Notes
    -----
        Branch switch at |s*tau1| = 100, matching MATLAB cdfLaplace.m:
        small branch: unscaled iv/kv (safe for |s*tau1| <= 100);
        large branch: scaled ive/kve with exp prefactors (avoids overflow).

        ive(n,x) = exp(-x)*In(x)  ->  MATLAB besseli(n,x,1)
        kve(n,x) = exp(x) *Kn(x)  ->  MATLAB besselk(n,x,1)

        The branch switch is essential for correct small-t behavior.
        F_cdf(s) = F_psi(s) / s
    """
    q0 = np.sqrt(s * tau0)
    q0_eps = (1.0 + eps) * q0
    q1 = np.sqrt(s * tau1)

    large = s * tau1 > 100

    # large-argument branch
    I0e_eps = ive(0, q0_eps)
    K0e_eps = kve(0, q0_eps)
    I0e_0 = ive(0, q0)
    K0e_0 = kve(0, q0)
    I1e_1 = ive(1, q1)
    K1e_1 = kve(1, q1)

    exp1 = np.exp(np.clip((2 + eps) * q0 - 2 * q1, -500, 500))
    exp2 = np.exp(np.clip(-eps * q0, -500, 500))
    expd = np.exp(np.clip(2 * q0 - 2 * q1, -500, 500))

    num_large = exp1 * I0e_eps * K1e_1 + exp2 * K0e_eps * I1e_1
    den_large = expd * I0e_0 * K1e_1 + K0e_0 * I1e_1

    # small-argument branch
    # errstate suppresses overflow warnings from elements that will be
    # discarded by np.where (both branches are always evaluated)
    with np.errstate(invalid='ignore', over='ignore'):
        num_small = iv(0, q0_eps) * kv(1, q1) + kv(0, q0_eps) * iv(1, q1)
        den_small = iv(0, q0) * kv(1, q1) + kv(0, q0) * iv(1, q1)

    num = np.where(large, num_large, num_small)
    den = np.where(large, den_large, den_small)

    return num / (den * s)


def Psi_pdf_star_annulus(s, eps, tau0, tau1):
    """ Laplace transform of the first-passage time PDF: psi*(s) = s * F_cdf(s) """
    return Psi_star_annulus(s, eps, tau0, tau1) * s


def make_inverse_cdf(num_samples=100, eps=RELEASE_EPS, tau0_ratio=1e-7,
                     stehfest_n=16):
    """ Precompute the inverse CDF table for cylindrical annulus return-time sampling.

    The table is built in dimensionless time units of tau1 = r1^2/D (tau1 = 1
    in the Laplace-domain solution), so sampled values are rescaled to
    physical times by multiplying with the particle's tau_D = r1^2/D.

    Parameters
    ----------
        num_samples : int
            Number of points in the logspace time array. Default 100.

        eps : float
            Dimensionless release position (r'-r0)/r0. Default RELEASE_EPS.

        tau0_ratio : float
            Geometry ratio tau0/tau1 = (r0/r1)^2 with r0 the fracture-matrix
            interface radius (half the aperture) and r1 the outer block
            radius (half the fracture spacing).

        stehfest_n : int
            Number of Stehfest coefficients. Default 16.

    Notes
    -----
        The time range starts well below eps^2 * tau0_ratio so Stehfest
        samples large enough s for correct early-time behavior
        (requires s >> (1/eps)^2 / tau0).

    Returns
    -------
        (times, cdf_vals) : tuple of np.ndarray
            Inverse CDF lookup arrays (times in units of tau1) for use
            with np.interp.
    """
    t_lo = max(1e-16, 0.01 * eps**2 * tau0_ratio)
    times = np.logspace(np.log10(t_lo), 1, num_samples)
    return build_inverse_cdf_table(Psi_star_annulus, times, stehfest_n=stehfest_n,
                                   eps=eps, tau0=tau0_ratio, tau1=1.0)


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
        K0, K1. Two numerical branches are used matching MATLAB cdfLaplace.m:
        unscaled Bessels for |s*tau1| <= 100, and scaled Bessels (ive, kve)
        with explicit exponential prefactors for |s*tau1| > 100.

        tau1 = r1^2 / D is stored on the particle as self.tau_D and used
        to rescale dimensionless sampled return times to physical times [s].

        The inverse CDF table (self.transfer_time, self.trans_prob) must
        be precomputed via make_inverse_cdf and attached to the particle
        before transport begins.

        All other parameters are attached to the particle class.
    """
    eps = self.release_eps if self.release_eps is not None else RELEASE_EPS
    self.delta_t_md = poisson_trapping_diffusion_time(self, G, eps)
