"""
.. module:: trapping.py
   :synopsis: Shared Poisson trapping-event sampler used by the finite
              matrix-diffusion TDRW models (dentz, annulus, from_file)
"""

import numpy as np


def poisson_trapping_diffusion_time(particle, G, eps):
    """ Sample the total matrix-diffusion time accrued during one advective
    step using the Poisson trapping-event model.

    The number of trapping events over the step is Poisson-distributed with
    rate gamma * delta_t, where gamma is the trapping rate into the matrix.
    Each event's return time is drawn from the model's precomputed inverse
    CDF table (particle.transfer_time / particle.trans_prob) and rescaled
    from dimensionless to physical time by particle.tau_D.

    Parameters
    ----------
        particle : Particle
            Particle object. Uses matrix_porosity, matrix_diffusivity,
            fracture_spacing, delta_t, tau_D, trans_prob, transfer_time.

        G : NetworkX graph
            graph obtained from graph_flow

        eps : float
            Dimensionless release position of the particle next to the
            absorbing fracture-matrix interface. Must match the eps used
            to build the inverse CDF table.

    Returns
    -------
        delta_t_md : float
            Total matrix diffusion time for this advective step [s].
    """
    b = G.edges[particle.curr_node, particle.next_node]['b']

    # trapping rate into the matrix block
    gamma = (2 * particle.matrix_porosity * particle.matrix_diffusivity) / (
        b * eps * particle.fracture_spacing)

    # average number of trapping events during this advective step
    average_number_of_trapping_events = particle.delta_t * gamma

    # sample number of trapping events from Poisson distribution
    n = np.random.poisson(average_number_of_trapping_events)

    # sample uniform random variables and map to return times via inverse CDF
    xi = np.random.uniform(size=n)
    return_times = particle.tau_D * np.interp(xi, particle.trans_prob,
                                              particle.transfer_time)

    return return_times.sum()
