import mpmath as mp
import numpy as np
from scipy import special
import matplotlib.pyplot as plt


def create_ecdf(vals, weights=None):
    """  create ecdf of vals 

    Parameters
    ----------
        vals : array
           array of values to be binned
        weights :array
            weights corresponding to vals to be used to create a weighted pdf

    Returns
    -------
        x : array
            x values of the cdf
        cdf : array
            values of the cdf, normalized so cummulative sum = 1
    """
    index_sort = np.argsort(vals)
    x = vals[index_sort]
    if weights is None:
        weights = np.ones(len(vals))
    cdf = weights[index_sort]
    cdf = np.cumsum(cdf)/cdf.sum()
    return(x, cdf)


def sudicky_solution(params, t_min, t_max, num_pts = 100):

    print("--> Sudicky Solution")
    times = np.logspace(np.log10(t_min), np.log10(t_max), num = num_pts)
    solution = np.zeros(num_pts)
    c0 = 1
    w = (params["porosity"]*np.sqrt(params["mdiff"])*params["frac_length"])/((params["b"]/2)*params["velocity"])
    G = np.sqrt(1 / params["mdiff"])
    B = params["frac_spacing"]/2
    sig = G*(B - 0.5*params["b"])
    v = params["velocity"]
    z = params["frac_length"]

    sudicky_laplace = lambda s: ((c0**2)/s)*mp.exp(-(s*z)/v)*mp.exp(-w*mp.sqrt(s)*mp.tanh(sig*mp.sqrt(s)))

    for i,t in enumerate(times): 
        solution[i] = mp.invertlaplace(sudicky_laplace, t, method='deHoog', dps = 10, degree = 18)
    print("--> done")
    return times, solution 


def get_fracture_segments(fracture_length, b, velocity, fracture_spacing, mdiff, phi, plim=0.01):
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

    transfer_time = fracture_spacing**2 / (2 * mdiff)  # mean transfer time
    print(f"transfer_time; {transfer_time} ")
    segment_length = ((b * np.sqrt(transfer_time)) / (phi * np.sqrt(mdiff) )) * special.erfcinv(1.0 - plim) * velocity

    print(f"maximum segment length {segment_length}")
    if segment_length >= fracture_length:
        return fracture_length, 1
    else:
        num_segments = int(np.ceil(fracture_length/segment_length))
        # Get the first decimal place in our max_length solution
        # decimal = np.ceil(np.log10(np.ceil(1 / max_length)))
        # factor = 10**decimal
        # segment_length = np.floor(max_length * factor) / factor
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


def transition_probability_cdf(t_min, t_max, params, num_pts):
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
    l1 = params["frac_spacing"]/2
    l2 = -l1
    delta_l = l1 - l2

    ## Roubinet et al. WRR 2010. Equation number 5.
    ## s is the Laplace variable
    laplace_trans_prob_function = lambda s: (mp.exp(l1*mp.sqrt(s/params["mdiff"]))/s) \
            *((1.0 - mp.exp(-2*l2*mp.sqrt(s/params["mdiff"])))/(1.0 - mp.exp(2.0 *(delta_l)*mp.sqrt(s/params["mdiff"]))))

    for i, t in enumerate(times):
        prob_cdf[i] = mp.invertlaplace(laplace_trans_prob_function,
                                       t,
                                       method='talbot',
                                       dps = 16, degree = 36)

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


def transfer_probabilities(params,
                           b_min,
                           b_max,
                           tf_min,
                           tf_max,
                           eps=1e-16,
                           num_pts=100):
    """ Returns the CDF of transfer probabilities and assocaited times. 
    Lower and upper bounds are first estimated using the physical parameters of the system.
    The bounds are then tighted based on the returned probabilities wherein we find a range with 
    probabilities greater than eps, and  
    """
    # estimate lower bound
    # get the minimum factor
    a_min = (params["porosity"] * np.sqrt(params["mdiff"])) / b_max
    # sample at the lowest value of tf, with sample ~ 0
    t_diff_lb = t_diff_unlimited(a_min, tf_min, eps)
    # Below this value the inversse laplace transform does not convergence
    if t_diff_lb < 1e-12:
        print(f"lb too low {t_diff_lb:0.2e} changing to 1e-12")
        t_diff_lb = 1e-12

    # estimate upper bound
    # get the maximum factor
    a_max = (params["porosity"] * np.sqrt(params["mdiff"])) / b_min
    # sample at the largest value of tf, with sample ~ 1
    t_diff_ub = t_diff_unlimited(a_max, tf_max, 1 - eps)
    # if t_diff_ub > 1e30:
    #     print(f"ub too high {t_diff_ub} changing to 1e30")
    #     t_diff_ub = 1e30

    print(f"Initial bounds. Min: {t_diff_lb:0.2e}, Max: {t_diff_ub:0.2e}")

    # Compute the transition probabilities across the whole range of times.
    times, trans_cdf = transition_probability_cdf(t_diff_lb, t_diff_ub, params,
                                                  num_pts)

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

    print(f"Final bounds. Min: {t_diff_lb:0.2e}, Max: {t_diff_ub:0.2e}")

    # Recompute the transition probabilities across the restricted range of times.
    times, trans_cdf = transition_probability_cdf(t_diff_lb, t_diff_ub, params,
                                                  num_pts)

    #convert to as dictionary
    trans_prob = {"times": times, "cdf": trans_cdf}
    # print(times)
    # print(trans_cdf)
    return trans_prob

def single_particle(trans_prob, fracture_params):

    global quiet
    prob_min = min( trans_prob['cdf'])
    prob_max = max( trans_prob['cdf']) 
    t_diff = 0
    for i in range(fracture_params["num_segments"]):
        xi = np.random.uniform(low = 0, high = 1)
        t_diff_seg = t_diff_unlimited(fracture_params['a'], fracture_params["segment_time"], xi) 

        # this is where things are going wrong.
        if not quiet: print('unlimited diffussion time ', t_diff_seg)

        if t_diff_seg < trans_prob['times'][0]:
            if not quiet: print("too low diffusion time")
            if not quiet: print("Transition does not occur")
            limited_probability = 0

        elif t_diff_seg > trans_prob['times'][-1]: 
            if not quiet: print("too high diffusion time")
            if not quiet: print("Transition occurs")
            limited_probability = 1

        else: 
            limited_probability = 2*np.interp(t_diff_seg/2, trans_prob['times'], trans_prob['cdf'])

        if limited_probability > 0:
            if not quiet: print("--> Checking for transition")
            if not quiet: print(f"Transition probability {limited_probability}")
            # Draw a random number from U[0,1] for each particle. 
            # Particles transfer to a new fracture if this random number
            # is less than the transfer probability
            xi = np.random.uniform(low = 0, high = 1)
            if xi < limited_probability:
                xi = np.random.uniform(low = prob_min, high = prob_max)
                t_diff_seg  = np.interp(xi, trans_prob['cdf'], trans_prob['times'])
                if not quiet: print("--> Transition occurs")
                # print("--> Transition occurs")
            else:
                if not quiet: print("--> Transition did not occur")

        t_diff += t_diff_seg
    total_time = t_diff + fracture_params['advect_time']
    return t_diff, total_time 

## main 
global quiet
quiet = True 

fracture_params = {
    "b" : 1e-4,
    "frac_length": 100,
    "velocity" : 1e-3,
}
params = {
    "frac_spacing": 1,  # Fracture spacing
    "porosity": 0.15,  # Matrix porosity
    "mdiff": 1e-8,  # Matrix diffusivity
}

params.update(fracture_params)

fracture_params["a"] = (params["porosity"] * np.sqrt(params["mdiff"])) / fracture_params['b']
fracture_params["advect_time"] = fracture_params["frac_length"]/fracture_params["velocity"]
fracture_params["segment_length"], fracture_params["num_segments"] = num_segs  = get_fracture_segments(fracture_params["frac_length"], 
    fracture_params["b"], fracture_params["velocity"], params["frac_spacing"]/2, 
    params['mdiff'], params['porosity'])
fracture_params["segment_time"] =  fracture_params["segment_length"]/fracture_params["velocity"]


b_min = 0.5*fracture_params["b"]  # minimum aperture in the network
b_max = 2*fracture_params["b"]  # maximum aperture in the network
tf_min = 0.5*fracture_params["advect_time"]  # minimum travel time
tf_max = 2*fracture_params["advect_time"] # maximum travel time
print(tf_min, tf_max) 

params.update(fracture_params)

for key in params.keys():
    print(key, params[key])

trans_prob = transfer_probabilities(params, b_min, b_max, tf_min, tf_max)
print(min(trans_prob['cdf']), max(trans_prob['cdf']))

# t_diff, total_time = single_particle(trans_prob, fracture_params)
# print(f"Advective time {fracture_params['advect_time']}")
# print(f"Diffusion time {t_diff}")
# print(f"Total time {total_time}")

print("--> running particles ")
num_particles = int(1e4)
total_times = np.zeros(num_particles)
for i in range(num_particles):
    # print(f"\nParticle {i+1}")
    _,total_times[i] = single_particle(trans_prob, fracture_params)
print("--> done")

times, solution = sudicky_solution(params, 1e-1*min(total_times), 1e1*max(total_times)) 
fig,ax = plt.subplots()
ax.semilogx(times, solution, '--', linewidth = 1,  label = 'Sudicky')
x,y = create_ecdf(total_times)
ax.semilogx(x,y, ':', linewidth = 1,  label = 'tdrw')
ax.legend()
plt.axis([10**6, 10**10, 0, 1.1])
plt.savefig("compare.png", dpi = 300)
plt.close()
