'''
   mapdfn.py

   Take output of dfnWorks-Version2.0:
   normal_vectors.dat, translations.dat, radii_Final.dat,
   perm.dat, aperture.dat
   and map dfn into a regular grid for continuous porous medium representation

   Usage: Call the methods in this script with map.py

   Dependencies: transformations.py copyright Christoph Gohlke and UC Regents
                 numpy
                 h5py
                 time

   Authors: Emily Stein (ergiamb@sandia.gov)
            Kris Kuhlman (klkuhl@sandia.gov)
            Applied Systems Analysis and Research, 8844
            Sandia National Laboratories

   Date: 07/13/18
   SAND Number: SAND2018-7604 O

   Modified by Teresa Portone (tporton@sandia.gov) Dec 1, 2021 to have porosity() take
   list of apertures instead of aperture filename. readApertures() method added.

   Modified by Rosie Leone (rleone@sandia.gov) Dec 16, 2021 to have permAniso() apply a stair step correction factor to the ECPM when conditional set to True

    Modified by Jeffrey Hyman 

'''

import time
import numpy as np
import transformations as tr
from h5py import File
import math as m
import itertools

def get_ellipses(radii, normals, translations):
    '''Read dfnWorks-Version2.0 output files describing radius, orientation, and
     location of fractures in space.
     Subsequent methods assume elliptical (in fact circular) fractures.
     Return a list of dictionaries describing each ellipse.
  '''
    ellipses = []
    for i in range(len(radii)):
        ellipses.append({
            'normal': np.zeros((3), dtype=np.float),
            'translation': np.zeros((3), dtype=np.float),
            'xrad': 0.0,
            'yrad': 0.0
        })
        ellipses[i]['normal'] = normals
        ellipses[i]['translation'] = translations
        ellipses[i]['xrad'] = radii[0] 
        ellipses[i]['yrad'] = radii[1] 

    return ellipses

def get_corner(origin, i, j, k, cell_size):
   
  corner = [[origin[0] + i * cell_size, origin[1] + j * cell_size,
            origin[2] + k * cell_size],
            [origin[0] + (i + 1) * cell_size,origin[1] + j * cell_size, origin[2] + k * cell_size],
            [origin[0] + (i + 1) * cell_size,origin[1] + (j + 1) * cell_size,origin[2] + k * cell_size],
            [origin[0] + i * cell_size,origin[1] + (j + 1) * cell_size,origin[2] + k * cell_size],
            [origin[0] + i * cell_size, origin[1] + j * cell_size,origin[2] + (k + 1) * cell_size],
            [origin[0] + (i + 1) * cell_size,origin[1] + j * cell_size,origin[2] + (k + 1) * cell_size],
            [origin[0] + (i + 1) * cell_size,origin[1] + (j + 1) * cell_size,origin[2] + (k + 1) * cell_size],
            [origin[0] + i * cell_size,origin[1] + (j + 1) * cell_size,origin[2] + (k + 1) * cell_size]]
  return corner 

def tag_cells(self, origin, nx, ny, nz, cell_size):
  '''Identify intersecting fractures for each cell of the ECPM domain.
    Extent of ECPM domain is determined by nx,ny,nz, and d (see below).
     ECPM domain can be smaller than the DFN domain.
     Return numpy array (fracture) that contains for each cell:
     number of intersecting fractures followed by each intersecting fracture id.

     ellipses = list of dictionaries containing normal, translation, xrad, 
                and yrad for each fracture
     origin = [x,y,z] float coordinates of lower left front corner of DFN domain
     nx = int number of cells in x in ECPM domain
     ny = int number of cells in y in ECPM domain
     nz = int number of cells in z in ECPM domain
     d = float discretization length in ECPM domain
  '''
  num_cells = nx * ny * nz
  fracture = np.zeros((num_cells, 20), dtype=np.int)
  # List of Keys
  index_list = range(num_cells)  
  # Using Dictionary comprehension
  cell_fracture_id = {key: None for key in index_list}
  t0 = time.time()
  # mod = nfrac/10
  for f in range(self.num_fracs):
    #   if f%mod == 0:
    print(f'--> Mapping ellipse {f} of {self.num_frac}.')
    tnow = time.time() - t0
    print(f'--> Time elapsed in map_dfn() = {tnow}.')
    normal = self.normal_vectors[i]
    translation =  self.centers[i]
    xrad = self.radii[i][0]
    yrad = self.radii[i][1]
    #calculate rotation matrix for use later in rotating coordinates of nearby cells
    direction = np.cross([0, 0, 1], normal)
    #cosa = np.dot([0,0,1],normal)/(np.linalg.norm([0,0,1])*np.linalg.norm(normal)) #frobenius norm = length
    #above evaluates to normal[2], so:
    angle = np.arccos(normal[2])  # everything is in radians
    M = tr.rotation_matrix(angle, direction)
    #find fracture in domain coordinates so can look for nearby cells
    # This can be rebuilt using the polygon boundary 

    max_rad = max(xrad, yrad)
    x1 = translation[0] - max_rad
    x2 = translation[0] + max_rad
    y1 = translation[1] - max_rad
    y2 = translation[1] + max_rad
    z1 = translation[2] - max_rad
    z2 = translation[2] + max_rad 

    #find indices of nearby cells so don't have to check all of them!
    i1 = max(0, int((x1 - origin[0]) / cell_size))  #round down
    i2 = min(nx, int((x2 - origin[0]) / cell_size + 1))  #round up
    j1 = max(0, int((y1 - origin[1]) / cell_size))
    j2 = min(ny, int((y2 - origin[1]) / cell_size + 1))
    k1 = max(0, int((z1 - origin[2]) / cell_size))
    k2 = min(nz, int((z2 - origin[2]) / cell_size + 1))

    index_set = itertools.product( range(k1, k2), range(j1, j2), range(i1, i2) )
    for k, j, i in index_set:
        print(i,j,k)
        #check if cell center is inside radius of fracture
        center = [origin[0] + i * cell_size + 0.5*cell_size,
                origin[1] + j * cell_size + 0.5*cell_size,
                origin[2] + k * cell_size + 0.5*cell_size]
        
        if x1 < center[0] < x2 and y1 < center[1] < y2 and z1 < center[2] < z2:
            local_center = center - translation
            #rotate cell center coordinates to xyz of fracture
            rotate_center = np.dot(local_center, M[:3, :3])
            #calculate r^2 of cell center in xy of fracture (fracture lies in z=0 plane)
            rsq_cell = np.square(rotate_center[0]) + np.square(
            rotate_center[1])
            if rsq_cell < np.square(xrad):
                #center is in radius, so check if fracture intersects cell
                #find z of cell corners in xyz of fracture
                corners = get_corner(origin, i,j,k, cell_size)
                max_z = 0.
                min_z = 0.
                for corner in corners:
                    rotate_corner = np.dot(corner - translation, M[:3, :3])
                    if rotate_corner[2] > max_z:
                        max_z = rotate_corner[2]
                    elif rotate_corner[2] < min_z:
                        min_z = rotate_corner[2]
                    #and store min and max values of z at corners
                    if min_z < 0. and max_z > 0.:  #fracture lies in z=0 plane
                        #fracture intersects that cell
                        index = i + nx * j + nx * ny * k
                        #   store number of fractures that intersect cell
                        cell_fracture_id[index].append(f + 1)
                        # increase count
                        fracture[index][0] += 1
                        if fracture[index][0] > 19: 
                            print(f'Number of fractures in cell ({index}) exceeds allotted memory.')
                            return
                        # gather fracture indices 
                        fracture[index][fracture[index][0]] = f + 1
    return fracture, cell_fracture_id 