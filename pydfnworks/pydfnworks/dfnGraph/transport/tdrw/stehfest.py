"""
.. module:: stehfest.py
   :synopsis: Gaver-Stehfest numerical Laplace inversion, shared by the
              finite matrix-diffusion TDRW models (dentz, annulus)
"""

import numpy as np
from math import factorial


def stehfest_coefficients(N=16):
    """ Compute Stehfest coefficients V_i for i = 1 ... N.

    Parameters
    ----------
        N : int
            Number of coefficients. Must be even. Default 16.

    Returns
    -------
        V : np.ndarray
            Array of N Stehfest coefficients.
    """
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


def stehfest_invert(F, t_arr, V, **kwargs):
    """ Invert the Laplace transform F at times t_arr using the Stehfest algorithm.

    f(t) ~ (ln2/t) * sum_i V_i * F(i*ln2/t)

    Parameters
    ----------
        F : callable
            Laplace-domain function F(s, **kwargs). Must accept a numpy array of s values.

        t_arr : np.ndarray
            Times at which to evaluate the inverse transform.

        V : np.ndarray
            Stehfest coefficients from stehfest_coefficients().

    Returns
    -------
        f : np.ndarray
            Approximate inverse transform evaluated at t_arr.
    """
    ln2 = np.log(2.0)
    f = np.zeros(len(t_arr))
    for idx, ti in enumerate(t_arr):
        s_vals = np.array([(i + 1) * ln2 / ti for i in range(len(V))])
        f[idx] = (ln2 / ti) * np.dot(V, F(s_vals, **kwargs))
    return f


def build_inverse_cdf_table(F_cdf, times, stehfest_n=16, **kwargs):
    """ Precompute an inverse CDF lookup table by Stehfest inversion of a
    Laplace-domain CDF.

    Parameters
    ----------
        F_cdf : callable
            Laplace transform of the CDF, F_cdf(s, **kwargs).

        times : np.ndarray
            Time points (typically logspaced) at which to invert the CDF.

        stehfest_n : int
            Number of Stehfest coefficients. Default 16.

    Returns
    -------
        t_unique : np.ndarray
            Return times, sorted by CDF value, for use with np.interp.

        cdf_unique : np.ndarray
            Strictly increasing cumulative probabilities in [0, 1]
            corresponding to t_unique.
    """
    V = stehfest_coefficients(stehfest_n)
    cdf_vals = stehfest_invert(F_cdf, times, V, **kwargs)

    # sort by cdf value to build the inverse CDF (cdf -> time) lookup
    order = np.argsort(cdf_vals)
    cdf_sorted = np.clip(cdf_vals[order], 0, 1)
    t_sorted = np.maximum(times[order], 0)

    # remove duplicate cdf values to ensure monotone interpolation
    cdf_unique, idx = np.unique(cdf_sorted, return_index=True)
    t_unique = np.asarray(t_sorted[idx])

    return t_unique, cdf_unique
