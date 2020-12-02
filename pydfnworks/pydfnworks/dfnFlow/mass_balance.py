#!/usr/bin/env python

# Calculate mass balance across a boundary of a DFN mesh
# Make sure that you run PFLOTRAN with MASS_FLOWRATE under OUTPUT
# Satish Karra
# March 17, 2016
# Updated Jeffrey Hyman Dec 19 2018

import numpy as np
import glob
from pydfnworks.dfnGen.meshing.mesh_dfn_helper import parse_params_file

__author__ = 'Satish Karra'
__email__ = 'satkarra@lanl.gov'


def get_domain():
    ''' Return dictionary of domain x,y,z by calling parse_params_file

    Parameters
    ----------
        None

    Returns
    -------
        domain : dict
            Dictionary of domain sizes in x, y, z

    Notes
    -----
        parse_params_file() is in mesh_dfn_helper.py
'''
    _, _, _, _, domain = parse_params_file(quiet=True)
    return domain


def parse_pflotran_input(pflotran_input_file):
    ''' Walk through PFLOTRAN input file and find inflow boundary, inflow and outflow pressure, and direction of flow

    Parameters
    ----------
        pflotran_input_file : string
            Name of PFLOTRAN input file

    Returns
    -------
        inflow_pressure : double
            Inflow Pressure boundary condition
        outflow_pressure : float
            Outflow pressure boundary condition
        inflow_file : string
            Name of inflow boundary .ex file 
        direction : string 
            Primary direction of flow x, y, or z

    Notes
    -----
    Currently only works for Dirichlet Boundary Conditions
'''

    with open(pflotran_input_file) as fp:
        outflow_found = False
        inflow_found = False
        for line in fp.readlines():
            if "BOUNDARY_CONDITION OUTFLOW" in line:
                outflow_found = True
            if outflow_found:
                if "REGION" in line:
                    outflow = line.split()[-1]
                    outflow_found = False
            if "BOUNDARY_CONDITION INFLOW" in line:
                inflow_found = True
            if inflow_found:
                if "REGION" in line:
                    inflow = line.split()[-1]
                    inflow_found = False

    with open(pflotran_input_file) as fp:
        inflow_name_found = False
        outflow_name_found = False
        inflow_found = False
        outflow_found = False

        for line in fp.readlines():
            if "REGION " + inflow in line:
                inflow_name_found = True
            if inflow_name_found:
                if "FILE" in line:
                    inflow_file = line.split()[-1]
                    inflow_name_found = False
            if "FLOW_CONDITION " + inflow in line:
                inflow_found = True
            if inflow_found:
                if "PRESSURE " in line:
                    if "dirichlet" not in line:
                        tmp = line.split()[-1]
                        tmp = tmp.split('d')
                        inflow_pressure = float(tmp[0]) * 10**float(tmp[1])
                        inflow_found = False

            if "REGION " + outflow in line:
                outflow_name_found = True
            if outflow_name_found:
                if "FILE" in line:
                    outflow_file = line.split()[-1]
                    outflow_name_found = False
            if "FLOW_CONDITION " + outflow in line:
                outflow_found = True
            if outflow_found:
                if "PRESSURE " in line:
                    if "dirichlet" not in line:
                        tmp = line.split()[-1]
                        tmp = tmp.split('d')
                        outflow_pressure = float(tmp[0]) * 10**float(tmp[1])
                        outflow_found = False

    if inflow_file == 'pboundary_left_w.ex' or inflow_file == 'pboundary_right_e.ex':
        direction = 'x'
    if inflow_file == 'pboundary_front_n.ex' or inflow_file == 'pboundary_back_s.ex':
        direction = 'y'
    if inflow_file == 'pboundary_top.ex' or inflow_file == 'pboundary_bottom.ex':
        direction = 'z'

    print("Inflow file: %s" % inflow_file)
    print("Inflow Pressure %e" % inflow_pressure)
    print("Outflow Pressure %e" % outflow_pressure)
    print("Primary Flow Direction : %s" % direction)

    return inflow_pressure, outflow_pressure, inflow_file, direction


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

    print("\n\nEffective Permeabilty Properties\n")
    fp = open(local_jobname + '_effective_perm.txt', "w")
    print('The mass flow rate [kg/s]: ' + str(mass_rate))
    fp.write('The mass flow rate [kg/s]: %e\n' % (mass_rate))
    print('The volume flow rate [m3/s]: ' + str(volume_rate))
    fp.write('The volume flow rate [m3/s]: %s\n' % (volume_rate))
    q = volume_rate / surface  #darcy flux over entire face m3/m2/s

    if direction == 'x':
        print('The darcy flow rate over %f x %f m2 area [m3/m2/s]: %e' %
              (domain['y'], domain['z'], q))
        fp.write('The darcy flow rate over %f x %f m2 area [m3/m2/s]: %e\n' %
                 (domain['y'], domain['z'], q))
        print('The darcy flow rate over %f x %f m2 area [m3/m2/y]: %e' %
              (domain['y'], domain['z'], spery * q))
        fp.write('The darcy flow rate over %f x %f m2 area [m3/m2/y]: %e\n' %
                 (domain['y'], domain['z'], spery * q))

    if direction == 'y':
        print('The darcy flow rate over %f x %f m2 area [m3/m2/s]: %e' %
              (domain['x'], domain['z'], q))
        fp.write('The darcy flow rate over %f x %f m2 area [m3/m2/s]: %e\n' %
                 (domain['x'], domain['z'], q))
        print('The darcy flow rate over %f x %f m2 area [m3/m2/y]: %e' %
              (domain['x'], domain['z'], spery * q))
        fp.write('The darcy flow rate over %f x %f m2 area [m3/m2/y]: %e\n' %
                 (domain['x'], domain['z'], spery * q))

    if direction == 'z':
        print('The darcy flow rate over %f x %f m2 area [m3/m2/s]: %e' %
              (domain['x'], domain['y'], q))
        fp.write('The darcy flow rate over %f x %f m2 area [m3/m2/s]: %e\n' %
                 (domain['x'], domain['y'], q))
        print('The darcy flow rate over %f x %f m2 area [m3/m2/y]: %e' %
              (domain['x'], domain['y'], spery * q))
        fp.write('The darcy flow rate over %f x %f m2 area [m3/m2/y]: %e\n' %
                 (domain['x'], domain['y'], spery * q))
    print('The effective permeability of the domain [m2]: ' +
          str(q * mu / pgrad))
    fp.write('The effective permeability of the domain [m2]: %e\n' %
             (q * mu / pgrad))
    fp.close()


def effective_perm(self):
    '''Computes the effective permeability of a DFN in the primary direction of flow using a steady-state PFLOTRAN solution. 

    Parameters
    ----------
        self : object 
            DFN Class

    Returns
    -------
        None

    Notes
    -----
    1. Information is written to screen and to the file self.local_jobname_effective_perm.txt
    2. Currently, only PFLOTRAN solutions are supported
    3. Assumes density of water 

'''
    print("\n--> Computing Effective Permeability of Block")
    if not self.flow_solver == "PFLOTRAN":
        print(
            "Incorrect flow solver selected. Cannot compute effective permeability"
        )
        return 0

    darcy_vel_file = 'darcyvel.dat'
    pflotran_input_file = self.local_dfnFlow_file

    inflow_pressure, outflow_pressure, boundary_file, direction = parse_pflotran_input(
        pflotran_input_file)
    domain = get_domain()
    mass_rate, volume_rate = flow_rate(darcy_vel_file, boundary_file)
    dump_effective_perm(self.local_jobname, mass_rate, volume_rate, domain,
                        direction, inflow_pressure, outflow_pressure)
    print("\n--> Complete\n\n")
