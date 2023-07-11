import math as m
import numpy as np
import time 
import pydfnworks.dfnGen.meshing.mapdfn_ecpm.transformations as tr

def mapdfn_porosity(num_cells, cell_fracture_id, aperture, cell_size, matrix_porosity):
    '''Calculate fracture porosity for each cell of ECPM intersected by
     one or more fractures. Simplifying assumptions: 1) each fracture crosses
     the cell parallel to cell faces, 2) each fracture completely crosses the cell.
     Assign bulk porosity to cells not intersected by fractures.
     Return numpy array of porosity for each cell in the ECPM domain.

     fracture = numpy array containing number of fractures in each cell, list of fracture numbers in each cell
     apertures = list containing aperture of each fracture
     d = float length of cell side
     bulk_por = float bulk porosity (which would normally be larger than fracture porosity)
  '''

    t0 = time.time()

    # ncell = fracture.shape[0]
    # porosity = np.zeros((ncell), '=f8')
    # for i in range(ncell):
    #     if fracture[i][0] == 0:
    #         porosity[i] = matrix_porosity
    #     else:  #there are fractures in this cell
    #         for j in range(1, fracture[i][0] + 1):
    #             fracnum = fracture[i][j]
    #             porosity[i] += apertures[
    #                 fracnum -
    #                 1] / cell_size  #aperture is 0 indexed, fracture numbers are 1 indexed

    porosity = np.zeros(num_cells, '=f8')
    for key in cell_fracture_id.keys():
        if len(cell_fracture_id[key]) > 0:
            for ifrac in cell_fracture_id[key]:
                porosity[key] += aperture[ifrac]/cell_size 
        else:
            porosity[key] = matrix_porosity

    t1 = time.time()
    print(f'--> Time spent in porosity() = {t1 - t0:0.2f} sec')

    return porosity

def mapdfn_perm_iso(num_cells, cell_fracture_id, T, cell_size, k_background):
    '''Calculate isotropic permeability for each cell of ECPM intersected by
     one or more fractures. Sums fracture transmissivities and divides by 
     cell length (d) to calculate cell permeability.
     Assign background permeability to cells not intersected by fractures.
     Returns numpy array of isotropic permeability for each cell in the ECPM.

     fracture = numpy array containing number of fractures in each cell, list of fracture numbers in each cell
     T = [] containing intrinsic transmissivity for each fracture
     d = length of cell sides
     k_background = float background permeability for cells with no fractures in them
  '''
    t0 = time.time()
    # ncell = fracture.shape[0]
    # k_iso = np.full((ncell), k_background, '=f8')
    # for i in range(ncell):
    #     if fracture[i][0] != 0:
    #         for j in range(1, fracture[i][0] + 1):
    #             fracnum = fracture[i][j]
    #             k_iso[i] += T[
    #                 fracnum -
    #                 1] / cell_size  #T is 0 indexed, fracture numbers are 1 indexed

    k_iso = np.full(num_cells, k_background, '=f8')
    for key in cell_fracture_id.keys():
        if len(cell_fracture_id[key]) > 0:
            for ifrac in cell_fracture_id[key]:
                k_iso[key] += T[ifrac]/cell_size 

    t1 = time.time()
    print(f'--> Time spent in permIso() = {t1 - t0:0.2f} sec')
    return k_iso

def mapdfn_perm_aniso(num_frac, num_cells,cell_fracture_id, normal_vectors, T,
               cell_size,
               matrix_perm,
               LUMP = False,
               correction_factor=True):
    '''Calculate anisotropic permeability tensor for each cell of ECPM
     intersected by one or more fractures. Discard off-diagonal components
     of the tensor. Assign background permeability to cells not intersected
     by fractures.
     Return numpy array of anisotropic permeability (3 components) for each 
     cell in the ECPM.

     fracture = numpy array containing number of fractures in each cell, list of fracture numbers in each cell
     ellipses = [{}] containing normal and translation vectors for each fracture
     T = [] containing intrinsic transmissivity for each fracture
     d = length of cell sides
     k_background = float background permeability for cells with no fractures in them
  '''
    #quick error check
    ellipseT = np.zeros((num_frac, 3), '=f8')
    fullTensor = []
    T_local = np.zeros((3, 3), dtype=np.float)
    t0 = time.time()
    #calculate transmissivity tensor in domain coordinates for each ellipse
    for ifrac in range(num_frac):
        # normal = ellipses[f]['normal']
        normal = normal_vectors[ifrac]
        direction = np.cross(normal, [0, 0, 1])
        angle = np.arccos(normal[2])
        M = tr.rotation_matrix(angle, direction)
        Transpose = np.transpose(M[:3, :3])
        T_local[0, 0] = T[ifrac]
        T_local[1, 1] = T[ifrac]
        #permeability = 0 in local z direction of fracture
        T_domain = np.dot(np.dot(M[:3, :3], T_local), Transpose)
        ellipseT[ifrac][0:3] = [T_domain[0, 0], T_domain[1, 1], T_domain[2, 2]]
        fullTensor.append(T_domain)
    t1 = time.time()
    print('time spent calculating fracture transmissivity %f' % (t1 - t0))

    #in case you were wondering what those off-diagonal terms are:
    t0 = time.time()
    #fout=file('Ttensor.txt','w')
    with open('Ttensor.txt', 'w') as fout:
        for f in range(len(fullTensor)):
            fout.write(str(fullTensor[f]))
            fout.write('\n\n')
    t1 = time.time()
    print('time spent writing fracture transmissivity %f' % (t1 - t0))

    #calculate cell effective permeability by adding fracture k to background k
    t0 = time.time()
    # maxfrac = fracture.shape[1]
    k_aniso = np.full((num_cells, 3), matrix_perm, '=f8')
    for icell in range(num_cells):
        if len(cell_fracture_id[icell]) > 0:
            for ifrac in cell_fracture_id[icell]: 
                if LUMP:  #lump off diagonal terms
                    #because symmetrical doesn't matter if direction of summing is correct, phew!
                    k_aniso[icell][0] += np.sum(fullTensor[ifrac][0, :3]) / cell_size
                    k_aniso[icell][1] += np.sum(fullTensor[ifrac][1, :3]) / cell_size
                    k_aniso[icell][2] += np.sum(fullTensor[ifrac][2, :3]) / cell_size
                else:  #discard off diagonal terms (default)
                    #ellipseT is 0 indexed, fracture numbers are 1 indexed
                    k_aniso[icell][0] += ellipseT[ifrac][0] / cell_size  
                    k_aniso[icell][1] += ellipseT[ifrac][1] / cell_size
                    k_aniso[icell][2] += ellipseT[ifrac][2] / cell_size

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

                k_aniso[icell][0] *= cf_x
                k_aniso[icell][1] *= cf_y
                k_aniso[icell][2] *= cf_z

            ########
    t1 = time.time()
    print(f'Time spent summing cell permeabilities {t1 - t0}')

    return k_aniso


