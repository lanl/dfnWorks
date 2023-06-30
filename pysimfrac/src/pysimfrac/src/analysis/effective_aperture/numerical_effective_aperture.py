import numpy as np
from pysimfrac.src.general.helper_functions import print_error


def build_matrix(nrows, ncolumns, h, k, direction='x'):
    """ Builds linear system for pressure with dirichlet conditions along the x-direction

    Parameters
    ----------------
        nrows : int

        ncolumns : int

        h : float

        k : 2D - numpy array
            Permeability field, size nrows x ncolumns

        direction : string
            x/y primary direction of flow

    Returns 
    ----------------
        A : 2D - numpy array
            Linear system size of nrows*ncolumns, nrows*ncolumns 
        b : 1D - numpy array
            RHS of Ax = b

    Notes
    -------------------
        Uses reflective BTC for laterial boundaries
    
    
    """
    A = np.zeros((nrows * ncolumns, nrows * ncolumns))
    b = np.zeros(nrows * ncolumns)
    for i in range(nrows * ncolumns):
        iy = int(
            i % nrows
        )  #;    // % is the "modulo operator", the remainder of i / width;
        ix = int(i / nrows)  #;    // where "/" is an integer division

        ## Check flow direction to build matrix.
        if direction == 'x':
            # print(f'row {iy} / col {ix}')
            if ix > 0 and ix < ncolumns - 1 and iy > 0 and iy < nrows - 1:
                A[i, i] = -4 * k[iy, ix]
                A[i, i - nrows] = k[iy, ix - 1]
                A[i, i + nrows] = k[iy, ix + 1]
                A[i, i - 1] = k[iy - 1, ix]
                A[i, i + 1] = k[iy + 1, ix]

            ##
            elif ix == 0:
                # print(f'row {iy} / col {ix} - left boundary')
                A[i, i] = 1
                b[i] = 2

            elif ix == ncolumns - 1:
                # print(f'row {iy} / col {ix} - right boundary')
                A[i, i] = 1
                b[i] = 1

            elif iy == 0:
                # print(f'row {iy} / col {ix} - bottom boundary')
                A[i, i] = -4 * k[iy, ix]
                A[i, i - nrows] = k[iy, ix - 1]
                A[i, i + nrows] = k[iy, ix + 1]
                # A[i, i - 1] = k[iy - 1, ix]
                A[i, i + 1] = 2 * k[iy + 1, ix]

            elif iy == nrows - 1:
                # print(f'row {iy} / col {ix} - top boundary')
                A[i, i] = -4 * k[iy, ix]
                A[i, i - nrows] = k[iy, ix - 1]
                A[i, i + nrows] = k[iy, ix + 1]
                A[i, i - 1] = 2 * k[iy - 1, ix]
                # A[i, i + 1] = k[iy + 1, ix]
        elif direction == 'y':
            # print(f'row {iy} / col {ix}')
            if ix > 0 and ix < ncolumns - 1 and iy > 0 and iy < nrows - 1:
                A[i, i] = -4 * k[iy, ix]
                A[i, i - nrows] = k[iy, ix - 1]
                A[i, i + nrows] = k[iy, ix + 1]
                A[i, i - 1] = k[iy - 1, ix]
                A[i, i + 1] = k[iy + 1, ix]

            elif iy == 0:
                # print(f'row {iy} / col {ix} - bottom boundary')
                A[i, i] = 1
                b[i] = 2

            elif iy == nrows - 1:
                # print(f'row {iy} / col {ix} - top boundary')
                A[i, i] = 1
                b[i] = 1

            elif ix == 0:
                # print(f'row {iy} / col {ix} - left boundary')
                A[i, i] = -4 * k[iy, ix]
                # A[i, i - nrows] = k[iy, ix - 1]
                A[i, i + nrows] = 2 * k[iy, ix + 1]
                A[i, i - 1] = k[iy - 1, ix]
                A[i, i + 1] = k[iy + 1, ix]

            elif ix == ncolumns - 1:
                # print(f'row {iy} / col {ix} - bottom boundary')
                A[i, i] = -4 * k[iy, ix]
                A[i, i - nrows] = 2 * k[iy, ix - 1]
                # A[i, i + nrows] = k[iy, ix + 1]
                A[i, i - 1] = k[iy - 1, ix]
                A[i, i + 1] = k[iy + 1, ix]

        else:
            print_error('--> Unknown direction for effective perm flow.')

    return A, b


def get_darcy_velocity(p, k, nrows, ncolumns, h):
    """ Compute Darcy velocity in the domain using pressure and permeability
    
    Parameters
    ----------------
        p : 2D numpy array
            pressure field (nrows x ncolumns)

        k : 2D numpy array
            permeability field (nrows x ncolumns) 

        nrows : int 
            number of rows in permeability field

        ncolumns : int 
            number of columns in permeability field 

        h : float 
            discretization length 

    Returns
    ----------------
        u : 2D numpy array
            u/x velocity field 
        v : 2D numpy array
            v/y velocity field 

    Notes
    ----------------
        q = -k/mu \grad P
    """
    mu = 8.9e-4  # dynamic viscosity of water
    i2h = 1 / (2 * h)
    ih = 1 / h
    u = np.zeros((nrows, ncolumns))
    v = np.zeros((nrows, ncolumns))

    for i in range(nrows):
        for j in range(ncolumns):
            if i > 0 and i < nrows - 1 and j > 0 and j < ncolumns - 1:
                u[i, j] = -k[i, j] * (p[i, j + 1] - p[i, j - 1]) * i2h
                v[i, j] = -k[i, j] * (p[i + 1, j] - p[i - 1, j]) * i2h

            ## corners - first order derviative
            if i == 0 and j == 0:
                u[i, j] = -k[i, j] * (p[i, j + 1] - p[i, j]) * ih
                v[i, j] = -k[i, j] * (p[i + 1, j] - p[i, j]) * ih

            elif i == 0 and j == ncolumns - 1:
                u[i, j] = -k[i, j] * (p[i, j] - p[i, j - 1]) * ih
                v[i, j] = -k[i, j] * (p[i + 1, j] - p[i, j]) * ih

            elif i == nrows - 1 and j == 0:
                u[i, j] = -k[i, j] * (p[i, j + 1] - p[i, j]) * ih
                v[i, j] = -k[i, j] * (p[i, j] - p[i - 1, j]) * ih

            elif i == nrows - 1 and j == ncolumns - 1:
                u[i, j] = -k[i, j] * (p[i, j] - p[i, j - 1]) * ih
                v[i, j] = -k[i, j] * (p[i, j] - p[i - 1, j]) * ih

            ## edges - first order in the direction of the edge
            elif i == 0:
                u[i, j] = -k[i, j] * (p[i, j + 1] - p[i, j - 1]) * i2h
                v[i, j] = -k[i, j] * (p[i + 1, j] - p[i, j]) * ih

            elif i == nrows - 1:
                u[i, j] = -k[i, j] * (p[i, j + 1] - p[i, j - 1]) * i2h
                v[i, j] = -k[i, j] * (p[i, j] - p[i - 1, j]) * ih

            elif j == 0:
                u[i, j] = -k[i, j] * (p[i, j + 1] - p[i, j]) * ih
                v[i, j] = -k[i, j] * (p[i + 1, j] - p[i - 1, j]) * i2h

            elif j == ncolumns - 1:
                u[i, j] = -k[i, j] * (p[i, j] - p[i, j - 1]) * ih
                v[i, j] = -k[i, j] * (p[i + 1, j] - p[i - 1, j]) * i2h

    return u, v


def get_effective_perm(u, v, lx, ly, h, nrows, ncolumns, direction):
    ## I don't know why we need this subtraction of h.
    ## but we get the wrong answer without it. JDH 24- jan 2023
    if direction == 'x':
        delta_p = 1.0 / (lx - h)
        q = np.zeros(ncolumns)
        for i in range(ncolumns):
            q[i] = np.mean(u[:, i])
        keff = np.mean(q / delta_p)
        beff = np.sqrt(12.0 * keff)

    elif direction == "y":
        delta_p = 1.0 / (ly - h)
        q = np.zeros(nrows)
        for i in range(nrows):
            q[i] = np.mean(v[i, :])
        keff = np.mean(q / delta_p)
        beff = np.sqrt(12.0 * keff)
    return keff, beff


def solve_darcy_equation(nrows, ncolumns, h, aperture, lx, ly):
    """ Sets up a linear system for pressure via the Laplace equation. Solves for Pressure, then computes the Darcy velocity. Inverts that for the effective perm, and then back to the effective aperture. 
    
    Parameters
    ----------------
        nrows : int 
            number of rows in permeability field

        ncolumns : int 
            number of columns in permeability field 

        h : float 
            discretization length 

        aperture : 2D numpy array
            2D projected aperture field (nrows x ncolumns) 

        lx : float 
            length of domain in x-direction 

        ly : float
            length of the domain in y-direction 

    Returns
    -----------------          
        keff_xx : float 
            Effective permeability in the x direction with dx gradient 

        beff_xx : float 
            Effective aperture in the x direction with dx gradient 
        
        keff_yy : float 
            Effective permeability in the y direction with dy gradient 

        beff_yy : float 
            Effective aperture in the y direction with dy gradient 

    Notes 
    -----------------
        Lots of assumptions baked into here. But, it's a start for a numerical approximation. 

    """

    # First, we convert aperture to permability using a local cubic law.
    perm = (aperture**2) / 12
    print('--> Building matrix - dx')
    A, b = build_matrix(nrows, ncolumns, h, perm, 'x')
    print('--> Linear solve')
    p = np.linalg.solve(A, b)
    ## weird python re-indexing thing
    p = p.reshape(ncolumns, nrows).T
    print('--> Getting velocity')
    u, v = get_darcy_velocity(p, perm, nrows, ncolumns, h)
    print('--> Computing effective permeability')
    keff_xx, beff_xx = get_effective_perm(u, v, lx, ly, h, nrows, ncolumns,
                                          'x')

    print('--> Building matrix - dy')
    A, b = build_matrix(nrows, ncolumns, h, perm, 'y')
    print('--> Linear solve')
    p = np.linalg.solve(A, b)
    ## weird python re-indexing thing
    p = p.reshape(ncolumns, nrows).T
    print('--> Getting velocity')
    u, v = get_darcy_velocity(p, perm, nrows, ncolumns, h)
    print('--> Computing effective permeability')
    keff_yy, beff_yy = get_effective_perm(u, v, lx, ly, h, nrows, ncolumns,
                                          'y')

    return keff_xx, beff_xx, keff_yy, beff_yy


def numerical_effective_aperture(self):
    """ Estimates the effective aperture of the fracture by solving the Darcy flow equations using a Laplace equation for pressure in 2-dimensions. The projected 2D aperture field is converted to permeability field using the local cubic law. 
    
    k = b^2 /12

    Then the pressure field is obtained using second order finite difference scheme for the Laplace equation. 
    
    nabla \cdot (k (bar{x}) nabla p) = 0

    The Darcy velocity is obtained using this solution 

    q = -k/mu grad p

    Then, Darcy's law is inverted to obtain the effective permeability

    keff = -(q \mu)/grad p

    and the effective aperture is 

    beff = sqrt(12*keff)
    
    Parameters
    -----------------
        self : simfrac object

    Returns
    -------------
        None
        
    Notes
    ------------
        mu drops out and we don't actualy use it for numerical stability. 

    """

    print(
        "--> Estimating effective aperture via Laplace's equation and Darcy's law in a 2D aperture field"
    )
    kxx, bxx, kyy, byy = solve_darcy_equation(self.ny, self.nx, self.h,
                                              self.aperture, self.lx, self.ly)

    print(f'--> Effective aperture bxx : {bxx:0.2e} {self.units} ')
    print(f'--> Effective permeability kxx : {kxx:0.2e} {self.units}^2')
    print(f'--> Effective aperture byy : {byy:0.2e} {self.units}')
    print(f'--> Effective permeability kyy : {kyy:0.2e} {self.units}^2')
    print(f'\n[{bxx:0.2e} {0.0:0.2e}]')
    print(f'[{0.0:0.2e} {byy:0.2e}]\n')
    tmp = {'kxx': kxx, 'bxx': bxx, 'kyy': kyy, 'byy': byy}
    self.effective_aperture.update({'numerical': tmp})
