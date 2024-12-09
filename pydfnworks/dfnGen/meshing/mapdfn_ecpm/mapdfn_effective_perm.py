from pydfnworks.general.logging import initialize_log_file, print_log

def mapdfn_effective_perm(self, inflow_pressure, outflow_pressure, mas_filename,
                   direction):
    """ Reads <pflotran-file>-mas.dat file to get outflow mass flow rate from a pflotran run. Converts the values to volumetric flow rates in m^3/s, then inverts Darcy's Law to get the effective permeability of the block

    Parameters
    ----------
        self : object 
            DFN Class
        inflow_pressure: float
            Pressure at the inflow boundary face. Units are Pascal
        outflow_pressure: float
            Pressure at the outflow boundary face. Units are Pascal
        mas_filename: string
            name of -mas.dat filename. 
        direction: string
            Primary direction of flow, x, y, or z

    Returns
    -------
        keff : float
            effective permeability of the block

    Notes
    -----
    1. Information is written to screen and to the file self.local_jobname_effective_perm.txt
    2. Currently, only PFLOTRAN solutions are supported
    3. Assumes density of water at 20c 
    4. MASS_BALANCE output option in PFLOTRAN must be turned on. 
    
    
    """
    
    #filename = 'cpm_pflotran-mas.dat'
    with open(mas_filename, 'r') as fp:
        header = fp.readline().split(',')
        for line in fp.readlines():
            values = line.split(' ')
    # Remove None from list 
    values = list(filter(None, values))
    # find index of mass outflow rate 
    for index,name in enumerate(header):
        # print(name)
        if "outflow Water Mass [kg/" in name:
            self.print_log(index, name)
            break

    mass_flowrate_name = header[index]
    mass_flowrate_value = abs(float(values[index]))
    # print(mass_flowrate_name,  mass_flowrate_value )
    rates = ['kg/s', 'kg/d', 'kg/y']
    for irate,rate in enumerate(rates):
        if rate in mass_flowrate_name:
            self.print_log(f"Mass flow rate in {rate}")
            if irate > 0:
                self.print_log("Will convert to kg/s")
            break


    if irate == 1:
        # convert days to seconds
        mass_flowrate_value /= 86400
    elif irate == 2:
        # concert years to seconds 
        mass_flowrate_value /= 3.14 * 1e7

    ## Parameters 
    mu = 8.9e-4  #dynamic viscosity of water at 20 degrees C, Pa*s
    density = 9.980123e2 ## Density of water at 20 C
    volume_flowrate_value = mass_flowrate_value / density 
    self.print_log(f"Volumetric Flow Rate: {volume_flowrate_value} m^3/s")
    if direction == 'x':
        surface = self.domain['y'] * self.domain['z']
        L = self.domain['x']
    if direction == 'y':
        surface = self.domain['x'] * self.domain['z']
        L = self.domain['y']
    if direction == 'z':
        surface = self.domain['x'] * self.domain['y']
        L = self.domain['z']
    pgrad = (inflow_pressure - outflow_pressure) / L
    #darcy flux over entire face m3/m2/s
    q = volume_flowrate_value / surface
    keff = q * mu / pgrad
    self.print_log(f"Effective Perm : {keff}")
    return keff    
