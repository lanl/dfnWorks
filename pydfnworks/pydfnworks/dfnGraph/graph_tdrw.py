import numpy as np
from scipy import special
import mpmath as mp
import os 

from pydfnworks.general.logging import local_print_log
import pydfnworks.dfnGraph.tdrw_finite_roubinet as roubinet  
import pydfnworks.dfnGraph.tdrw_finite_dentz as dentz
import pydfnworks.dfnGraph.tdrw_finite_annulus as annulus
import pydfnworks.dfnGraph.tdrw_finite_from_file as from_file


# Valid finite matrix diffusion models that require fracture_spacing
_FINITE_MODELS_REQUIRING_SPACING = ("roubinet", "dentz", "annulus")


def _check_tdrw_params(matrix_porosity, matrix_diffusivity, fracture_spacing, tdrw_model, tdrw_filename):
    """ Check that the provided tdrw values are physical

    Parameters
    ----------
        matrix_porosity : float
            Porosity of the rock matrix [-]

        matrix_diffusivity : float
            Effective diffusivity of the rock matrix [m^2/s]

        fracture_spacing : float
            Characteristic matrix block half-width / fracture spacing [m]
            Required for finite matrix models.

        tdrw_model : str
            Name of the TDRW matrix diffusion model. Valid options:
            'infinite', 'roubinet', 'dentz', 'annulus', 'from_file'.

        tdrw_filename : str or None
            Path to CDF file, required when tdrw_model == 'from_file'.

    Returns
    -------
        None

    Notes
    -----
        Logs errors and warnings via local_print_log. Does not raise
        exceptions; callers should treat logged errors as fatal.
    """
    local_print_log("\n* TDRW for Matrix Diffusion is ON.")

    # --- Matrix Porosity ---
    if matrix_porosity is None:
        local_print_log("Error: Requested TDRW but no value for matrix_porosity was provided.", "error")
    elif not (0 <= matrix_porosity <= 1):
        local_print_log(
            f"Error: Requested TDRW but matrix_porosity={matrix_porosity} is outside the valid range [0, 1].",
            "error"
        )
    else:
        local_print_log(f"--> Matrix porosity value: {matrix_porosity:.2f} [-]")

    # --- Matrix Diffusivity ---
    if matrix_diffusivity is None:
        local_print_log("Error: Requested TDRW but no value for matrix_diffusivity was provided.", "error")
    elif matrix_diffusivity <= 0:
        local_print_log(f"Error: Non-positive matrix_diffusivity={matrix_diffusivity}. Exiting program.", "error")
    else:
        local_print_log(f"--> Matrix diffusivity value: {matrix_diffusivity:.2e} [m^2/s]")

    # --- TDRW Model Selection ---
    if tdrw_model is None:
        local_print_log("Warning: No TDRW model specified; default behavior may apply.", "warning")

    elif tdrw_model == "infinite":
        local_print_log("--> Using infinite matrix diffusion model (no fracture spacing required).")

    elif tdrw_model in _FINITE_MODELS_REQUIRING_SPACING:
        local_print_log(f"--> Using {tdrw_model.capitalize()} model for finite matrix diffusion.")
        # --- Fracture Spacing Check ---
        if fracture_spacing is None:
            local_print_log(
                f"Error: TDRW model '{tdrw_model}' requires a fracture_spacing value, but none was provided.",
                "error"
            )
        elif fracture_spacing <= 0:
            local_print_log(f"Error: Non-positive fracture_spacing={fracture_spacing}. Exiting program.", "error")
        else:
            local_print_log(f"--> Fracture spacing value: {fracture_spacing:.2e} [m]")

        if tdrw_model == "annulus":
            local_print_log("--> Annulus geometry: absorbing boundary at fracture-matrix interface, reflecting boundary at block interior.")

    elif tdrw_model == "from_file":
        if tdrw_filename is None:
            local_print_log("Error. TDRW Filename not provided.", "error")
        elif not os.path.isfile(tdrw_filename):
            local_print_log(f"Error. File not found: {tdrw_filename}", "error")
        else:
            local_print_log(f"--> Sampling matrix diffusion time from: {tdrw_filename}.")

    else:
        local_print_log(
            f"Error: Unknown TDRW model '{tdrw_model}'. Valid options are 'infinite', 'roubinet', 'dentz', 'annulus', or 'from_file' (case-sensitive).",
            "error"
        )

    local_print_log("")  # clean trailing newline   


def _set_up_limited_matrix_diffusion(G,
                                     tdrw_model,
                                     fracture_spacing,
                                     matrix_porosity,
                                     matrix_diffusivity,
                                     eps=1e-16,
                                     num_pts=100,
                                     tdrw_filename=None):
    """ Sets up transition probabilities for limited block size matrix diffusion

    Parameters
    ----------
        G : networkX graph
            Graph provided by graph_flow modules

        tdrw_model : str
            Name of the TDRW matrix diffusion model. Valid options:
            'roubinet', 'dentz', 'annulus', 'from_file'.

        fracture_spacing : float
            Characteristic matrix block half-width [m].
            Required for 'roubinet', 'dentz', and 'annulus' models.

        matrix_porosity : float
            Matrix porosity [-]

        matrix_diffusivity : float
            Matrix diffusivity [m^2/s]

        eps : float
            Small parameter for Roubinet model. Default 1e-16.

        num_pts : int
            Number of points in the logspace CDF table. Default 100.

        tdrw_filename : str or None
            Path to CDF file, required when tdrw_model == 'from_file'.

    Returns
    -------
        transfer_time : np.ndarray or None
            Array of dimensionless diffusion return times for inverse CDF lookup.

        trans_prob : np.ndarray or None
            Array of cumulative probabilities corresponding to transfer_time.

    Notes
    -----
        The returned arrays are used with np.interp to map uniform random
        samples to return times during particle transport. See
        limited_matrix_diffusion_* functions in each model module.
    """
    if tdrw_model == 'roubinet':
        b_min, b_max, tf_min, tf_max = roubinet.get_aperture_and_time_limits(G)
        trans_prob = roubinet.transfer_probabilities(b_min, b_max, tf_min, tf_max,
                                                     matrix_porosity, matrix_diffusivity,
                                                     fracture_spacing, eps, num_pts)
        transfer_time = fracture_spacing**2 / (2 * matrix_diffusivity)

    elif tdrw_model == "dentz":
        transfer_time, trans_prob = dentz._make_inverse_cdf_spline_for_times()

    elif tdrw_model == "annulus":
        # annulus model: absorbing wall at fracture-matrix interface,
        # reflecting wall at block interior; eps fixed inside the module
        transfer_time, trans_prob = annulus._make_inverse_cdf_annulus(num_samples=num_pts)

    elif tdrw_model == "from_file":
        transfer_time, trans_prob = from_file._load_finite_time_cdf(tdrw_filename)

    else:
        trans_prob = None
        transfer_time = None

    return transfer_time, trans_prob
