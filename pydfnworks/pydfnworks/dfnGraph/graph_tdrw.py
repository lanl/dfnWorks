from re import I
from threading import TIMEOUT_MAX
import numpy as np
from scipy import special
import mpmath as mp


def get_fracture_segments(transfer_time,
                          fracture_length,
                          b,
                          velocity,
                          fracture_spacing,
                          matrix_diffusivity,
                          matrix_porosity,
                          plim=0.01):
    """

    This function calculates the maximum segment length that can be used in the TDRW model, following the protocol proposed by Roubinet et al., 2010.
    
    Note that Roubinet said that a plim value of 0.1 was acceptable. However, we are better able to match the results of Sudicky across parameter values when plim = 0.01. 

    Parameters
    ---------------------

    Returns
    ---------------------

    Notes
    ---------------------

    """

    segment_length = ((b * np.sqrt(transfer_time)) /
                      (matrix_porosity * np.sqrt(matrix_diffusivity))
                      ) * special.erfcinv(1.0 - plim) * velocity
    if segment_length >= fracture_length:
        return fracture_length, 1
    else:
        num_segments = int(np.ceil(fracture_length / segment_length))
        return segment_length, num_segments


def t_diff_unlimited(a, tf, xi):
    '''
    This function returns randomly drawn diffusion times, assuming an unlimited matrix.
    
    Parameters
    -------------------
        a : double
         Constant parameter describing retention in the matrix. a = (matrix_porosity*matrix_diffusion)/aperture_length
        tf : double
            Advective travel time
        xi : float
            value between [0,1)
   
    Returns
    --------------
        t_diff : float
            Total time diffusing the matrix
            
    Notescx
    -------------
        For a random sample, sample xi from U[0,1). 
        
    '''
    return ((a * tf) / special.erfcinv(xi))**2


def transition_probability_cdf(t_min, t_max, frac_spacing, matrix_diffusivity,
                               num_pts):
    '''
    This function calculates the probability that a particle changes fractures, given the time needed to reach
    penetration depth (tstar). It can return the transfer probability for a single tstar (when num_pts == 1) or
    for a collection.
    
    When calculating transfer probabilities for a collection of points, we break up times using two vectors, t1 and
    t2. t1 ensures that we get proper point definition over our primary range of interest so that we can accurately
    produce our transfer probability distribution. The vector t2 contains extra points that are used in case the values
    in t1 were not sufficiently high to plateau.
    
    Negative probabilities can sometimes appear due to numerical instabilities in our laplace inverse transform.

    We remove these negative values. Moreover, we ensure that our final distribution is monotonically 
    '''
    print("--> Building transition probability cdf")

    times = np.logspace(np.log10(t_min), np.log10(t_max), num=num_pts)
    prob_cdf = np.zeros(num_pts)

    ## Parameters for Roubinet function for the transfer probability function described
    ## in Roubinet et al. WRR 2010. Equation number 5.
    l1 = frac_spacing / 2
    l2 = -l1
    delta_l = l1 - l2

    ## Roubinet et al. WRR 2010. Equation number 5.
    ## s is the Laplace variable
    laplace_trans_prob_function = lambda s: (mp.exp(l1*mp.sqrt(s/matrix_diffusivity))/s) \
            *((1.0 - mp.exp(-2*l2*mp.sqrt(s/matrix_diffusivity)))/(1.0 - mp.exp(2.0 *(delta_l)*mp.sqrt(s/matrix_diffusivity))))

    for i, t in enumerate(times):
        prob_cdf[i] = mp.invertlaplace(laplace_trans_prob_function,
                                       t,
                                       method='talbot',
                                       dps=16,
                                       degree=36)

        if prob_cdf[i] >= 0.5:
            break

    # print(times, prob_cdf)
    # # CLEAN UP the solution.
    # # Sometime small negative values will appear due to numerical instabilities. Remove these.
    ind = np.asarray(np.where(prob_cdf >= 0)).flatten()
    prob_cdf = prob_cdf[ind]
    times = times[ind]

    # # Monotonically increasing
    prob_cdf = np.maximum.accumulate(prob_cdf)
    # unique values
    prob_cdf, ind = np.unique(prob_cdf, return_index=True)
    times = times[ind]

    return times, prob_cdf


def transfer_probabilities(b_min,
                           b_max,
                           tf_min,
                           tf_max,
                           matrix_porosity,
                           matrix_diffusivity,
                           frac_spacing,
                           eps=1e-16,
                           num_pts=100):
    """ Returns the CDF of transfer probabilities and assocaited times. 
    Lower and upper bounds are first estimated using the physical parameters of the system.
    The bounds are then tighted based on the returned probabilities wherein we find a range with 
    probabilities greater than eps, and  
    """
    # estimate lower bound
    # get the minimum factor
    a_min = (matrix_porosity * np.sqrt(matrix_diffusivity)) / b_max
    # sample at the lowest value of tf, with sample ~ 0
    t_diff_lb = t_diff_unlimited(a_min, tf_min, eps)
    # Below this value the inversse laplace transform does not convergence
    if t_diff_lb < 1e-12:
        print(f"lb too low {t_diff_lb:0.2e} changing to 1e-12")
        t_diff_lb = 1e-12

    # estimate upper bound
    # get the maximum factor
    a_max = (matrix_porosity * np.sqrt(matrix_diffusivity)) / b_min
    # sample at the largest value of tf, with sample ~ 1
    t_diff_ub = t_diff_unlimited(a_max, tf_max, 1 - eps)
    # if t_diff_ub > 1e30:
    #     print(f"ub too high {t_diff_ub} changing to 1e30")
    #     t_diff_ub = 1e30

    print(
        f"--> Initial bounds for diffusion times. Min: {t_diff_lb:0.2e}, Max: {t_diff_ub:0.2e}"
    )

    # Compute the transition probabilities across the whole range of times.
    times, trans_cdf = transition_probability_cdf(t_diff_lb, t_diff_ub,
                                                  frac_spacing,
                                                  matrix_diffusivity, num_pts)

    # Restricts the
    # We end up with a lot of values we don't need, close to 0 probability.
    # walk through the CDF and find the time corresponding to the
    # first probability greater than epsilon
    for i, val in enumerate(trans_cdf):
        if val > eps:
            t_diff_lb = times[i]
            break

    # Likewise we end up with a lot of values we don't need, close to 0.5 probability.
    # walk through the CDF and find the time corresponding to the
    # first probability greater than 0.5 - epsilon

    for i, val in reversed(list(enumerate(trans_cdf))):
        if val <= 0.5:
            t_diff_ub = times[i]
            break

    print(
        f"--> Final bounds for diffusion times. Min: {t_diff_lb:0.2e}, Max: {t_diff_ub:0.2e}"
    )

    # Recompute the transition probabilities across the restricted range of times.
    times, trans_cdf = transition_probability_cdf(t_diff_lb, t_diff_ub,
                                                  frac_spacing,
                                                  matrix_diffusivity, num_pts)

    #convert to as dictionary
    trans_prob = {"times": times, "cdf": trans_cdf}
    # print(times)
    # print(trans_cdf)
    return trans_prob


def segment_matrix_diffusion(trans_prob, matrix_porosity, matrix_diffusivity,
                             b, segment_length, velocity, num_segments):

    a = (matrix_porosity * np.sqrt(matrix_diffusivity)) / b

    segment_time = segment_length / velocity
    prob_min = min(trans_prob['cdf'])
    prob_max = max(trans_prob['cdf'])
    t_diff = 0
    for i in range(num_segments):
        xi = np.random.uniform(low=0, high=1)
        t_diff_seg = t_diff_unlimited(a, segment_time, xi)

        if t_diff_seg < trans_prob['times'][0]:
            limited_probability = 0

        elif t_diff_seg > trans_prob['times'][-1]:
            limited_probability = 1

        else:
            limited_probability = 2 * np.interp(
                t_diff_seg / 2, trans_prob['times'], trans_prob['cdf'])

        if limited_probability > 0:
            # Draw a random number from U[0,1] for each particle.
            # Particles transfer to a new fracture if this random number
            # is less than the transfer probability
            xi = np.random.uniform(low=0, high=1)
            if xi < limited_probability:
                xi = np.random.uniform(low=prob_min, high=prob_max)
                t_diff_seg = np.interp(xi, trans_prob['cdf'],
                                       trans_prob['times'])

        t_diff += t_diff_seg
    return t_diff


def get_aperture_and_time_limits(G):
    """ Walks through edges on the graph and returns min and max of aperture and advective travel times 
    
    Parameters
    ---------------------
        G : networkX graph  
            Graph provided by graph_flow modules


    Returns
    -------------
        b_min : float
            Minimum value of aperture on the network
        b_max : float
            Maximmum value of aperture on the network
        t_min : float
            Minimum value of advective travel time on the network
        t_max : float
            Maximmum value of advective travel time on the network

    Notes
    --------------------
        Could be improved with nx.get_edge_attributes, maybe. JDH


    """
    # get b_min, b_max, t_min, t_max
    print("--> Getting b and t limits")
    b_min = None
    b_max = None
    t_min = None
    t_max = None
    for u, v, d in G.edges(data=True):
        # print(u,v,d)
        if u != 's' and u != 't' and v != 's' and v != 't':
            if b_min is None:
                b_min = d['b']
            elif d['b'] < b_min:
                b_min = d['b']

            if b_max is None:
                b_max = d['b']
            elif d['b'] > b_max:
                b_max = d['b']

            if t_min is None:
                t_min = d['time']
            elif d['time'] < t_min:
                t_min = d['time']

            if t_max is None:
                t_max = d['time']
            elif d['time'] > t_max:
                t_max = d['time']
            # if d['time'] > 1e16:
            #     print(u,v,d)

    print(f"--> b-min: {b_min:0.2e}, b-max: {b_max:0.2e}")
    print(f"--> t-min: {t_min:0.2e}, t-max: {t_max:0.2e}")
    return b_min, b_max, t_min, t_max


def set_up_limited_matrix_diffusion(G,
                                    frac_spacing,
                                    matrix_porosity,
                                    matrix_diffusivity,
                                    eps=1e-16,
                                    num_pts=100):
    """ Sets up transition probabilities for limited block size matrix diffusion
    
    Parameters
    ---------------------



    Returns
    -------------


    Notes
    --------------------



    """

    b_min, b_max, tf_min, tf_max = get_aperture_and_time_limits(G)
    trans_prob = transfer_probabilities(b_min, b_max, tf_min, tf_max,
                                        matrix_porosity, matrix_diffusivity,
                                        frac_spacing, eps, num_pts)
    return trans_prob


# def check_unlimited_conditions(frac_length, velocity, matrix_diffusivity, matrix_porosity, b, fracture_spacing):
#     """
#     Pretty sure this is wrorng...
#     """

#     peclet_number = ( frac_length* velocity ) / matrix_diffusivity
#     xi = np.random.uniform(size=1, low=0, high=1)[0]
#     limited_conditions = (matrix_porosity * frac_length)/(np.sqrt(2) * xi * 0.5*b * fracture_spacing)

#     if peclet_number > limited_conditions:
#         return True
#     else:
#         return False


def limited_matrix_diffusion(self, G):

    #print("--> running limited matrix diffusion")
    frac_length = G.edges[self.curr_node, self.next_node]['length']
    b = G.edges[self.curr_node, self.next_node]['b']
    velocity = G.edges[self.curr_node, self.next_node]['velocity']
    # print(frac_length, b, velocity, self.fracture_spacing, self.matrix_diffusivity, self.matrix_porosity)

    # if check_unlimited_conditions(frac_length, velocity, self.matrix_diffusivity, self. matrix_porosity, b, self.fracture_spacing):
    #     # print("--> unlimited conditions")
    #     self.unlimited_matrix_diffusion(G)
    # else:
    # print("--> limited conditions")
    segment_length, num_segments = get_fracture_segments(
        self.transfer_time, frac_length, b, velocity, self.fracture_spacing,
        self.matrix_diffusivity, self.matrix_porosity)
    # print(f"fracture length {frac_length}")
    # print(f"segment length {segment_length}")
    # print(f"num segments {num_segments}")
    self.delta_t_md = segment_matrix_diffusion(self.trans_prob,
                                               self.matrix_porosity,
                                               self.matrix_diffusivity, b,
                                               segment_length, velocity,
                                               num_segments)


def unlimited_matrix_diffusion(self, G):
    """ Matrix diffusion part of particle transport

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None
    """

    b = G.edges[self.curr_node, self.next_node]['b']
    a_nondim = self.matrix_porosity * np.sqrt(self.matrix_diffusivity) / b
    xi = np.random.uniform(size=1, low=0, high=1)[0]
    self.delta_t_md = ((a_nondim * self.delta_t / special.erfcinv(xi))**2)
