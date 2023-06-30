#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from pysimfrac.src.general.helper_functions import print_warning

def pad(self, target_size):
    """
    

    Parameters
    ----------
    target_size : TYPE
        DESCRIPTION.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    None.

    """

    voxels_needed = target_size - self.frac_3D.shape[-1]

    if voxels_needed < 0:
        raise ValueError(
            f'Target size {target_size} is smaller than voxelized fracture {self.frac_3D.shape[-1]}'
        )

    self.frac_3D = np.pad(
        self.frac_3D,
        ((0, 0), (0, 0),
         (voxels_needed // 2, voxels_needed // 2 + voxels_needed % 2)),
        'constant')


def voxelize(self, solid_voxels=5):
    """
    

    Parameters
    ----------
    solid_voxels : TYPE, optional
        DESCRIPTION. The default is 5.

    Returns
    -------
    None.

    """

    import numpy.lib.index_tricks as ndi

    self.aperture_check()  # check that there are no negative apertures
    self.reset_bottom()  # push the negative values to 0

    # add solid voxels so the fracture is lined
    z_size = np.ceil(self.top.max() + solid_voxels)

    if z_size > 512:
        print_warning('The size of the array might be too big')
        if z_size > 2058:
            ValueError(f'Target size {z_size} is too big')

    # size of our 3D array
    size_3D = (*self.top.shape, int(z_size))
    flat_frac = np.zeros(np.prod(size_3D))

    # array of positional indices
    inds = np.arange(np.prod(size_3D)).reshape(size_3D)

    ind_top = np.ceil(self.top + solid_voxels // 2).astype(int)
    ind_bottom = np.ceil(self.bottom + solid_voxels // 2).astype(int)

    max_ap = (ind_top - ind_bottom).max()
    for i in range(max_ap):
        """
        loop through the fracture aperture to select the void voxels
        
        source for alternative to np.choose:
        https://numpy.org/doc/stable/reference/generated/numpy.choose.html
        """

        ind_layer = ind_bottom + i
        ind_layer[ind_layer > ind_top] = 0

        ind_1D = np.array([
            inds.T[ind_layer[I]][(I[1], I[0])]
            for I in ndi.ndindex(ind_layer.shape)
        ])
        flat_frac[ind_1D] = 1

    self.frac_3D = flat_frac.reshape(size_3D)
    self.frac_3D[:, :, 0] = 0
