"""
.. module:: from_file.py
   :synopsis: Finite matrix diffusion with a user-supplied return-time CDF.
              The CDF table is read from a two-column ASCII file instead of
              being derived from an analytic block geometry.
"""

import numpy as np

from pydfnworks.general.logging import local_print_log
from pydfnworks.dfnGraph.transport.tdrw.trapping import poisson_trapping_diffusion_time

# Dimensionless release position next to the absorbing wall. The supplied CDF
# table must have been generated with the same release position (this matches
# the slab/Dentz convention, RELEASE_EPS in dentz.py).
RELEASE_EPS = 1e-4


def load_finite_time_cdf(tdrw_filename):
    """ Load a matrix-diffusion return-time CDF from file.

    Parameters
    ----------
        tdrw_filename : str
            Path to a two-column ASCII file. Column 1: dimensionless return
            times (rescaled by tau_D = (fracture_spacing/2)^2 / matrix_diffusivity
            during transport). Column 2: cumulative probabilities in [0, 1],
            strictly increasing.

    Returns
    -------
        finite_md_times : np.ndarray
            Return times for inverse CDF lookup.

        finite_md_cdf : np.ndarray
            Cumulative probabilities corresponding to finite_md_times.
    """
    data = np.genfromtxt(tdrw_filename)

    if data.ndim != 2 or data.shape[1] < 2:
        local_print_log(
            f"Error. File {tdrw_filename} does not contain at least two columns.",
            "error")

    finite_md_times = data[:, 0]
    finite_md_cdf = data[:, 1]

    return finite_md_times, finite_md_cdf


def limited_matrix_diffusion_from_file(self, G):
    """ Matrix diffusion with limited block size using a CDF read from file

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None

    Notes
    -----
        All parameters are attached to the particle class. The inverse CDF
        table (self.transfer_time, self.trans_prob) is loaded from file by
        load_finite_time_cdf during transport setup. Sampled times are
        rescaled by tau_D = (fracture_spacing/2)^2 / matrix_diffusivity.
    """
    eps = self.release_eps if self.release_eps is not None else RELEASE_EPS
    self.delta_t_md = poisson_trapping_diffusion_time(self, G, eps)
