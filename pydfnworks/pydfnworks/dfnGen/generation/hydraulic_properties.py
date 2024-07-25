import numpy as np
import sys

from pydfnworks.general.logging import local_print_log

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
        error = f"Error. The variable of choice '{variable}' is not known in the function get_units()\nAcceptable names are aperture, permeability, and transmissivity\nExiting."
        local_print_log(error, 'error')
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


def load_fractures(filename, quiet):
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
        local_print_log(f"--> Loading Fracture information from {filename}")

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

    Notes
    -----
    permeability/Transmissivty are defined using the cubic law

    k = b^2/12

    T = (b^3 rho g)/(12 mu)

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
        error = f"Error in conversion. Unknown name provided in convert. Either '{source}' or '{target}' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n"
        local_print_log(error, 'error')


def log_normal(params, variable, number_of_fractures):
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
    local_print_log(f'--> Creating uncorrelated lognormal {variable} values.')
    units = get_units(variable)
    local_print_log(f"--> Mean: {params['mu']} {units}")
    local_print_log(f"--> Log Variance: {params['sigma']}")

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
        error = "Error. The variable of choice '{0}'' is not known\nAcceptable names are aperture, permeability, and transmissivity\nExiting.\n".format(
            variable)
        local_print_log(error, 'error')
    local_print_log('--> Complete\n')
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
    local_print_log(
        f'--> Creating Perfectly Correlated {variable} values based on fracture radius.'
    )
    units = get_units(variable)

    if variable == "aperture":
        local_print_log(f"\n b = {params['alpha']:0.2e} * r^{params['beta']} {units}\n")
    if variable == "permeability":
        local_print_log(f"\n k = {params['alpha']:0.2e} * r^{params['beta']} {units}\n")
    if variable == "transmissivity":
        local_print_log(f"\n T = {params['alpha']:0.2e} * r^{params['beta']} {units}\n")

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

    local_print_log("--> Complete\n")
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
    local_print_log("--> Creating Semi-Correlated {0} values based on fracture radius.".
          format(variable))
    local_print_log('--> Coefficient: {0}'.format(params["alpha"]))
    local_print_log('--> Exponent : {0}'.format(params["beta"]))
    local_print_log('--> Log Variance: {0}'.format(params["sigma"]))

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

    local_print_log('--> Complete\n')
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

    local_print_log("--> Creating constant {0} values.".format(variable))
    units = get_units(variable)
    local_print_log("--> Value: {0} {1}".format(params["mu"], units))

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

    local_print_log('--> Complete\n')
    return b, perm, T


def dump_aperture(self, filename, format=None):

    if format is None:
        np.savetxt(filename, self.aperture)
    elif format == "fehm" or format == "FEHM":
        self.print_log(f"--> Writing {filename}")
        with open(filename, 'w+') as fp:
            fp.write('aperture\n')
            for i, b in enumerate(self.aperture):
                fp.write(f'-{i+7:d} 0 0 {b:0.5e}\n')
    else:
        self.print_log("--> Warning. Unknown format requested.\nOptions are None and fehm/FEHM (case senstive)")

def dump_perm(self, filename, format=None):

    if format is None:
        np.savetxt(filename, self.perm)
    elif format == "fehm" or format == "FEHM":
        # write perm file
        self.print_log(f"--> Writing {filename}")
        with open(filename, 'w+') as fp:
            fp.write('permeability\n')
            for i, k in enumerate(self.perm):
                fp.write(f'-{i+7:d} 0 0 {k:0.5e} {k:0.5e} {k:0.5e}\n')
            fp.write("\n")


def dump_transmissivity(self, filename, format=None):
    if format is None:
        np.savetxt(filename, self.transmissivity)
    elif format == "fehm" or format == "FEHM":
        self.print_log(f"--> Writing {filename}")
        with open(filename, 'w+') as fp:
            fp.write('transmissivity\n')
            for i, trans in enumerate(self.transmissivity):
                fp.write(f'-{i:d} 0 0 {trans:0.5e}\n')


def dump_fracture_info(self, filename):

    ## revise fracture_info.dat
    self.print_log(f"--> Writing {filename}")
    connections = np.genfromtxt("dfnGen_output/fracture_info.dat",
                                skip_header=1)[:, 0].astype(int)
    with open(filename, "w+") as fp:
        fp.write("num_connections perm aperture\n")
        for i in range(self.num_frac):
            fp.write(
                f"{connections[i]:d} {self.perm[i]:0.8e} {self.aperture[i]:0.8e}\n"
            )
    self.print_log("--> Complete")


def dump_hydraulic_values(
    self,
    prefix=None,
    format=None,
):
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
    self.print_log("--> Dumping values to files")
    if not prefix:
        self.print_log(f"--> Using prefix {prefix}")
    if not format:
        self.print_log(f"--> Using format : {format}")
    # Write out new aperture.dat
    if prefix is not None:
        aper_filename = prefix + '_aperture.dat'
        perm_filename = prefix + '_perm.dat'
        trans_filename = prefix + '_transmissivity.dat'
        frac_info_filename = "dfnGen_output/" + prefix + '_fracture_info.dat'
    else:
        aper_filename = "aperture.dat"
        perm_filename = "perm.dat"
        trans_filename = "transmissivity.dat"
        frac_info_filename = "dfnGen_output/fracture_info.dat"

    self.dump_aperture(aper_filename, format)
    self.dump_perm(perm_filename, format)
    self.dump_transmissivity(trans_filename, format)
    self.dump_fracture_info(frac_info_filename)


def set_fracture_hydraulic_values(self, variable, fracture_list, value_list):
    """ Assigns hydraulic properties to a list of provided fractures. 

    Paramters
    -----------------
        self : object 
            DFN Class
        variable : string
            base variable in relationship. Options are: aperture, permeability, transmissivity
        fractture_list : list
            List of fractures index whose variables are being assigned. *Note* Fractures are indexed starting at 1.
        value_list : list  
            values to be assigned. 

    Returns 
    -------------
        None

    Notes
    ----------------
        None
    """

    if len(fracture_list) != len(value_list):
        error = f"Error. Length of fracture list is not equal to the length of the value list provided.\nExiting.\n"
        self.print_log(error, 'error')

    ## convert to numpy array
    value_list = np.array(value_list)
    fracture_list = np.array(fracture_list)

    # print(value_list)
    # print(fracture_list)
    if variable == 'aperture':
        b = value_list
        perm = convert(b, variable, "permeability")
        transmissivity = convert(b, variable, "transmissivity")

    elif variable == 'permeability':
        perm = value_list
        b = convert(perm, variable, "aperture")
        transmissivity = convert(perm, variable, "transmissivity")

    elif variable == 'transmissivity':
        transmissivity = value_list
        b = convert(transmissivity, variable, "aperture")
        perm = convert(transmissivity, variable, "permeability")

    else:
        error = f"Error. The variable of choice '{variable}' is not known\nAcceptable names are aperture, permeability, transmissivity\nExiting.\n"
        self.print_log(error, 'error')

    self.aperture[fracture_list - 1] = b
    self.perm[fracture_list - 1] = perm
    self.transmissivity[fracture_list - 1] = transmissivity


def generate_hydraulic_values(self,
                              variable,
                              relationship,
                              params,
                              family_id=None):
    """ Generates hydraulic property values. 

    Parameters
    -----------
        self : object 
            DFN Class
        variable : string
            base variable in relationship. Options are: aperture, permeability, transmissivity

        relationship : string
            name of functional relationship for apertures. 
            options are log-normal, correlated, semi-correlated, and
            constant
        params : dictionary
            dictionary of parameters for functional relationship
                if correlated --> {"alpha":value, "beta:value}
                if semi-correlated --> {"alpha":value, "beta":value, "sigma":value}
                if constant --> {"mu":value}
                if log-normal --> {"mu":value, "sigma":value}

        family_id : int
            family id of fractures

    Returns
    ----------
        None

    Notes
    ----------
    See Hyman et al. 2016 "Fracture size and transmissivity correlations: Implications for transport simulations in sparse
    three-dimensional discrete fracture networks following a truncated power law distribution of fracture size" Water Resources Research for more details 

    Changes in hydraulic properties are added to DFN object
    """
    # Check if the variable choice is defined
    variables = ["aperture", "permeability", "transmissivity"]
    if variable not in variables:
        error = "Error. The variable of choice '{0}'' is not known\nAcceptable names are {1}, {2}, {3}\nExiting.\n".format(
            variable, variables[0], variables[1], variables[2])
        self.print_log(error, 'error')
    # else:
    #     print(
    #         "Creating aperture, permeability, and transmissivity based on {0}."
    #         .format(variable))

    # check if the function is defined
    functions = ["log-normal", "semi-correlated", "constant", "correlated"]
    if relationship not in functions:
        error = f"Error! The provided relationship '{relationship}' is unknown\nAcceptable relationship are log-normal, semi-correlated, constant, or correlated\nExiting.\n"
        self.print_log(error, 'error')

    ## use max value of radius
    radii = self.radii[:, 2]
    families = self.families
    number_of_fractures = self.num_frac

    if family_id is not None:
        self.print_log(f"--> Working on Fracture Family {family_id}")
        idx = np.where(families == family_id)
        if len(idx[0]) == 0:
            error = f"Error. No fractures in the network are in the requested family. {family_id}.\nUser Rectangles = -1\nUser Ellipses = 0.\nStochastic Families > 0.\nExiting\n"
            self.print_log(error, 'error')

    if relationship == "log-normal":
        keys = ["mu", "sigma"]
        for key in keys:
            if not check_key(params, key):
                error = "Error. The required key '{0}' was not found in the params dictionary\nExiting\n".format(
                    key)
                self.print_log(error, 'error')
        b, perm, transmissivity = log_normal(params, variable,
                                             number_of_fractures)

    if relationship == "correlated":
        keys = ["alpha", "beta"]
        for key in keys:
            if not check_key(params, key):
                error = "Error. The required key '{0}' was not found in the params dictionary\nExiting\n".format(
                    key)
                self.print_log(error, 'error')
        b, perm, transmissivity = correlated(params, variable, radii)

    if relationship == "semi-correlated":
        keys = ["alpha", "beta", "sigma"]
        for key in keys:
            if not check_key(params, key):
                error = "Error. The required key '{0}' was not found in the params dictionary\nExiting\n\n".format(
                    key)
                self.print_log(error, 'error')
        b, perm, transmissivity = semi_correlated(params, variable, radii,
                                                  number_of_fractures)
    if relationship == "constant":
        keys = ["mu"]
        for key in keys:
            if not check_key(params, key):
                error = "Error. The required key '{0}' was not found in the params dictionary\nExiting\n\n".format(
                    key)
                self.print_log(error, 'error')
        b, perm, transmissivity = constant(params, variable,
                                           number_of_fractures)
    if family_id == None:
        self.aperture = b
        self.perm = perm
        self.transmissivity = transmissivity
    else:
        # Sent entries that are not in the requested family to None
        idx = np.where(families == family_id)
        self.aperture[idx] = b[idx]
        self.perm[idx] = perm[idx]
        self.transmissivity[idx] = transmissivity[idx]
