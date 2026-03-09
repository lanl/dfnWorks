"""
:synopsis: Example demonstrating hydraulic property distributions for fracture families
:version: 2.9.8
:maintainer: Jeffrey Hyman
:date: January 23, 2026

.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

Example: Hydraulic Property Distributions
=========================================

This example demonstrates the different hydraulic property distributions
available in dfnWorks for assigning aperture, permeability, or transmissivity
to fracture families.

Four fracture families are created, each using a different distribution:

1. Log-normal (uncorrelated): Values drawn from a log-normal distribution
   Parameters: mu (mean), sigma (log-variance)

2. Exponential (uncorrelated): Values drawn from an exponential distribution  
   Parameters: lam (rate parameter, mean = 1/lam)

3. Correlated: Power-law relationship with fracture radius
   Formula: aperture = alpha * radius^beta
   Parameters: alpha (coefficient), beta (exponent)

4. Semi-correlated: Power-law with log-normal perturbation
   Formula: log(aperture) = log(alpha * radius^beta) + sqrt(sigma) * N(0,1)
   Parameters: alpha (coefficient), beta (exponent), sigma (log-variance of noise)

Reference:
    Hyman et al. (2016) "Fracture size and transmissivity correlations: 
    Implications for transport simulations in sparse three-dimensional 
    discrete fracture networks following a truncated power law distribution 
    of fracture size" Water Resources Research.
"""

from pydfnworks import *
import os
import matplotlib.pyplot as plt
import numpy as np 


# =============================================================================
# Setup paths and initialize DFN object
# =============================================================================
src_path = os.getcwd()
jobname = src_path + "/output"

DFN = DFNWORKS(jobname,
               ncpu=8)

# =============================================================================
# Domain parameters
# =============================================================================
DFN.params['domainSize']['value'] = [25, 25, 25]  # 10m x 10m x 10m domain
DFN.params['h']['value'] = 0.1                     # Mesh resolution
DFN.params['stopCondition']['value'] = 1           # Stop by fracture count
DFN.params['disableFram']['value'] = True 

# ==========================D===================================================
# Fracture Family 1: Log-normal aperture distribution
# -----------------------------------------------------------------------------
# Apertures are drawn from a log-normal distribution independent of fracture
# size. Useful when aperture variability is high and not correlated with size.
# =============================================================================
DFN.add_fracture_family(
    shape="rect",
    distribution="exp",
    exp_mean=3.0,
    min_radius=1.0,
    max_radius=10.0,
    kappa=10.0,
    theta=0.0,
    phi=0.0,
    aspect=1.0,
    p32=2.5,
    hy_variable='aperture',
    hy_function='log-normal',
    hy_params={
        "mu": 1e-4,      # Mean aperture [m]
        "sigma": 0.5     # Log-variance
    }
)

# =============================================================================
# Fracture Family 2: Exponential aperture distribution
# -----------------------------------------------------------------------------
# Apertures are drawn from an exponential distribution with rate parameter lam.
# The mean aperture is 1/lam. Produces a memoryless distribution where small
# apertures are most common.
# =============================================================================
DFN.add_fracture_family(
    shape="rect",
    distribution="exp",
    exp_mean=3.0,
    min_radius=1.0,
    max_radius=10.0,
    kappa=10.0,
    theta=90.0,
    phi=0.0,
    aspect=1.0,
    p32=2.5,
    hy_variable='aperture',
    hy_function='exponential',
    hy_params={
        "lam": 1e4       # Rate parameter [1/m], mean = 1e-4 m
    }
)

# =============================================================================
# Fracture Family 3: Correlated aperture (power-law with radius)
# -----------------------------------------------------------------------------
# Aperture scales with fracture radius via a power-law relationship:
#   b = alpha * r^beta
# Larger fractures have larger apertures, consistent with geomechanical models.
# =============================================================================
DFN.add_fracture_family(
    shape="rect",
    distribution="exp",
    exp_mean=3.0,
    min_radius=1.0,
    max_radius=10.0,
    kappa=10.0,
    theta=0.0,
    phi=90.0,
    aspect=1.0,
    p32=2.5,
    hy_variable='aperture',
    hy_function='correlated',
    hy_params={
        "alpha": 1e-5,   # Coefficient [m^(1-beta)]
        "beta": 0.5      # Exponent [-]
    }
)

# =============================================================================
# Fracture Family 4: Semi-correlated aperture (power-law with noise)
# -----------------------------------------------------------------------------
# Combines the correlated model with log-normal variability:
#   log(b) = log(alpha * r^beta) + sqrt(sigma) * N(0,1)
# Captures both size-dependence and natural heterogeneity.
# =============================================================================
DFN.add_fracture_family(
    shape="rect",
    distribution="exp",
    exp_mean=3.0,
    min_radius=1.0,
    max_radius=10.0,
    kappa=10.0,
    theta=90.0,
    phi=90.0,
    aspect=1.0,
    p32=2.5,
    hy_variable='aperture',
    hy_function='semi-correlated',
    hy_params={
        "alpha": 1e-5,   # Coefficient [m^(1-beta)]
        "beta": 0.5,     # Exponent [-]
        "sigma": 1.0     # Log-variance of perturbation
    }
)

# =============================================================================
# Run workflow
# =============================================================================
DFN.make_working_directory(delete=True)

DFN.print_domain_parameters()
DFN.check_input()
DFN.create_network()
DFN.output_report() 
# DFN.mesh_network()
# DFN.dump_hydraulic_values()
# DFN.add_variable_to_mesh('Permeability', 'perm.dat', 'reduced_mesh.inp')
# DFN.add_variable_to_mesh('Aperture', 'aperture.dat', 'reduced_mesh.inp')

### 


# =============================================================================
# Plot aperture distributions by family
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes = axes.flatten()

family_labels = [
    "Family 1: Log-normal",
    "Family 2: Exponential",
    "Family 3: Correlated",
    "Family 4: Semi-correlated"
]

colors =['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

for i, ax in enumerate(axes):
    family_id = i + 1
    idx = np.where(DFN.families == family_id)[0]
    apertures = DFN.aperture[idx]
    
    ax.hist(apertures * 1e4, bins=20, density=True, alpha=0.7, 
            color=colors[i], edgecolor='black', linewidth=0.5)
    ax.set_xlabel(r'Aperture [$\times 10^{-4}$ m]')
    ax.set_ylabel('Probability Density')
    ax.set_title(family_labels[i])
    
    # Add statistics
    mean_val = np.mean(apertures)
    std_val = np.std(apertures)
    ax.text(0.95, 0.95, f'$\mu$ = {mean_val:.2e} m\n$\sigma$ = {std_val:.2e} m',
            transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.suptitle('Aperture Distributions by Fracture Family', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('aperture_distributions.png', dpi=150, bbox_inches='tight')
plt.close()

print("--> Aperture distribution plot saved to 'aperture_distributions.png'")
