
import math as m
import numpy as np

# from pydfnworks
from pydfnworks.dfnGen.generation.hydraulic_properties import convert

def stress_based_apertures(self,
                           sigma_mat,
                           friction_angle=24.9,
                           dilation_angle=5,
                           critical_shear_displacement=0.003,
                           shear_modulus=34.1e9,
                           min_b=1e-10,
                           shear_stiffness=434e9):
    """ Takes stress tensor as input (defined in dfn run file) and calculates new apertures based on Bandis equations. New aperture and permeability values are written to files.


    Parameters
    ----------------------
        sigma_mat : array
            3 x 3 stress tensor (units in Pa)
        friction_angle : float
            Friction angle (Degrees)
        dilation_angle : float
            Dilation angle (Degrees)
        critical_shear_displacement : float
            Critical shear displacement
        shear_modulus : float 
            Shear modulus (Pa)
        min_b : float
             Minimum aperture (m)
        shear_stiffness : float 
            Shear stiffness (Pa/m)

    Returns
    ----------------------
        None

    Notes
    ----------------------

        For details of implementation see 
        
        "Sweeney, Matthew Ryan, and J. D. Hyman. "Stress effects on flow and transport in three‐dimensional fracture networks." Journal of Geophysical Research: Solid Earth 125.8 (2020): e2020JB019754."

        and 

        Baghbanan, Alireza, and Lanru Jing. "Stress effects on permeability in a fractured rock mass with correlated fracture length and aperture." International journal of rock mechanics and mining sciences 45.8 (2008): 1320-1334.

        and

        Zhao, Zhihong, et al. "Impact of stress on solute transport in a fracture network: A comparison study." Journal of Rock Mechanics and Geotechnical Engineering 5.2 (2013): 110-123.

    """
    print("--> Computing aperture based on stress tensor")
    print("\n--> Stress Tensor (Pa):\n")
    print(
        f"\t{sigma_mat[0][0]:0.2e} {sigma_mat[0][1]:0.2e} {sigma_mat[0][2]:0.2e}"
    )
    print(
        f"\t{sigma_mat[1][0]:0.2e} {sigma_mat[1][1]:0.2e} {sigma_mat[1][2]:0.2e}"
    )
    print(
        f"\t{sigma_mat[2][0]:0.2e} {sigma_mat[2][1]:0.2e} {sigma_mat[2][2]:0.2e}"
    )
    print()

    # write stress to file.
    with open("stress.dat", "w") as fstress:
            fstress.write(
                f"\t{sigma_mat[0][0]:0.2e} {sigma_mat[0][1]:0.2e} {sigma_mat[0][2]:0.2e}"
            )
            fstress.write(
                f"\t{sigma_mat[1][0]:0.2e} {sigma_mat[1][1]:0.2e} {sigma_mat[1][2]:0.2e}"
            )
            fstress.write(
                f"\t{sigma_mat[2][0]:0.2e} {sigma_mat[2][1]:0.2e} {sigma_mat[2][2]:0.2e}"
            )


    # read fracture data:
    initial_aperture = np.genfromtxt(self.aper_file, skip_header=1)[:, -1]
    normals = np.genfromtxt('normal_vectors.dat', skip_header=0)
    radii_frac = np.genfromtxt('radii_Final.dat', skip_header=2)[:, 0]
    num_frac = len(initial_aperture)
    b = np.zeros(num_frac)

    # Cycle through fractures and compute new aperture base on stress field and user defined parameters
    for i in range(num_frac):
        # Magnitude of normal stress
        sigma_mag = sigma_mat[0][0]*(normals[i][0])**2 + \
                    sigma_mat[1][1]*(normals[i][1])**2 + \
                    sigma_mat[2][2]*(normals[i][2])**2 + \
                    2*(sigma_mat[0][1]*normals[i][0]*normals[i][1] + \
                    sigma_mat[1][2]*normals[i][1]*normals[i][2] + \
                    sigma_mat[0][2]*normals[i][0]*normals[i][2])

        T_1 = sigma_mat[0][0]*normals[i][0] + \
              sigma_mat[0][1]*normals[i][1] + \
              sigma_mat[0][2]*normals[i][2]

        T_2 = sigma_mat[1][0]*normals[i][0] + \
              sigma_mat[1][1]*normals[i][1] + \
              sigma_mat[1][2]*normals[i][2]

        T_3 = sigma_mat[2][0]*normals[i][0] + \
              sigma_mat[2][1]*normals[i][1] + \
              sigma_mat[2][2]*normals[i][2]
              
        stress_sqr = (T_1)**2 + (T_2)**2 + (T_3)**2
        # Magnitude of shear stress
        shear_stress = np.sqrt(max(0, stress_sqr - (sigma_mag)**2))
        # Critical normal stress (see Zhao et al. 2013 JRMGE)
        sigma_nc = (0.487 * initial_aperture[i] * 1e6 + 2.51) * 1e6
        # Normal displacement
        normal_displacement = (9 * sigma_mag * initial_aperture[i]) / (sigma_nc +
                                                       10 * sigma_mag)
        # Shear dilation
        shear_stress_critical = -sigma_mag * m.tan(m.radians(friction_angle))
        # Fracture half length
        l = radii_frac[i]
        
        # rock stiffness
        rock_stiffness = 0.92 * shear_modulus / l
        ks1 = shear_stiffness + rock_stiffness
        ks2 = rock_stiffness
        # 
        if shear_stress > shear_stress_critical:
            dilation_tmp = (shear_stress - shear_stress_critical * (1 - ks2 / ks1)) / (ks2)
        else:
            dilation_tmp = 0

        dilation = min(dilation_tmp, critical_shear_displacement) * m.tan(m.radians(dilation_angle))

        # take the max of the computed and provided minimum aperture.
        b[i] = max(min_b, initial_aperture[i] - normal_displacement + dilation)

    diff = abs(b - initial_aperture)
    diff2 = diff**2
    print(f"--> L2 change in apertures {np.sqrt(diff.sum()):0.2e}")
    print(f"--> Maximum change in apertures {max(diff):0.2e}")

    k = convert(b, 'aperture', 'permeability')
    T = convert(b, 'aperture', 'transmissivity')

    self.dump_hydraulic_values(b, k, T, prefix='stress')

    print("--> Computing aperture based on stress field complete ")
