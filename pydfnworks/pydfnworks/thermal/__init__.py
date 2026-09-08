"""
pydfnworks.thermal
==================

Heat extraction from fractured rock for hydraulic-fracture spacing
optimization. Two backends share the heat_extraction() interface

    heat_extraction(spacing, m_dot, T_res, T_inj, rock_props, fluid_props,
                    n_fractures, fracture_height, t_eval) -> Q(t) [W]

so an optimizer written against one can be pointed at the other by
changing only its dispatch:

    mpf_gringarten.heat_extraction  Phase 1 analytic surrogate (Gringarten
                                    et al. 1975 multiple parallel fractures),
                                    tens of microseconds per call. Default.
    dfn_heat.heat_extraction        Phase 2 DFN graph-transport backend.
                                    Interface only in this version; raises
                                    NotImplementedError.

optimize_spacing() searches the spacing that maximizes a user-supplied
objective(t, Q); cumulative_heat() and time_to_drawdown() are provided.
"""

from pydfnworks.thermal import mpf_gringarten, dfn_heat
from pydfnworks.thermal.common import GRANITE_PROPS, WATER_PROPS, SECONDS_PER_YEAR
from pydfnworks.thermal.mpf_gringarten import heat_extraction, production_temperature
from pydfnworks.thermal.dfn_heat import thermal_to_tdrw_parameters
from pydfnworks.thermal.optimize_spacing import (optimize_spacing,
                                                 cumulative_heat,
                                                 time_to_drawdown)

BACKENDS = {
    "mpf_gringarten": mpf_gringarten.heat_extraction,
    "dfn_heat": dfn_heat.heat_extraction,
}
DEFAULT_BACKEND = "mpf_gringarten"


def get_backend(name=DEFAULT_BACKEND):
    """ Return a heat_extraction() backend by name

    Parameters
    ----------
        name : str
            "mpf_gringarten" (default) or "dfn_heat"

    Returns
    -------
        backend : callable
            function with the heat_extraction() signature
    """
    try:
        return BACKENDS[name]
    except KeyError:
        raise ValueError(
            f"Unknown thermal backend '{name}'. Options: {tuple(BACKENDS)}")
