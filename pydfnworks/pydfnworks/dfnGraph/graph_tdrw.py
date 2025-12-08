import numpy as np
from scipy import special
import mpmath as mp

from pydfnworks.general.logging import local_print_log
import pydfnworks.dfnGraph.tdrw_finite_roubinet as roubinet  
import pydfnworks.dfnGraph.tdrw_finite_dentz as dentz

def _check_tdrw_params(matrix_porosity, matrix_diffusivity, fracture_spacing, tdrw_model):
    """ Check that the provided tdrw values are physiscal


    Parameters
    ----------
        G: NetworkX graph 
            Directed Graph obtained from output of graph_flow

    Returns
    -------
        dict : nested dictionary.

    Notes
    -----
        dict[n]['child'] is a list of vertices downstream to vertex n
        dict[n]['prob'] is a list of probabilities for choosing a downstream node for vertex n
    
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
    elif tdrw_model in ("roubinet", "dentz"):
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
    else:
        local_print_log(
            f"Error: Unknown TDRW model '{tdrw_model}'. Valid options are 'infinite', 'roubinet', or 'dentz' (case-sensitive).",
            "error"
        )

    local_print_log("")  # clean trailing newline   
    
def _set_up_limited_matrix_diffusion(G,tdrw_model,
                                    fracture_spacing,
                                    matrix_porosity,
                                    matrix_diffusivity,
                                    eps=1e-16,
                                    num_pts=100):
    """ Sets up transition probabilities for limited block size matrix diffusion
    
    Parameters
    ---------------------
        G : networkX graph  
            Graph provided by graph_flow modules

        fracture_length : float
            Length of the current edge segment in the graph [m]

        matrix_porosity: float
            Matrix Porosity 

        matrix_diffusivity : float
            Matrix Diffusivity value  [m^2/s]

        eps : float 
            Default - 1e-16

        num_pts : int 
            Number of points in the logspace array between t_min and t_max
 

    Returns
    -------------
        trans_prob : dictionary 
            Dictionary elements
            times : np.array
                Array of diffusion times 
            prob_cdf : np.array
                Array of cummulative probabilities. They only go to 0.5

    Notes
    --------------------
        None

    """
    if tdrw_model == 'roubinet':
        # local_print_log("Using Roubinet Model for finite Matrix Diffusion")
        b_min, b_max, tf_min, tf_max = roubinet.get_aperture_and_time_limits(G)
        trans_prob = roubinet.transfer_probabilities(b_min, b_max, tf_min, tf_max,
                                            matrix_porosity, matrix_diffusivity,
                                            fracture_spacing, eps, num_pts)
        transfer_time = fracture_spacing**2 / (2 * matrix_diffusivity)
    elif tdrw_model == "dentz":
        # local_print_log("Using Dentz Model for finite Matrix Diffusion") 
        transfer_time, trans_prob = dentz._make_inverse_cdf_spline_for_times()
    else:
        trans_prob = None
        transfer_time = None

    return transfer_time, trans_prob
