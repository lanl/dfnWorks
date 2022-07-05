"""
Function to compute new DFN apertures w/ stress
"""
import numpy as np
import math as m
import os
import sys

# Function input is 3x3 tensor
def compute_new_apertures(sigma_mat):
    """ Takes stress tensor as input (defined in dfn run file) and calculates
    new apertures based on Bandis equations.

    Parameters
    __________
        sigma_mat : array
            3 x 3 stress tensor (units in Pa)

    Returns
    _______
        aperture.dat : file
            New apertures
        perm.dat : file
            New permeabilities based on cubic law from new apertures

    Notes
    _____
        None
    
    """
    print("--> Starting")
    ## BEGINNING OF USER DEFINED PARAMETERS
    phi = 25.0 # Friction angle
    psi = 5 # Dilation angle
    u_cs = 0.003 # Critical shear displacement
    eta = 0.92 # Geometric coefficient
    G = 10.e9 # Shear modulus
    min_ap = 1e-6 # Minimum aperture
    kfrac = 10.e9 # Fracture stiffness (Pa/m)
    ## END OF USER DEFINED PARAMETERS
    # Input data:
    aperture = np.genfromtxt('aperture.dat',skip_header=1)[:,-1]
    normals = np.genfromtxt('normal_vectors.dat',skip_header=0)
    radii_frac = np.genfromtxt('radii_Final.dat',skip_header=2)[:,0]
    print(np.mean(aperture))
    new_ap=np.zeros(len(aperture))

    for i in range(len(aperture)):
        # Magnitude of normal stress
        sigma_mag = sigma_mat[0][0]*(normals[i][0])**2 + \
                    sigma_mat[1][1]*(normals[i][1])**2 + \
                    sigma_mat[2][2]*(normals[i][2])**2 + \
                    2*(sigma_mat[0][1]*normals[i][0]*normals[i][1] + \
                    sigma_mat[1][2]*normals[i][1]*normals[i][2] + \
                    sigma_mat[0][2]*normals[i][0]*normals[i][2]); 
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
        tau = np.sqrt(max(0,stress_sqr-(sigma_mag)**2))
        # Critical normal stress (see Zhao et al. 2013 JRMGE)
        sigma_nc = (0.487*aperture[i]*1e6+2.51)*1e6 
        # Normal displacement
        u_n = (9*sigma_mag*aperture[i])/(sigma_nc+10*sigma_mag)
        # Shear dilation
        tau_critical = -sigma_mag*m.tan(m.radians(phi))
        l = radii_frac[i] # Fracture half length?  
        krock = eta*G/l
        ks1 = kfrac + krock 
        ks2 = krock
        if tau > tau_critical: 
            u_s = (tau-tau_critical*(1-ks2/ks1))/(ks2)
        else:
            u_s = 0
        u_d = min(u_s,u_cs)*m.tan(m.radians(psi))
        new_ap[i] = aperture[i] - u_n + u_d 
        #print(i,normals[i][:],aperture[i],new_ap[i])
    diff = (new_ap - aperture)**2
    print("--> L2 change in apertures : %0.2e"%(np.sqrt(diff.sum())))
    return new_ap 

def dump_new_aperture_and_perm(new_ap):
    print("--> Dumping out new apertures and perms")
    os.remove('aperture.dat')
    faperture = open("aperture.dat",'w')
    faperture.write('aperture\n')
    for i in range(len(new_ap)):
        faperture.write('-%d 0 0 %0.5e\n'%(i+7, new_ap[i]))
    faperture.close()

    # Perm is based on the cubic law
    new_perm = new_ap**2/12
    
    os.remove('perm.dat')
    fperm = open("perm.dat",'w')
    fperm.write('permeability\n')
    for i in range(len(new_ap)):
        fperm.write('-%d 0 0 %0.5e %0.5e %0.5e\n'%(i+7, new_perm[i], new_perm[i], new_perm[i]))
    fperm.close()
    print("--> Complete")

print("Computing new apertures based on provided stress tensor")
s1 = float(sys.argv[1])
s2 = float(sys.argv[2])
s3 = float(sys.argv[3])
print("s1: %0.2e s2: %0.2e s3 %0.2e"%(s1,s2,s3))
with open("stress.dat","w") as fp:
    fp.write("s1: %0.2e\ns2: %0.2e\ns3 %0.2e"%(s1,s2,s3))

x=[[s1,0,0],[0,s2,0],[0,0,s3]]

new_ap = compute_new_apertures(x)
dump_new_aperture_and_perm(new_ap)


