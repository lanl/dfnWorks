import numpy as np
import sys

def get_units(variable):
    """
    Returns a string of appropriate units for different variable

    Parameters
    -----------
        variable : string
            name of variable. Acceptable values are aperture, permeability, and transmissivity
    Returns
    ----------
        units : string
            appropriate units for provided variable
    """

    if variable == "aperture":
        units = "m"
    elif variable == "permeability":
        units = "m^2"
    elif variable == "transmissivity":
        units = "m^2/s"
    else:
        error = "ERROR!!! The variable of choice '{0}' is not known in the function get_units()\nAcceptable names are aperture, permeability, and transmissivity\nExiting.".format(
            variable)
        sys.stderr.write(error)
        sys.exit(1)
    return units


def check_key(dict, key):
    ''' 
    Checks if key is in dict

    Parameters
    -----------
        dict : dictionary
        key : string
    Returns
    ----------
        bool : bool
            True if key is in dictionary, False if not

    '''

    if key in dict.keys():
        return True
    else:
        return False


def load_fractures(filename,quiet):
    ''' 
    Loads fracture information from filename. 

    Parameters
    -----------
        filename : string
            name of fracture radii file
    Returns
    ----------
        r : array of doubles
            maximum radii of fractures

        family_id : array of ints
            family id for each fractures
        n : int
            number of fractures in the domain 

    '''
    if not quiet:
        print("--> Loading Fracture information from {0}".format(filename))

    data = np.genfromtxt(filename, skip_header=2)
    family_id = (data[:, 2]).astype(int)
    n, _ = np.shape(data)
    r = np.zeros(n)
    for i in range(n):
        if data[i, 0] >= data[i, 1]:
            r[i] = data[i, 0]
        else:
            r[i] = data[i, 1]
    return r, family_id, n


def convert(x, source, target):
    ''' 
    converts between variables aperture, permeability, and transmissivity

    Parameters
    -----------
        x : numpy array
            input values
        source : string
            variable name of source
        target : string
            variable name of output 
    Returns
    ----------
        y : numpy array
            array of converted values
    '''

    mu = 8.9e-4  #dynamic viscosity of water at 20 degrees C, Pa*s
    g = 9.8  #gravity acceleration
    rho = 997  # water density

    if source == "aperture" and target == "permeability":
        perm = (x**2) / 12
        return perm
    if source == "aperture" and target == "transmissivity":
        T = (x**3 * rho * g) / (12 * mu)
        return T
    if source == "permeability" and target == "aperture":
        b = np.sqrt((12.0 * x))
        return b

    if source == "permeability" and target == "transmissivity":
        b = np.sqrt((12.0 * x))
        T = (b * x * rho * g) / (12 * mu)
        return T

    if source == "transmissivity" and target == "aperture":
        b = ((x * 12 * mu) / (rho * g))**(1 / 3)
        return b
    if source == "transmissivity" and target == "permeability":
        b = ((x * 12 * mu) / (rho * g))**(1 / 3)
        perm = (b**2) / 12
        return perm
    else:
        error = "ERROR!!! Unknown names is convert. Either '{0}' or '{1}' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n".format(
            source, target)
        sys.stderr.write(error)
        sys.exit(1)


def log_normal(params, variable,number_of_fractures):
    """ Creates Fracture Based Log-Normal values that is number_of_fractures long.
    The values has a mean mu and log-variance sigma. 
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the Log Normal values. Must contain keys mu and sigma. 
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        number_of_fractures : int
            number of fractures in the DFN 
    Returns
    ----------
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values

    Notes
    ----------
        values are generated for the variable provided. The two remaining variables are derived using those values
    """
    print('--> Creating uncorrelated lognormal {0} values.'.format(variable))
    units = get_units(variable)
    print("--> Mean: {0} {1}".format(params["mu"], units))
    print("--> Log Variance: {0}".format(params["sigma"]))

    if variable == "aperture":
        b = np.log(params["mu"]) * np.ones(number_of_fractures)
        perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
        b = np.exp(b + np.sqrt(params["sigma"]) * perturbation)

        perm = convert(b, variable, "permeability")
        T = convert(b, variable, "transmissivity")

    elif variable == "permeability":
        perm = np.log(params["mu"]) * np.ones(number_of_fractures)
        perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
        perm = np.exp(perm + np.sqrt(params["sigma"]) * perturbation)

        b = convert(perm, variable, "aperture")
        T = convert(perm, variable, "transmissivity")

    elif variable == "transmissivity":
        T = np.log(params["mu"]) * np.ones(number_of_fractures)
        perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
        T = np.exp(T + np.sqrt(params["sigma"]) * perturbation)

        b = convert(T, variable, "aperture")
        perm = convert(T, variable, "permeability")

    else:
        error = "ERROR!!! The variable of choice '{0}'' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n".format(
            variable)
        sys.stderr.write(error)
        sys.exit(1)
    print('--> Complete\n')
    return b, perm, T


def correlated(params, variable, radii):
    """ Creates hydraulic properties of fractures based on power-law relationship with 
    fracture radius. For example, T = alpha*r^beta
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the power-law relationship. Must contain alpha and beta. 
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        radii : array
            array of fracture radii in the domain

    Returns
    ----------
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values
    """
    print(
        '--> Creating Perfectly Correlated {0} values based on fracture radius.'
        .format(variable))
    units = get_units(variable)
    if variable == "aperture":
        print("b ={1}*r^{2} {3}".format(variable, params["alpha"],
                                        params["beta"], units))
    if variable == "permeability":
        print("k ={1}*r^{2} {3}".format(variable, params["alpha"],
                                        params["beta"], units))
    if variable == "transmissivity":
        print("T ={1}*r^{2} {3}".format(variable, params["alpha"],
                                        params["beta"], units))


    if variable == "aperture":
        b = params["alpha"] * radii**params["beta"]

        perm = convert(b, variable, "permeability")
        T = convert(b, variable, "transmissivity")

    elif variable == "permeability":
        perm = params["alpha"] * radii**params["beta"]

        b = convert(perm, variable, "aperture")
        T = convert(perm, variable, "transmissivity")

    elif variable == "transmissivity":
        T = params["alpha"] * radii**params["beta"]
        b = convert(T, variable, "aperture")
        perm = convert(T, variable, "permeability")

    print("--> Complete\n")
    return b, perm, T


def semi_correlated(params, variable, radii, number_of_fractures):
    """ Creates hydraulic properties of fractures based on power-law relationship with 
    fracture radius with a noise term. For example, log(T) = log(alpha*r^beta) + sigma * N(0,1)
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the power-law relationship. Must contain alpha and beta. 
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        radii : array
            array of fracture radii in the domain
        number_of_fractures : int
            number of fractures in the DFN 

    Returns
    ----------
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values
    """
    print("--> Creating Semi-Correlated {0} values based on fracture radius.".
          format(variable))
    print('--> Coefficient: {0}'.format(params["alpha"]))
    print('--> Exponent : {0}'.format(params["beta"]))
    print('--> Log Variance: {0}'.format(params["sigma"]))

    if variable == "aperture":
        b = params["alpha"] * radii**params["beta"]
        perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
        b = np.exp(np.log(b) + np.sqrt(params["sigma"]) * perturbation)

        perm = convert(b, variable, "permeability")
        T = convert(b, variable, "transmissivity")

    elif variable == "permeability":

        perm = params["alpha"] * radii**params["beta"]
        perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
        perm = np.exp(np.log(perm) + np.sqrt(params["sigma"]) * perturbation)

        b = convert(perm, variable, "aperture")
        T = convert(perm, variable, "transmissivity")

    elif variable == "transmissivity":

        T = params["alpha"] * radii**params["beta"]
        perturbation = np.random.normal(0.0, 1.0, number_of_fractures)
        T = np.exp(np.log(T) + np.sqrt(params["sigma"]) * perturbation)
        b = convert(T, variable, "aperture")
        perm = convert(T, variable, "permeability")

    print('--> Complete\n')
    return b, perm, T


def constant(params, variable, number_of_fractures):
    """ Creates hydraulic properties of fractures with constant values
    
    Parameters
    -----------
        params : dict 
            Dictionary of parameters for the power-law relationship. Must contain alpha and beta. 
        variable : string 
            name of values being generated. Acceptable values are aperture, permeability, and transmissivity
        number_of_fractures : int
            number of fractures in the DFN 

    Returns
    ----------
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values
    Returns
    ----------
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values

    Notes
    ----------
        Values are generated for the variable provided. The two remaining variables are derived using those values
    """

    print("--> Creating constant {0} values.".format(variable))
    units = get_units(variable)
    print("--> Value: {0} {1}".format(params["mu"], units))

    if variable == "aperture":
        b = params["mu"] * np.ones(number_of_fractures)
        perm = convert(b, variable, "permeability")
        T = convert(b, variable, "transmissivity")

    elif variable == "permeability":

        perm = params["mu"] * np.ones(number_of_fractures)
        b = convert(perm, variable, "aperture")
        T = convert(perm, variable, "transmissivity")

    elif variable == "transmissivity":

        T = params["mu"] * np.ones(number_of_fractures)
        b = convert(T, variable, "aperture")
        perm = convert(T, variable, "permeability")

    print('--> Complete\n')
    return b, perm, T


def dump_hydraulic_values(self, b, perm, T, prefix=None):
    """ Writes variable information to files.  
    
    Parameters
    -----------
        prefix : string
            prefix of aperture.dat and perm.dat file names
            prefix_aperture.dat and prefix_perm.dat 
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values
    Returns
    ----------
        None

    Notes
    ----------
    """
    print("--> Dumping values to files")
    n = len(b)
    # Write out new aperture.dat
    if prefix is not None:
        aper_filename = prefix + '_aperture.dat'
        perm_filename = prefix + '_perm.dat'
        trans_filename = prefix + '_transmissivity.dat'
    else:
        aper_filename = "aperture.dat"
        perm_filename = "perm.dat"
        trans_filename = "transmissivity.dat"

    # write aperture file
    print("--> Writing {0}".format(aper_filename))
    with open(aper_filename, 'w+') as fp:
        fp.write('aperture\n')
        for i in range(n):
            fp.write('-{0:d} 0 0 {1:0.5e}\n'.format(i + 7, b[i]))

    # write perm file
    print("--> Writing {0}".format(perm_filename))
    with open(perm_filename, 'w+') as fp:
        fp.write('permeability\n')
        for i in range(n):
            fp.write('-{0:d} 0 0 {1:0.5e} {1:0.5e} {1:0.5e}\n'.format(
                i + 7, perm[i]))

    print("--> Writing {0}".format(trans_filename))
    np.savetxt(trans_filename, T)
    print("Complete")


def generate_hydraulic_values(self,
                              variable,
                              relationship,
                              params,
                              radii_filename="radii_Final.dat",
                              family_id=None):
    """ Generates hydraulic property values. 

    Parameters
    -----------
        self : object 
            DFN Class 
        relationship : string
            name of functional relationship for apertures. 
            options are log-normal, correlated, semi-correlated, and
            constant
        params : dictionary
            dictionary of parameters for functional relationship
        family_id : int
            family id of fractures

    Returns
    ----------
        b : array
            aperture values
        perm : array
            permeability values
        T : array
            transmissivity values
        idx : array of bool
            true / false of fracture families requested. If family_id = None, all entires are true. 
            Only family members entires of b, perm, and T will be non-zero

    Notes
    ----------
    See Hyman et al. 2016 "Fracture size and transmissivity correlations: Implications for transport simulations in sparse
    three-dimensional discrete fracture networks following a truncated power law distribution of fracture size" Water Resources Research for more details 
    """

    # Check if the variable choice is defined
    variables = ["aperture", "permeability", "transmissivity"]
    if variable not in variables:
        error = "ERROR!!! The variable of choice '{0}'' is not known\nAcceptable names are {1}, {2}, {3}\nExiting.\n".format(
            variable, variables[0], variables[1], variables[2])
        sys.stderr.write(error)
        sys.exit(1)
    # else:
    #     print(
    #         "Creating aperture, permeability, and transmissivity based on {0}."
    #         .format(variable))

    # check if the function is defined
    functions = ["log-normal", "semi-correlated", "constant", "correlated"]
    if relationship not in functions:
        error = "ERROR!!! The provided relationship '{0}' is unknown\nAcceptable relationship are {1}, {2}, {3}, {4}\nExiting.\n".format(
            relationship, functions[0], functions[1], functions[2],
            functions[3])
        sys.stderr.write(error)
        sys.exit(1)
    # else:
    #     print(
    #         "Creating aperture, permeability, and transmissivity using the {0} function."
    #         .format(relationship))

    # Load Fracture information
    radii, families, number_of_fractures = load_fractures(radii_filename,quiet=True)

    if relationship == "log-normal":
        keys = ["mu", "sigma"]
        for key in keys:
            if not check_key(params, key):
                error = "ERROR!!! The required key '{0}' was not found in the params dictionary\nExiting\n".format(
                    key)
                sys.stderr.write(error)
                sys.exit(1)
        b, perm, T = log_normal(params, variable, number_of_fractures)

    if relationship == "correlated":
        keys = ["alpha", "beta"]
        for key in keys:
            if not check_key(params, key):
                error = "ERROR!!! The required key '{0}' was not found in the params dictionary\nExiting\n".format(
                    key)
                sys.stderr.write(error)
                sys.exit(1)
        b, perm, T = correlated(params, variable, radii)

    if relationship == "semi-correlated":
        keys = ["alpha", "beta", "sigma"]
        for key in keys:
            if not check_key(params, key):
                error = "ERROR!!! The required key '{0}' was not found in the params dictionary\nExiting\n\n".format(
                    key)
                sys.stderr.write(error)
                sys.exit(1)
        b, perm, T = semi_correlated(params, variable, radii, number_of_fractures)

    if relationship == "constant":
        keys = ["mu"]
        for key in keys:
            if not check_key(params, key):
                error = "ERROR!!! The required key '{0}' was not found in the params dictionary\nExiting\n\n".format(
                    key)
                sys.stderr.write(error)
                sys.exit(1)
        b, perm, T = constant(params, variable, number_of_fractures)


    if family_id == None:
        return b, perm, T
    else:
        # Sent entrites that are not in the requested family to None
        idx = np.where(families != family_id)
        b[idx] = 0  
        T[idx] = 0 
        perm[idx] = 0 
        return b,perm,T

# if __name__ == '__main__':

#     variable = "transmissivity"

#     function = "correlated"
#     params = {"alpha":6.7*10**-9,"beta":1.4}
#     _,_,T1 = generate_hydraulic_values(variable,function,params,radii_filename="/Users/jhyman/Desktop/radii_Final.dat",family_id=1)

#     function = "semi-correlated"
#     params = {"alpha":6.3*10**-9,"beta":0.5,"sigma":1.0}
#     _,_,T2 = generate_hydraulic_values(variable,function,params,radii_filename="/Users/jhyman/Desktop/radii_Final.dat",family_id=2)

#     #combine values
#     T = T1 + T2
#     print(T)

#     # convert to other variables
#     perm = convert(T,"transmissivity","permeability")
#     b = convert(T,"transmissivity","aperture")
#     # write to file
#     #dump_values("testing",b,perm,T)
