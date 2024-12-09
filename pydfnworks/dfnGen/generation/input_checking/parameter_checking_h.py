import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf
import numpy as np
import scipy


def f(theta, t, a, b):
    """Differential Equation Angle Theta as a function of arc length, see Hyman et al. 2014, SIAM J. Sci. Comp. Equation 3.3"""
    return 1.0 / np.sqrt((a * np.sin(theta))**2 + (b * np.cos(theta)**2))


def compute_min_edge_length(aspect, min_radius, num_points):
    """ Check that the arc length of discretized fracture is greater than 3*h 
    
    Parameters
    ------------
        aspect : float
            aspect ratio of fracture family
        min_radius : float
            minimum radius of fracture family
        num_points : int
            number of points on fracture boundary

    Returns
    ----------
        min_edge : float
            Minimum edge length of discretized fracture

    Notes
    -------------
        None

    """
    # Major and Minor Axis of Ellipse
    r = min_radius

    ## TODO check > 3h
    a = aspect
    b = 1.0

    # approximation of total arclength
    c = np.pi * (a + b) * (1.0 + (3.0 * ((a - b) / (a + b))**2) /
                           (10. + np.sqrt(4. - 3. * ((a - b) / (a + b))**2)))

    #number of points
    n = num_points
    # expected arclength
    ds = c / n

    # array of steps
    steps = np.linspace(0, c, n + 1)
    # Numerically integrate arclength ODE
    theta = scipy.integrate.odeint(f, 0, steps, args=(a, b), rtol=10**-10)

    # Convert theta to x and y
    x = a * r * np.cos(theta)
    y = b * r * np.sin(theta)

    # Check Euclidean Distance between consecutive points
    min_edge = None
    for i in range(1, n):
        for j in range(i, n):
            if (i != j):
                edge_current = np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2)
                if min_edge is None:
                    min_edge = edge_current
                elif edge_current < min_edge:
                    min_edge = edge_current
    return min_edge


def check_shape(params, prefix):
    """ Check that the rectangles and ellipses generated will not involve features with length less than 3*h value used in FRAM. 

    
    Parameters
    -------------
        params : dict
            parameter dictionary
        prefix : string
            either 'e' or 'r' for ellipse or rectangle

    Returns
    ----------
        None

    Notes
    -------------
        Exits program is minimum edge is less than 3*h

    """

    shape = "ellipse" if prefix == 'e' else "rectangle"
    aspect_list = params[prefix + "aspect"]['value']
    num_points_list = None

    if shape == "ellipse":
        num_point_list = params['enumPoints']['value']

    ## counter for each distribution list as we check against discretized ellipses
    log_cnt = 0
    tpl_cnt = 0
    exp_cnt = 0
    const_cnt = 0
    cnt = 0
    exit_flag = False

    for cnt, distrib in enumerate(params[prefix + 'distr']['value']):
        if distrib == 1:
            min_radius = params[prefix + 'LogMin']['value'][log_cnt]
            log_cnt += 1

        elif distrib == 2:
            min_radius = params[prefix + 'min']['value'][tpl_cnt]
            tpl_cnt += 1

        elif distrib == 3:
            min_radius = params[prefix + 'ExpMin']['value'][exp_cnt]
            exp_cnt += 1

        elif distrib == 4:
            min_radius = params[prefix + 'const']['value'][const_cnt]
            const_cnt += 1

        if shape == "ellipse":
            hmin = compute_min_edge_length(aspect_list[cnt], min_radius,
                                           num_point_list[cnt])
        else:
            hmin = compute_min_edge_length(aspect_list[cnt], min_radius, 4)

        if hmin < (3 * params["h"]["value"]):
            exit_flag = True
            hf.print_warning(
                f"The {shape} family #{cnt+1} has defined a shape with features too small for meshing. Increase the aspect ratio or minimum radius so that no 2 points of the polygon create a line of length less than 3h"
            )
    if exit_flag:
        hf.print_error(
            "One or more fracture families have too small a edge sizes relative to h. See previous warnings for details."
        )


def check_h(params):
    """ Checks h values relative to domain size, minimum fracture size, and discretized edge lengths. 

    Parameters
    -------------
        params : dict
            parameter dictionary

    Returns
    ----------
        None

    Notes
    -------------
        Exits program is minimum edge is less than 3*h

    """

    hf.check_none('h', params['h']['value'])
    if params['h']['value'] == 0:
        hf.print_error("Value of \"h\" cannot be 0")

    # Determine minimum relative h size based on domain size
    x = params['domainSize']['value'][0]
    y = params['domainSize']['value'][1]
    z = params['domainSize']['value'][2]

    domain_cross_dist = np.sqrt(x**2 + y**2 + z**2)
    eps = 10**-5
    min_h = domain_cross_dist * eps

    ## if fram is on, ensure that it is a reasonable value
    if params['framOn']['value']:
        if params['h']['value'] < min_h:
            hf.print_error(
                f"Value of \"h\" is less than minimum for this domain size. Value provide: {params['h']['value']}. Minimum Value: {min_h}"
            )

        if params["minimum_fracture_size"]["value"] is not None:
            # Check against Minimum radius
            if params['h'][
                    'value'] > params["minimum_fracture_size"]["value"] / 10:
                hf.print_warning(
                    f"Provided value  of \"h\" ({params['h']['value']:0.2e}) is greater 1/10th the minimum fracture size ({params['minimum_fracture_size']['value']:0.2e}). The generated mesh will be very coarse and there will likely be a high rate of fracture rejection."
                )

            if params['h'][
                    'value'] < params["minimum_fracture_size"]["value"] / 1000:
                hf.print_warning(
                    f"Provided value  of  \"h\" ({params['h']['value']}) is smaller than 1/1000th than minimum fracture size ({params['minimum_fracture_size']['value']}). The generated mesh will be extremely fine and will likely be huge and costly to create. Computation will take a long time."
                )

    ## If FRAM is off, we just need to make sure the value won't crash the geneator
    else:
        if params['h']['value'] < min_h:
            hf.print_warning(
                f"Value of \"h\" is less than minimum for this domain size. Value provide: {params['h']['value']}. Minimum Value: {min_h}. Resetting to 10*minimum value"
            )
            params['h']['value'] = 10 * min_h

        if params["minimum_fracture_size"]["value"] is not None:
            # Check against Minimum radius
            if params['h'][
                    'value'] > params["minimum_fracture_size"]["value"] / 10:
                hf.print_warning(
                    f"Provided value  of \"h\" ({params['h']['value']}) is greater 1/10th the minimum fracture size ({params['minimum_fracture_size']['value']}). Resetting to 1/10 min fracture size"
                )
                params['h'][
                    'value'] = params["minimum_fracture_size"]["value"] / 10
