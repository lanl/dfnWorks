#!/usr/bin/env python

# Calculate mass balance across a boundary of a DFN mesh
# Make sure that you run PFLOTRAN with MASS_FLOWRATE under OUTPUT
# Satish Karra
# March 17, 2016
# Updated Jeffrey Hyman Dec 19 2018
# Revision Jeffrey Hyman Oct 5 2020

import os
import numpy as np
import glob

__author__ = 'Satish Karra'
__email__ = 'satkarra@lanl.gov'


def check_inputs(boundary_file, direction, inflow_pressure, outflow_pressure):

    ## Check Pressure
    if inflow_pressure < outflow_pressure:
        print(
            "--> ERROR! Inflow Pressure less the outflow pressure. Cannot compute effective permeability"
        )
        return False

    if not os.path.exists(boundary_file):
        print(f"--> ERROR! Boundary file not found. Please check path.")
        return False

    ## Check Direction
    fail = False
    if direction == 'x':
        if not boundary_file in [
                'pboundary_left_w.ex', 'pboundary_right_e.ex'
        ]:
            print(
                f"--> ERROR! Direction {direction} is not consistent with boundary file {boundary_file}. Cannot compute effective permeability."
            )
            return False

    elif direction == 'y':
        if not boundary_file in [
                'pboundary_front_n.ex', 'pboundary_back_s.ex'
        ]:
            print(
                f"--> ERROR! Direction {direction} is not consistent with boundary file {boundary_file}. Cannot compute effective permeability."
            )
            return False

    elif direction == 'z':
        if not boundary_file in [
                'pboundary_top.ex', 'pboundary_bottom.ex'
        ]:
            print(
                f"--> ERROR! Direction {direction} is not consistent with boundary file {boundary_file}. Cannot compute effective permeability."
            )
            return False
    return True


def flow_rate(darcy_vel_file, boundary_file):
    '''Calculates the flow rate across the inflow boundary

    Parameters
    ----------
        darcy_vel_file : string
            Name of concatenated Darcy velocity file
        boundary_file : string
             ex file for the inflow boundary

    Returns
    -------
        mass_rate : float
            Mass flow rate across the inflow boundary
        volume_rate : float
            Volumetric flow rate across the inflow boundary

    Notes
    -----
    None
'''
    # Calculate the mass flow rate
    mass_rate = 0.0  #kg/s
    volume_rate = 0.0  #m^3/s

    dat_boundary = np.genfromtxt(boundary_file, skip_header=1)
    dat = np.genfromtxt(darcy_vel_file)
    for cell in dat_boundary[:, 0]:
        if (np.any(dat[:, 0] == int(cell))):
            ids = np.where(dat[:, 0] == int(cell))[0]
            for idx in ids:
                cell_up = int(dat[idx, 0])
                cell_down = int(dat[idx, 1])
                mass_flux = dat[idx, 2]  # in m/s , darcy flux, right? m3/m2/s
                density = dat[idx, 3]  # in kg/m3
                area = dat[idx, 4]  # in m^2
                if (cell_up == int(cell)):
                    mass_rate = mass_flux * area * \
                    density + mass_rate  # in kg/s
                    volume_rate = mass_flux * area + volume_rate  #in m3/s
                else:
                    mass_rate = - mass_flux * area * \
                    density + mass_rate  # in kg/s
                    volume_rate = -mass_flux * area + volume_rate  #in m3/s
                #print cell_up, cell_down, mass_flux, density, area, mass_rate, volume_rate
        if (np.any(dat[:, 1] == int(cell))):
            ids = np.where(dat[:, 1] == int(cell))[0]
            for idx in ids:
                cell_up = int(dat[idx, 0])
                cell_down = int(dat[idx, 1])
                mass_flux = dat[idx, 2]  # in m/s
                density = dat[idx, 3]  # in kg/m3
                area = dat[idx, 4]  # in m^2
                if (cell_up == int(cell)):
                    mass_rate = mass_flux * area * \
                    density + mass_rate  # in kg/s
                    volume_rate = mass_flux * area + volume_rate  #in m3/s
                else:
                    mass_rate = - mass_flux * area * \
                    density + mass_rate  # in kg/s
                    volume_rate = -mass_flux * area + volume_rate  #in m3/s
                #print cell_up, cell_down, mass_flux, density, area, mass_rate, volume_rate
    return mass_rate, volume_rate


def dump_effective_perm(local_jobname, mass_rate, volume_rate, domain,
                        direction, inflow_pressure, outflow_pressure):
    '''Compute the effective permeability of the DFN and write it to screen and to the file local_jobname_effective_perm.dat

    Parameters
    ----------
        local_jobname  : string
            Jobname
        mass_rate : float
            Mass flow rate through inflow boundary
        volume_rate : float
            Volumetric flow rate through inflow boundary
        direction : string
            Primary direction of flow (x, y, or z)
        domain : dict
            Dictionary of domain sizes in x, y, z
        inflow_pressure : float
            Inflow boundary pressure
        outflow_pressure : float
            Outflow boundary pressure

    Returns
    -------
        None

    Notes
    -----
    Information is written into (local_jobname)_effective_perm.txt
'''

    Lm3 = domain['x'] * domain['y'] * domain['z']  #L/m^3
    # if flow is in x direction, cross section is domain['y']*domain['z']
    if direction == 'x':
        surface = domain['y'] * domain['z']
        L = domain['x']
    if direction == 'y':
        surface = domain['x'] * domain['z']
        L = domain['y']
    if direction == 'z':
        surface = domain['x'] * domain['y']
        L = domain['z']
    # Print the calculated mass flow rate in kg/s
    mu = 8.9e-4  #dynamic viscosity of water at 20 degrees C, Pa*s
    spery = 3600. * 24. * 365.25  #seconds per year
    # compute pressure gradient
    pgrad = (inflow_pressure - outflow_pressure) / L
    #darcy flux over entire face m3/m2/s
    q = volume_rate / surface

    output_string = f'''The mass flow rate [kg/s]: {mass_rate:0.5e}
The volume flow rate [m^3/s]: {volume_rate:0.5e}
'''

    if direction == 'x':
        output_string += f'''The Darcy flow rate over {domain['y']} x {domain['z']} m^2 area [m^3/m^2/s]: {q:0.5e}
The Darcy flow rate over {domain['y']} x {domain['z']} m^2 area [m^3/m^2/y]: {spery*q:0.5e}
'''
    elif direction == 'y':
        output_string += f'''The Darcy flow rate over {domain['x']} x {domain['z']} m^2 area [m^3/m^2/s]: {q:0.5e}
The Darcy flow rate over {domain['x']} x {domain['z']} m^2 area [m^3/m^2/y]: {spery*q:0.5e}
'''
    elif direction == 'y':
        output_string += f'''The Darcy flow rate over {domain['x']} x {domain['y']} m^2 area [m^3/m^2/s]: {q:0.5e}
The Darcy flow rate over {domain['x']} x {domain['y']} m^2 area [m^3/m^2/y]: {spery*q:0.5e}
'''
    output_string += f'The effective permeability of the domain [m^2]: {q * mu / pgrad:0.5e}'
    print("\n--> Effective Permeability Properties: ")
    print(output_string)
    fp = open(f'{local_jobname}_effective_perm.txt', "w")
    fp.write(output_string)
    fp.close()
    keff = q * mu / pgrad
    return keff


def effective_perm(self, inflow_pressure, outflow_pressure, boundary_file,
                   direction):
    '''Computes the effective permeability of a DFN in the primary direction of flow using a steady-state PFLOTRAN solution. 

    Parameters
    ----------
        self : object 
            DFN Class
        inflow_pressure: float
            Pressure at the inflow boundary face. Units are Pascal
        outflow_pressure: float
            Pressure at the outflow boundary face. Units are Pascal
        boundary_file: string
            Name of inflow boundary file, e.g., pboundary_left.ex
        direction: string
            Primary direction of flow, x, y, or z

    Returns
    -------
        None

    Notes
    -----
    1. Information is written to screen and to the file self.local_jobname_effective_perm.txt
    2. Currently, only PFLOTRAN solutions are supported
    3. Assumes density of water at 20c 

'''
    print("--> Computing Effective Permeability of Block\n")
    if not self.flow_solver == "PFLOTRAN":
        print(
            "Incorrect flow solver selected. Cannot compute effective permeability"
        )
        return 0

    darcy_vel_file = 'darcyvel.dat'
    pflotran_input_file = self.local_dfnFlow_file

    print(f"--> Inflow file name:\t\t{boundary_file}")
    print(f"--> Darcy Velocity File:\t{darcy_vel_file}")
    print(f"--> Inflow Pressure:\t\t{inflow_pressure:0.5e} Pa")
    print(f"--> Outflow Pressure:\t\t{outflow_pressure:0.5e} Pa")
    print(f"--> Primary Flow Direction:\t{direction}")

    if not check_inputs(boundary_file, direction, inflow_pressure,
                        outflow_pressure):
        return 1

    mass_rate, volume_rate = flow_rate(darcy_vel_file, boundary_file)
    keff = dump_effective_perm(self.local_jobname, mass_rate, volume_rate,
                               self.domain, direction, inflow_pressure,
                               outflow_pressure)
    print("--> Complete\n\n")
    self.keff = keff
