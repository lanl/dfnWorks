"""
Hydraulic properties module for dfnWorks.

This module provides functions for generating, converting, and writing
hydraulic properties (aperture, permeability, transmissivity) for discrete
fracture networks.
"""

# Conversion utilities
from .conversions import (
    get_units,
    check_key,
    load_fractures,
    convert,
)

# Distribution generators
from .distributions import (
    log_normal,
    exponential,
    correlated,
    semi_correlated,
    constant,
    DISTRIBUTIONS,
)

# File I/O
from .io import (
    dump_aperture,
    dump_perm,
    dump_transmissivity,
    dump_fracture_info,
    dump_hydraulic_values,
)

# DFN class methods
from .dfn_methods import (
    set_fracture_hydraulic_values,
    generate_hydraulic_values,
)

__all__ = [
    # Conversions
    'get_units',
    'check_key',
    'load_fractures',
    'convert',
    # Distributions
    'log_normal',
    'exponential',
    'correlated',
    'semi_correlated',
    'constant',
    'DISTRIBUTIONS',
    # I/O
    'dump_aperture',
    'dump_perm',
    'dump_transmissivity',
    'dump_fracture_info',
    'dump_hydraulic_values',
    # DFN methods
    'set_fracture_hydraulic_values',
    'generate_hydraulic_values',
]
