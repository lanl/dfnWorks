'''
   mapdfn2pflotran.py

   Call methods in mapdfn.py to take output of dfnWorks-Version2.0, create
   equivalent continuous porous medium representation, and write parameters
   (permeability, porosity, tortuosity) to files for use with PFLOTRAN.

   Usage: Edit values for origin, nx, ny, nz, d, k_background, bulk_por,
          tortuosity factor, and h5origin.
          Paths and filenames are hardwired and may also need to be checked.
          As written, they assume script is being called from a subdirectory.
          Then: python mapdfn2pflotran.py

   Dependencies: mapdfn.py
                 numpy
                 h5py

   Author: 

   Date: 07/13/18
   SAND Number: SAND2018-7605 O

'''
import time

from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_upscale import mapdfn_porosity, mapdfn_perm_iso, mapdfn_perm_aniso
from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_io import write_h5_files
from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_helper_functions import setup_output_dir, setup_domain
from pydfnworks.dfnGen.meshing.mapdfn_ecpm.mapdfn_cell_area import mapdfn_cell_weights
from pydfnworks.general.logging import initialize_log_file, print_log


def mapdfn_ecpm(self,
                matrix_perm,
                matrix_porosity,
                cell_size,
                matrix_on=False,
                tortuosity_factor=0.001,
                lump_diag_terms=False,
                correction_factor=False,
                output_dir="mapdfn_ecpm",
                cell_area="flat"):
    """ This script takes the top-level directory of the dfn and maps it to an ecpm, saving the ecpm files in that directory
  
    Parameters
    -----------------
        self : dfnWorks object
        
        matrix_perm : float
            permeability of the matrix cells without fratures 

        cell_size : float
            The cell size (meters) to use for the meshing

        matrix_on : bool
            Default is False

        tortuosity_factor : float

        lump_diag_terms : bool
            If True, sum each row of the fracture transmissivity tensor
            (including off-diagonal terms) onto the diagonal. Default is False,
            which keeps only the diagonal.

        correction_factor : boolean
            Apply the stair-step correction of Sweeney et al. (2019) to the
            anisotropic permeability. For each axis, the factor ranges from 1
            (fracture normal aligned with or perpendicular to the axis) to
            2*sqrt(2) (normal at 45 degrees), using the fracture in the cell
            whose normal is closest to 45 degrees. Only applied with
            cell_area = "flat". Default is False: the mapping tags every cell
            the fracture plane passes through, so the flat-cut mapping already
            overestimates conductance, and the correction increases it further.

        output_dir : string
            output directory

        cell_area : string
            How much of each tagged cell a fracture is assumed to cover.
            "flat" (default) treats every fracture as a full cut across the
            cell face (area d**2). "normal" weights each fracture by the mean
            plane--cube section area ``d**2 / ||n||_1``. "section" uses the exact
            area of the fracture plane inside each cell, computed from the
            fracture normal and the cell-center offset. For "normal" and
            "section" the correction_factor is not applied.

        
    Returns
    -----------------
        None

    Authors
    -----------------
        Emily Stein (ergiamb@sandia.gov)
        Applied Systems Analysis and Research, 8844
        Sandia National Laboratories
    
        Edited by Teresa Portone (tporton@sandia.gov) 11/2020 to take arguments.

        Rosie Leone 

        Jeffrey Hyman 07/2023 - Integration with pydfnWorks 

    Notes
    -----------------


    """
    self.print_log("\n")
    self.print_log('=' * 80)
    self.print_log("* Starting MAPDFN - ECPM")
    self.print_log('=' * 80)

    # setup the domain
    filenames = setup_output_dir(output_dir, self.jobname)
    domain_center = [
        self.params['domainCenter']['value'][0],
        self.params['domainCenter']['value'][1],
        self.params['domainCenter']['value'][2]
    ]
    origin, h5origin, nx, ny, nz, num_cells = setup_domain(
        self.domain, domain_center, cell_size)

    # id cells that intersect the DFN
    cell_fracture_id = self.mapdfn_tag_cells(origin, num_cells, nx, ny, nz,
                                             cell_size)

    # fracture-cell area weights (None keeps the flat-cut mapping)
    cell_fracture_weight = None
    if cell_area != "flat":
        if correction_factor:
            self.print_log(
                f"--> Warning: correction_factor is calibrated for the flat-cut mapping and is not applied with cell_area = '{cell_area}'",
                'warning')
            correction_factor = False
        cell_fracture_weight = mapdfn_cell_weights(self, cell_fracture_id,
                                                   origin, nx, ny, cell_size,
                                                   cell_area)

    porosity, k_iso, k_aniso = self.mapdfn_upscale(num_cells, cell_fracture_id,
                                                   cell_size, matrix_porosity,
                                                   matrix_perm,
                                                   lump_diag_terms,
                                                   correction_factor,
                                                   cell_fracture_weight)

    # write evereything to files
    write_h5_files(filenames, nx, ny, nz, cell_size, cell_fracture_id, k_iso,
                   k_aniso, porosity, matrix_perm, tortuosity_factor,
                   matrix_on, h5origin)

    self.print_log('=' * 80)
    self.print_log("* MAPDFN Complete")
    self.print_log('=' * 80)
    self.print_log("\n")
