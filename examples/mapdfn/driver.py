#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 12:04:03 2020

@author: rosie
"""

import os, sys
from pydfnworks import *

src_path = os.getcwd()

jobname = f"{src_path}/output"

DFN = DFNWORKS(jobname)

DFN.params['domainSize']['value'] = [1000.0, 1000.0, 1000.0]
DFN.params['domainSizeIncrease']['value'] = [100, 100, 100]
DFN.params['domainCenter']['value'] = [500, 500, 500]

DFN.params['h']['value'] = 3.0
DFN.params['stopCondition']['value'] = 1
DFN.params['seed']['value'] = 1
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]
DFN.params['visualizationMode']['value'] = True
DFN.params['seed']['value'] = 200  #seed for random generator 0 seeds off clock
DFN.params['ignoreBoundaryFaces']['value'] = False
DFN.params['boundaryFaces']['value'] = [1, 1, 0, 0, 0, 0]

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        p32=0.0099,
                        number_of_points=12,
                        kappa=9.41,
                        theta=95,
                        phi=274,
                        alpha=2.4,
                        min_radius=30.0,
                        max_radius=564.0,
                        hy_variable='permeability',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 1e-12,
                            "beta": 0.9,
                        })

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        p32=0.0113,
                        number_of_points=12,
                        kappa=8.3,
                        theta=90,
                        phi=180,
                        alpha=2.4,
                        min_radius=30.0,
                        max_radius=564.0,
                        hy_variable='permeability',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 1e-12,
                            "beta": 0.9,
                        })

DFN.add_fracture_family(shape="ell",
                        distribution="tpl",
                        p32=0.0240,
                        number_of_points=12,
                        kappa=5.7,
                        theta=169,
                        phi=150,
                        alpha=2.4,
                        min_radius=30.0,
                        max_radius=564.0,
                        hy_variable='permeability',
                        hy_function='correlated',
                        hy_params={
                            "alpha": 1e-12,
                            "beta": 0.9,
                        })

DFN.add_user_fract(shape='ell',
                   radii=600,
                   translation=[-400, 0, 200],
                   normal_vector=[30, 15, 60],
                   number_of_vertices=5,
                   aperture=1.0e-3)

DFN.add_user_fract(shape='ell',
                   radii=1000,
                   translation=[0, 0, 0],
                   normal_vector=[95, 5, 0],
                   number_of_vertices=5,
                   aperture=1.0e-3)

DFN.add_user_fract(shape='ell',
                   radii=600,
                   aspect_ratio=1,
                   translation=[400, 0, 200],
                   normal_vector=[30, 15, 60],
                   number_of_vertices=5,
                   aperture=1.0e-3)

DFN.add_user_fract(shape='ell',
                   radii=600,
                   aspect_ratio=1,
                   translation=[400, 0, -400],
                   normal_vector=[30, 15, 60],
                   number_of_vertices=5,
                   aperture=5.0e-5)

DFN.make_working_directory(delete=True)
DFN.print_domain_parameters()
DFN.check_input()
DFN.create_network()
#DFN.dump_hydraulic_values()
#DFN.mesh_network()

#DFN.dfn_flow()
mat_perm = 1e-13
mat_por = 0.1
cell_size = 20
DFN.mapdfn_ecpm(mat_perm, mat_por, cell_size )

DFN.dfnFlow_file = f"{src_path}/cpm_pflotran.in"
DFN.local_dfnFlow_file = f"cpm_pflotran.in"
DFN.pflotran()

DFN.dfnFlow_file = f"{src_path}/cpm_transport.in"
DFN.local_dfnFlow_file = f"cpm_transport.in"
DFN.pflotran()
