import math as m
import numpy as np
import time
import pydfnworks.dfnGen.meshing.mapdfn_ecpm.transformations as tr
from pydfnworks.general.logging import local_print_log


def mapdfn_porosity(num_cells, cell_fracture_id, aperture, cell_size,
                    matrix_porosity):
    """ Calculate fracture porosity for each cell of ECPM intersected by one or more fractures. Simplifying assumptions: 1) each fracture crosses the cell parallel to cell faces, 2) each fracture completely crosses the cell. Assign bulk porosity to cells not intersected by fractures. 

    Parameters
    ---------------
        num_cells : int
            Total number of cells in the domain 
    
        cell_fracture_id : dict
            Dictionary num_cells long. Keys: cell number, Entries: List of the fractures that intersect that cell

        aperture : numpy array
            array of fracture apertures (likely from DFN.aperture)

        cell_size : float 
            discretization length in ECPM domain
        
        matrix_porosity : float
            porosity of the matrix cells without fratures 

    Returns
    -----------
        porosity : numpy array
            porosity values in the domain cells

    Notes
    ----------
        None
    """

    local_print_log(f'--> Upscaling porosity')
    porosity = np.zeros(num_cells, '=f8')
    for cell_id, fractures in cell_fracture_id.items():
        if len(fractures) > 0:
            for ifrac in fractures:
                # fracture volume fraction is (aperture * cell_size**2 / cell_size**3)
                porosity[cell_id] += aperture[ifrac] / cell_size
        else:
            porosity[cell_id] = matrix_porosity
        if porosity[cell_id] > 1:
            # print("Error, porisity is greater than 1")
            porosity[cell_id] = 1
    return porosity


def mapdfn_perm_iso(num_cells, cell_fracture_id, perm, aperture, porosity, cell_size,
                    matrix_perm):
    """ Calculate isotropic permeability for each cell of ECPM intersected by one or more fractures. Sums fracture permeabilities and multiples by fracture volume (aperture*d*d/d**3) length (d) to calculate cell permeability. 
    4 March 2024 : Adjusted to also include matrix contribution to flow
    Assign background permeability to cells not intersected by fractures. 
    
    Parameters
    --------------
        num_cells : int
            Total number of cells in the domain 
    
        cell_fracture_id : dict
            Dictionary num_cells long. Keys: cell number, Entries: List of the fractures that intersect that cell

        perm : numpy array
            array of fracture perm (k)

        aperture : numpy array
            array of fracture aperture (b)

        porosity : numpy array 
            fracture porosity values in the domain cells


        cell_size : float 
            discretization length in ECPM domain
        
        matrix_permeablity : float
            permeability of the matrix cells without fratures 

    Returns
    --------------
        k_iso : numpy array
            numpy array of isotropic permeability for each cell in the ECPM.

    
    Notes
    ----------
  
    """

    local_print_log(f'--> Computing Isotropic Permeability')
    k_iso = np.full(num_cells, matrix_perm, '=f8')
    for cell_id, fractures in cell_fracture_id.items():
        local_perm  = 0
        if len(fractures) > 0:
            for ifrac in fractures:
                # k_iso[cell_id] += transmissivity[ifrac] / cell_size 
                ## this is a weighted average based on the fracture volume
                # fracture volume fraction is (aperture * cell_size**2 / cell_size**3)
                local_perm += (aperture[ifrac]/cell_size) * perm[ifrac]
                # local_perm += transmissivity[ifrac] / cell_size
                # print(local_perm)
        ## weighted average 
        # print("Using Weighted average")
        # print(f"matrix_perm**(1-porosity[cell_id] : {matrix_perm**(1-porosity[cell_id])}")
        # print(f"local_perm {local_perm}")
        # print(f"porosity {porosity[cell_id]}")
        # print(f"local_perm**(porosity[cell_id] : {local_perm**(porosity[cell_id])}")
        # geo_mean_perm = (matrix_perm**(1-porosity[cell_id])) * ( local_perm**porosity[cell_id])
        # print(f"geo-mean: {geo_mean_perm:0.2e}")
        k_iso[cell_id] = max(matrix_perm, ( 1 - porosity[cell_id] ) * matrix_perm  + porosity[cell_id] * local_perm)
        # k_iso[cell_id] = max(geo_mean_perm, local_perm)
        # k_iso[cell_id] = local_perm 
    return k_iso


def mapdfn_perm_aniso(num_frac,
                      num_cells,
                      cell_fracture_id,
                      normal_vectors,
                      perm, 
                      aperture,
                      porosity,
                      cell_size,
                      matrix_perm,
                      lump_diag_terms=False,
                      correction_factor=True):
    """ Calculate anisotropic permeability tensor for each cell of ECPM intersected by one or more fractures. Discard off-diagonal components of the tensor. Assign background permeability to cells not intersected by fractures.

    Parameters
    -------------------
        num_frac : int
            Number of fractures in the DFN

        num_cells : int
            Total number of cells in the domain 
    
        cell_fracture_id : dict
            Dictionary num_cells long. Keys: cell number, Entries: List of the fractures that intersect that cell

        normal_vectors : numpy array 
            array of fracture normal vectors 

        perm : numpy array
            array of fracture perm (k)

        aperture : numpy array
            array of fracture aperture (b)

        cell_size : float 
            discretization length in ECPM domain
        
        matrix_perm : float
            permeability of the matrix cells without fratures 

        lump_diag_terms : bool
            Default is False

        correction_factor : bool
            Default is True

    Returns
    --------------
            k_aniso : numpy array
                Return numpy array of anisotropic permeability (3 components) for each cell in the ECPM.

    Notes
    ---------------
        None

    """
    local_print_log(f'--> Computing anisotropic permeability')

    #quick error check
    fracture_trans = np.zeros((num_frac, 3), '=f8')
    full_tensor = []
    T_local = np.zeros((3, 3))
    #calculate transmissivity tensor in domain coordinates for each ellipse
    for ifrac in range(num_frac):
        # normal = ellipses[f]['normal']
        normal = normal_vectors[ifrac]
        direction = np.cross(normal, [0, 0, 1])
        angle = np.arccos(normal[2])
        M = tr.rotation_matrix(angle, direction)
        Transpose = np.transpose(M[:3, :3])
        # T_local[0, 0] = transmissivity[ifrac]
        # T_local[1, 1] = transmissivity[ifrac]
        T_local[0, 0] = aperture[ifrac]*perm[ifrac]
        T_local[1, 1] =  aperture[ifrac]*perm[ifrac]
        #permeability = 0 in local z direction of fracture
        T_domain = np.dot(np.dot(M[:3, :3], T_local), Transpose)
        fracture_trans[ifrac][0:3] = [
            T_domain[0, 0], T_domain[1, 1], T_domain[2, 2]
        ]
        full_tensor.append(T_domain)

    # #in case you were wondering what those off-diagonal terms are:
    # t0 = time.time()
    # #fout=file('Ttensor.txt','w')
    # with open('Ttensor.txt', 'w') as fout:
    #     for f in range(len(full_tensor)):
    #         fout.write(str(full_tensor[f]))
    #         fout.write('\n\n')
    # t1 = time.time()
    # print('time spent writing fracture transmissivity %f' % (t1 - t0))

    #calculate cell effective permeability by adding fracture k to background k
    t0 = time.time()
    k_aniso = np.full((num_cells, 3), matrix_perm, '=f8')
    for icell in range(num_cells):
        k_aniso_x = 0
        k_aniso_y = 0
        k_aniso_z = 0
        if len(cell_fracture_id[icell]) > 0:
            for ifrac in cell_fracture_id[icell]:
                if lump_diag_terms:  #lump off diagonal terms
                    #because symmetrical doesn't matter if direction of summing is correct, phew!
                    # k_aniso[icell][0] += np.sum(
                    #     full_tensor[ifrac][0, :3]) / cell_size
                    # k_aniso[icell][1] += np.sum(
                    #     full_tensor[ifrac][1, :3]) / cell_size
                    # k_aniso[icell][2] += np.sum(
                    #     full_tensor[ifrac][2, :3]) / cell_size

                    k_aniso_x += np.sum(
                        full_tensor[ifrac][0, :3]) / cell_size
                    k_aniso_y += np.sum(
                        full_tensor[ifrac][1, :3]) / cell_size
                    k_aniso_z += np.sum(
                        full_tensor[ifrac][2, :3]) / cell_size


                else:  #discard off diagonal terms (default)
                    #fracture_trans is 0 indexed, fracture numbers are 1 indexed
                    # k_aniso[icell][0] += fracture_trans[ifrac][0] / cell_size
                    # k_aniso[icell][1] += fracture_trans[ifrac][1] / cell_size
                    # k_aniso[icell][2] += fracture_trans[ifrac][2] / cell_size

                    k_aniso_x += fracture_trans[ifrac][0] / cell_size
                    k_aniso_y += fracture_trans[ifrac][1] / cell_size
                    k_aniso_z += fracture_trans[ifrac][2] / cell_size



            if correction_factor:
                #correction factor Sweeney et al. 2019 from upscale.py

                min_n1 = 1e6
                min_n2 = 1e6
                min_n3 = 1e6

                for ifrac in cell_fracture_id[icell]:
                    # normal = ellipses[ifrac]['normal']
                    n1_temp = normal[0]
                    theta1_t = m.degrees(m.acos(n1_temp)) % 90
                    if abs(theta1_t - 45) <= min_n1:
                        theta1 = theta1_t
                        min_n1 = theta1_t
                    n2_temp = normal[1]
                    theta2_t = m.degrees(m.acos(n2_temp)) % 90
                    if abs(theta2_t - 45) <= min_n2:
                        theta2 = theta2_t
                        min_n2 = theta2_t
                    n3_temp = normal[2]
                    theta3_t = m.degrees(m.acos(n3_temp)) % 90
                    if abs(theta3_t - 45) <= min_n3:
                        theta3 = theta3_t
                        min_n3 = theta3_t

                sl = (2 * 2**(1. / 2) - 1) / -45.0
                b = 2 * 2**(1. / 2)

                cf_x = sl * abs(theta1 - 45) + b
                cf_y = sl * abs(theta2 - 45) + b
                cf_z = sl * abs(theta3 - 45) + b

                # k_aniso[icell][0] *= cf_x
                # k_aniso[icell][1] *= cf_y
                # k_aniso[icell][2] *= cf_z

                k_aniso_x *= cf_x
                k_aniso_y *= cf_y
                k_aniso_z *= cf_z

            ########

        k_aniso[icell][0] = max(matrix_perm, ( 1 - porosity[icell]) * matrix_perm + porosity[icell] * k_aniso_x)
        k_aniso[icell][1] = max(matrix_perm, ( 1 - porosity[icell]) * matrix_perm + porosity[icell] * k_aniso_y)
        k_aniso[icell][2] = max(matrix_perm, ( 1 - porosity[icell]) * matrix_perm + porosity[icell] * k_aniso_z)

    return k_aniso


def mapdfn_upscale(self, num_cells, cell_fracture_id, cell_size,
                   matrix_porosity, matrix_perm, lump_diag_terms,
                   correction_factor):
    """ 
  
    Parameters
    -----------------
        self : dfnWorks object

        num_cells : int
            Total number of cells in the domain 
    
        cell_fracture_id : dict
            Dictionary num_cells long. Keys: cell number, Entries: List of the fractures that intersect that cell

        cell_size : float 
            discretization length in ECPM domain
        
        matrix_porosity : float
            perosity of the matrix

        matrix_perm : float
            permeability of the matrix cells without fratures 

        lump_diag_terms : bool
            Default is False

        correction_factor : bool
            Default is True
        
    Returns
    -----------------
        porosity : numpy array
            porosity values in the domain cells
        k_iso : numpy array
            numpy array of isotropic permeability for each cell in the ECPM.
        k_aniso : numpy array
            Return numpy array of anisotropic permeability (3 components) for each cell in the ECPM.

    Notes
    -----------------

    """
    self.print_log("\n** Starting upscaling **")
    t0 = time.time()
    # compute the porosities of the cells
    porosity = mapdfn_porosity(num_cells, cell_fracture_id, self.aperture,
                               cell_size, matrix_porosity)
    # transmissivity = self.aperture * self.perm
    # compute the perms
    k_iso = mapdfn_perm_iso(num_cells, cell_fracture_id, self.perm, self.aperture, porosity, 
                            cell_size, matrix_perm)
    k_aniso = mapdfn_perm_aniso(self.num_frac, num_cells, cell_fracture_id,
                                self.normal_vectors, self.perm, self.aperture, porosity, cell_size,
                                matrix_perm, lump_diag_terms,
                                correction_factor)
    t1 = time.time()
    self.print_log(
        f"** Upscaling Complete. Time required : {t1 - t0:0.2f} seconds **\n")
    return porosity, k_iso, k_aniso
