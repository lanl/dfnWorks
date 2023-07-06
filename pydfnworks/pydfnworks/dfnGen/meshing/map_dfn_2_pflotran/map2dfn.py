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

   Modified by Rosie Leone (rleone@sandia.gov) Dec 16, 2021 to have permAniso() apply
   a stair step correction factor to the ECPM when conditional set to True
'''

import time
import numpy as np
import transformations as tr
from h5py import File
import math as m


def readEllipse(radiifile='radii_Final.dat',
                normalfile='normal_vectors.dat',
                transfile='translations.dat'):
    '''Read dfnWorks-Version2.0 output files describing radius, orientation, and
     location of fractures in space.
     Subsequent methods assume elliptical (in fact circular) fractures.
     Return a list of dictionaries describing each ellipse.
  '''
    ellipses = []
    with open(radiifile, 'r') as f:
        radii = f.readlines()  #two lines to get rid of at top of file
    radii.pop(0)
    radii.pop(0)
    with open(normalfile, 'r') as f:
        normals = f.readlines()  #no lines to get rid of at top of file
    with open(transfile, 'r') as f:
        temp = f.readlines()  #one line to get rid of at top of file
    temp.pop(0)
    translations = []
    for line in temp:
        if line.split()[-1] != 'R':
            translations.append(line)
    print(len(radii))
    print(len(normals))
    print(len(translations))
    for i in range(len(radii)):
        ellipses.append({
            'normal': np.zeros((3), dtype=np.float),
            'translation': np.zeros((3), dtype=np.float),
            'xrad': 0.0,
            'yrad': 0.0
        })
        ellipses[i]['normal'][0] = float(normals[i].split()[0])
        ellipses[i]['normal'][1] = float(normals[i].split()[1])
        ellipses[i]['normal'][2] = float(normals[i].split()[2])
        ellipses[i]['translation'][0] = float(translations[i].split()[0])
        ellipses[i]['translation'][1] = float(translations[i].split()[1])
        ellipses[i]['translation'][2] = float(translations[i].split()[2])
        ellipses[i]['xrad'] = float(radii[i].split()[0])
        ellipses[i]['yrad'] = float(radii[i].split()[1])

    return ellipses


def readApertures(aperturefile='aperture.dat'):
    '''Read dfnWorks-Version2.0 output files describing fracture aperture.
     Return numpy array containing aperture for each fracture.
  '''
    apertures = np.loadtxt(aperturefile)
    return apertures


def readPerms(permfile='perm.dat'):
    '''Read dfnWorks-Version2.0 output files describing fracture aperture.
     Return numpy array containing permeability for each fracture.
  '''
    perms = np.loadtxt(permfile)
    return perms


def findT(apertures, perms):
    """ Take as arguments numpy arrays for apertures, perms, and return 
  numpy array of transmissivities."""
    return apertures * perms


def map_dfn(ellipses, origin, nx, ny, nz, d):
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
    ncell = nx * ny * nz
    nfrac = len(ellipses)
    fracture = np.zeros((ncell, 20), dtype=np.int)

    t0 = time.time()
    # mod = nfrac/10
    for f in range(nfrac):
        #   if f%mod == 0:
        print('Mapping ellipse %i of %i.' % (f, nfrac))
        tnow = time.time() - t0
        print('Time elapsed in map_dfn() = %f.' % (tnow))
        normal = ellipses[f]['normal']
        translation = ellipses[f]['translation']
        xrad = ellipses[f]['xrad']
        yrad = ellipses[f]['yrad']
        #calculate rotation matrix for use later in rotating coordinates of nearby cells
        direction = np.cross([0, 0, 1], normal)
        #cosa = np.dot([0,0,1],normal)/(np.linalg.norm([0,0,1])*np.linalg.norm(normal)) #frobenius norm = length
        #above evaluates to normal[2], so:
        angle = np.arccos(normal[2])  # everything is in radians
        M = tr.rotation_matrix(angle, direction)
        #find fracture in domain coordinates so can look for nearby cells
        if xrad > yrad:
            x1 = translation[0] - xrad
            x2 = translation[0] + xrad
            y1 = translation[1] - xrad
            y2 = translation[1] + xrad
            z1 = translation[2] - xrad
            z2 = translation[2] + xrad
        else:  #this else is misleading because script only works on circles
            x1 = translation[0] - yrad
            x2 = translation[0] + yrad
            y1 = translation[1] - yrad
            y2 = translation[1] + yrad
            z1 = translation[2] - yrad
            z2 = translation[2] + yrad
        #find indices of nearby cells so don't have to check all of them!
        i1 = max(0, int((x1 - origin[0]) / d))  #round down
        i2 = min(nx, int((x2 - origin[0]) / d + 1))  #round up
        j1 = max(0, int((y1 - origin[1]) / d))
        j2 = min(ny, int((y2 - origin[1]) / d + 1))
        k1 = max(0, int((z1 - origin[2]) / d))
        k2 = min(nz, int((z2 - origin[2]) / d + 1))
        for k in range(k1, k2):  #for cells close to fracture
            for j in range(j1, j2):
                for i in range(i1, i2):
                    #check if cell center is inside radius of fracture
                    center = [
                        origin[0] + i * d + d / 2., origin[1] + j * d + d / 2.,
                        origin[2] + k * d + d / 2.
                    ]
                    if center[0] > x1 and center[0] < x2 and center[
                            1] > y1 and center[1] < y2 and center[
                                2] > z1 and center[2] < z2:
                        local_center = center - translation
                        #rotate cell center coordinates to xyz of fracture
                        rotate_center = np.dot(local_center, M[:3, :3])
                        #calculate r^2 of cell center in xy of fracture (fracture lies in z=0 plane)
                        rsq_cell = np.square(rotate_center[0]) + np.square(
                            rotate_center[1])
                        if rsq_cell < np.square(xrad):
                            #center is in radius, so check if fracture intersects cell
                            #find z of cell corners in xyz of fracture
                            corner = [[
                                origin[0] + i * d, origin[1] + j * d,
                                origin[2] + k * d
                            ],
                                      [
                                          origin[0] + (i + 1) * d,
                                          origin[1] + j * d, origin[2] + k * d
                                      ],
                                      [
                                          origin[0] + (i + 1) * d,
                                          origin[1] + (j + 1) * d,
                                          origin[2] + k * d
                                      ],
                                      [
                                          origin[0] + i * d,
                                          origin[1] + (j + 1) * d,
                                          origin[2] + k * d
                                      ],
                                      [
                                          origin[0] + i * d, origin[1] + j * d,
                                          origin[2] + (k + 1) * d
                                      ],
                                      [
                                          origin[0] + (i + 1) * d,
                                          origin[1] + j * d,
                                          origin[2] + (k + 1) * d
                                      ],
                                      [
                                          origin[0] + (i + 1) * d,
                                          origin[1] + (j + 1) * d,
                                          origin[2] + (k + 1) * d
                                      ],
                                      [
                                          origin[0] + i * d,
                                          origin[1] + (j + 1) * d,
                                          origin[2] + (k + 1) * d
                                      ]]
                            maxz = 0.
                            minz = 0.
                            for c in range(len(corner)):
                                rotate_corner = np.dot(corner[c] - translation,
                                                       M[:3, :3])
                                if rotate_corner[2] > maxz:
                                    maxz = rotate_corner[2]
                                elif rotate_corner[2] < minz:
                                    minz = rotate_corner[2]
                            #and store min and max values of z at corners
                            if minz < 0. and maxz > 0.:  #fracture lies in z=0 plane
                                #fracture intersects that cell
                                index = i + nx * j + nx * ny * k
                                fracture[index][
                                    0] += 1  #store number of fractures that intersect cell
                                if fracture[index][0] > 19:
                                    print(
                                        'Number of fractures in cell %d exceeds allotted memory.'
                                        % index)
                                    return
                                fracture[index][fracture[index][0]] = f + 1

    return fracture


def porosity(fracture, apertures, d, bulk_por):
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
    ncell = fracture.shape[0]
    porosity = np.zeros((ncell), '=f8')
    for i in range(ncell):
        if fracture[i][0] == 0:
            porosity[i] = bulk_por
        else:  #there are fractures in this cell
            for j in range(1, fracture[i][0] + 1):
                fracnum = fracture[i][j]
                porosity[i] += apertures[
                    fracnum -
                    1] / d  #aperture is 0 indexed, fracture numbers are 1 indexed

    t1 = time.time()
    print('Time spent in porosity() = %f.' % (t1 - t0))

    return porosity


def permIso(fracture, T, d, k_background):
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
    ncell = fracture.shape[0]
    k_iso = np.full((ncell), k_background, '=f8')
    for i in range(ncell):
        if fracture[i][0] != 0:
            for j in range(1, fracture[i][0] + 1):
                fracnum = fracture[i][j]
                k_iso[i] += T[
                    fracnum -
                    1] / d  #T is 0 indexed, fracture numbers are 1 indexed

    t1 = time.time()
    print('Time spent in permIso() = %f.' % (t1 - t0))

    return k_iso


def permAniso(fracture,
              ellipses,
              T,
              d,
              k_background,
              LUMP=0,
              out_dir='./',
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
    nfrac = len(ellipses)
    if nfrac != len(T):
        print(
            'ellipses and transmissivity contain different numbers of fractures'
        )
        return

    ellipseT = np.zeros((nfrac, 3), '=f8')
    fullTensor = []
    T_local = np.zeros((3, 3), dtype=np.float)
    t0 = time.time()
    #calculate transmissivity tensor in domain coordinates for each ellipse
    for f in range(nfrac):
        normal = ellipses[f]['normal']
        direction = np.cross(normal, [0, 0, 1])
        angle = np.arccos(normal[2])
        M = tr.rotation_matrix(angle, direction)
        Transpose = np.transpose(M[:3, :3])
        T_local[0, 0] = T[f]
        T_local[1, 1] = T[f]
        #permeability = 0 in local z direction of fracture
        T_domain = np.dot(np.dot(M[:3, :3], T_local), Transpose)
        ellipseT[f][0:3] = [T_domain[0, 0], T_domain[1, 1], T_domain[2, 2]]
        fullTensor.append(T_domain)
    t1 = time.time()
    print('time spent calculating fracture transmissivity %f' % (t1 - t0))

    #in case you were wondering what those off-diagonal terms are:
    t0 = time.time()
    #fout=file('Ttensor.txt','w')
    fout = open(out_dir + 'Ttensor.txt', 'w')
    for f in range(len(fullTensor)):
        fout.write(str(fullTensor[f]))
        fout.write('\n\n')
    fout.close()
    t1 = time.time()
    print('time spent writing fracture transmissivity %f' % (t1 - t0))

    #calculate cell effective permeability by adding fracture k to background k
    t0 = time.time()
    ncells = fracture.shape[0]
    maxfrac = fracture.shape[1]
    k_aniso = np.full((ncells, 3), k_background, '=f8')
    for i in range(ncells):
        if fracture[i][0] != 0:
            for j in range(1, fracture[i][0] + 1):
                fracnum = fracture[i][j]
                if LUMP:  #lump off diagonal terms
                    #because symmetrical doesn't matter if direction of summing is correct, phew!
                    k_aniso[i][0] += np.sum(fullTensor[fracnum - 1][0, :3]) / d
                    k_aniso[i][1] += np.sum(fullTensor[fracnum - 1][1, :3]) / d
                    k_aniso[i][2] += np.sum(fullTensor[fracnum - 1][2, :3]) / d
                else:  #discard off diagonal terms (default)
                    k_aniso[i][0] += ellipseT[fracnum - 1][
                        0] / d  #ellipseT is 0 indexed, fracture numbers are 1 indexed
                    k_aniso[i][1] += ellipseT[fracnum - 1][1] / d
                    k_aniso[i][2] += ellipseT[fracnum - 1][2] / d

            if correction_factor:
                #correction factor Sweeney et al. 2019 from upscale.py

                min_n1 = 1e6
                min_n2 = 1e6
                min_n3 = 1e6

                for j in range(1, fracture[i][0] + 1):
                    fracnum = fracture[i][j]
                    normal = ellipses[fracnum - 1]['normal']
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

                k_aniso[i][0] *= cf_x
                k_aniso[i][1] *= cf_y
                k_aniso[i][2] *= cf_z

            ########
    t1 = time.time()
    print('time spent summing cell permeabilities %f' % (t1 - t0))

    return k_aniso


def count_stuff(filename='mapELLIPSES.txt'):
    '''Mapping DFN to ECPM can result in false connections when non-intersecting
     fractures happen to intersect the same cell of the ECPM.
     Make sweeping assumption that cells with 3 or more fractures in them
     are more likely than cells with 2 fractures in them to contain a false
     connection and count them as such.
     Return counts of 1) total number of cells, 2) number of (active) cells 
     containing fractures, 3) number of cells containing 3 or more fractures.
     
     (This method could more efficiently use the fracture array returned by
      map_dfn().)
  '''
    fin = file(filename, 'r')
    cellcount = 0
    count0 = 0
    count1 = 0
    count2 = 0
    count3 = 0
    morethan4 = 0
    for line in fin:
        if line.startswith('#'):
            continue
        elif int(line.split()[3]) == 0:
            cellcount += 1
            count0 += 1
        elif int(line.split()[3]) == 1:
            cellcount += 1
            count1 += 1
        elif int(line.split()[3]) == 2:
            cellcount += 1
            count2 += 1
        elif int(line.split()[3]) == 3:
            cellcount += 1
            count3 += 1
        elif int(line.split()[3]) >= 4:
            cellcount += 1
            morethan4 += 1
    print('\n')
    print('Information for %s ' % filename)
    print('Total number of cells in grid %i' % cellcount)
    print('Number of cells containing fractures %i' % (cellcount - count0))
    print('Percent active cells %.1f' %
          (100. * (float(cellcount) - float(count0)) / float(cellcount)))
    print('Number of cells containing 1 fracture %i' % (count1))
    print('Number of cells containing 2 fractures %i' % (count2))
    print('Number of cells containing 3 fractures %i' % (count3))
    print('Number of cells containing 4 or more fractures %i' % (morethan4))
    print('Possible false connections %i (cells containing >= 3 fractures)' %
          (count3 + morethan4))
    fin.close()
    count = {
        'cells': cellcount,
        'active': (cellcount - count0),
        'false': (count3 + morethan4)
    }

    return count
