"""
.. module:: dfn_heat.py
   :synopsis: Phase 2 DFN-based, particle-consistent heat-extraction
              backend. In v0 only the interface is implemented.
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

Notes
-----
    Plan. The Phase 2 backend reuses the graph transport machinery in
    pydfnworks.dfnGraph.transport.graph_transport.run_graph_transport(),
    which already implements time-domain random walk (TDRW) exchange with
    a finite matrix slab (tdrw_model='dentz', block half-width
    fracture_spacing/2) using the same Stehfest inversion as the Phase 1
    surrogate. Heat obeys the same fracture/matrix equations as a solute
    with the substitutions listed in thermal_to_tdrw_parameters(), so the
    finite-slab return-time kernel does not need a second implementation:
    the thermal run is a call to run_graph_transport() with the mapped
    parameters. What remains (deferred past v0) is the thermal post-
    processing: converting the particle arrival-time distribution at the
    production well into T_out(t) and Q(t) (the tracer-to-thermal mapping
    of Shook 2001), including the per-fracture flow partition from the
    graph flow solution rather than the equal split assumed by the
    surrogate.

    Sampler cost at thermal diffusivity. The finite-slab models sample
    matrix excursions as Poisson trapping events at a rate
    gamma = 2 phi_m D_m / (b eps B) per unit advective time (see
    tdrw/trapping.py; b is the edge aperture, B the slab half-width, eps
    the release position, 1e-4 by default). With the thermal mapping
    phi_m D_m is about 7e-7 m^2/s, some 1e7 times the solute value, so a
    particle with an advective time of 1e3 s undergoes of order 1e6 to
    1e7 excursions and a single particle takes minutes. The Phase 2
    backend therefore has to sample the total slab retention time per
    edge from the finite-slab kernel directly (one draw per edge, as the
    'infinite' model does with its closed-form kernel) rather than event
    by event; the infinite model runs 200 particles in well under a
    second on the graph_transport example DFN. Until then the finite
    tdrw models should not be run with thermal parameters at production
    particle counts.

    heat_extraction() here accepts the same nine positional arguments as
    the Phase 1 backend, validates them identically, and raises
    NotImplementedError. That lets an optimizer be pointed at either
    backend without an interface change once Phase 2 is ready.

    References
        Shook, G. M. (2001). Predicting thermal breakthrough in
        heterogeneous media from tracer tests. Geothermics 30(6), 573-589.
"""

from pydfnworks.dfnGraph.transport.tdrw import FINITE_MODELS
from pydfnworks.thermal.common import (check_heat_extraction_inputs,
                                       check_props, thermal_diffusivity,
                                       volumetric_heat_capacity, ROCK_KEYS,
                                       FLUID_KEYS)

NOT_IMPLEMENTED_MESSAGE = (
    "pydfnworks.thermal.dfn_heat.heat_extraction: the Phase 2 DFN-based "
    "heat kernel (particle arrival times -> T_out(t), Q(t)) is not "
    "implemented in this version. The interface is final; use "
    "pydfnworks.thermal.mpf_gringarten.heat_extraction (Phase 1 analytic "
    "surrogate) until the finite-slab thermal post-processing lands.")


def thermal_to_tdrw_parameters(rock_props, fluid_props):
    """ Map thermal properties onto the TDRW parameters of run_graph_transport()

    Parameters
    ----------
        rock_props : dict
            {"rho": kg/m^3, "c": J/kg/K, "k": W/m/K}

        fluid_props : dict
            {"rho": kg/m^3, "c": J/kg/K}

    Returns
    -------
        tdrw : dict
            "matrix_porosity"    (rho c)_rock / (rho c)_fluid [-]
            "matrix_diffusivity" k / (rho c)_rock, the rock thermal
                                 diffusivity [m^2/s]

    Notes
    -----
        Solute transport in a fracture with matrix diffusion balances the
        fracture concentration c against the matrix flux phi_m D_m dc/dz.
        Conductive heat exchange balances the fluid energy (rho c)_f T
        against the rock flux k dT/dz = (rho c)_r alpha dT/dz. Dividing by
        (rho c)_f puts the thermal problem in solute form with

            phi_m -> (rho c)_r / (rho c)_f,   D_m -> alpha = k / (rho c)_r

        so the TDRW exchange parameter phi_m sqrt(D_m) / b becomes
        sqrt(k (rho c)_r) / ((rho c)_f b), the Lauwerier group. The finite
        slab models take fracture_spacing unchanged. For granite and water
        the porosity-like ratio is about 0.5, inside the [0, 1] range
        enforced by check_tdrw_params().
    """
    check_props(rock_props, ROCK_KEYS, "rock_props")
    check_props(fluid_props, FLUID_KEYS, "fluid_props")
    return {
        "matrix_porosity":
        volumetric_heat_capacity(rock_props) /
        volumetric_heat_capacity(fluid_props),
        "matrix_diffusivity":
        thermal_diffusivity(rock_props),
    }


def heat_extraction(spacing,
                    m_dot,
                    T_res,
                    T_inj,
                    rock_props,
                    fluid_props,
                    n_fractures,
                    fracture_height,
                    t_eval,
                    *,
                    dfn=None,
                    G=None,
                    nparticles=10**4,
                    tdrw_model="dentz",
                    initial_positions="flux",
                    **transport_kwargs):
    """ Heat extraction rate Q(t) from DFN graph transport (Phase 2, stub)

    Parameters
    ----------
        spacing, m_dot, T_res, T_inj, rock_props, fluid_props, n_fractures,
        fracture_height, t_eval :
            same meaning and units as in
            pydfnworks.thermal.mpf_gringarten.heat_extraction(). spacing
            is passed to run_graph_transport() as fracture_spacing.

        dfn : DFNWORKS object or None
            keyword-only. DFN whose graph is used.

        G : NetworkX graph or None
            keyword-only. Flow graph from run_graph_flow() between the
            injection and production wells.

        nparticles : int
            keyword-only. Number of particles. Default 10**4.

        tdrw_model : str
            keyword-only. Finite matrix diffusion model for the rock
            slabs; one of pydfnworks.dfnGraph.transport.tdrw.FINITE_MODELS.
            Default 'dentz'.

        initial_positions : str
            keyword-only. 'flux' (default) or 'uniform', see
            run_graph_transport().

        transport_kwargs :
            further keyword arguments forwarded to run_graph_transport()

    Returns
    -------
        Q : numpy array
            heat extraction rate at each time in t_eval [W]

    Notes
    -----
        v0 validates the arguments (raising ValueError for the same bad
        inputs as the Phase 1 backend) and then raises
        NotImplementedError; see the module notes for what is left.
    """
    check_heat_extraction_inputs(spacing, m_dot, T_res, T_inj, rock_props,
                                 fluid_props, n_fractures, fracture_height,
                                 t_eval)
    if tdrw_model not in FINITE_MODELS:
        raise ValueError(
            f"tdrw_model must be a finite matrix model {FINITE_MODELS}, got '{tdrw_model}'"
        )
    if int(nparticles) < 1:
        raise ValueError(f"nparticles must be >= 1, got {nparticles}")

    tdrw = thermal_to_tdrw_parameters(rock_props, fluid_props)
    detail = (
        f" Planned call: run_graph_transport(G, nparticles={int(nparticles)}, "
        f"tdrw_flag=True, tdrw_model='{tdrw_model}', "
        f"matrix_porosity={tdrw['matrix_porosity']:.3e}, "
        f"matrix_diffusivity={tdrw['matrix_diffusivity']:.3e}, "
        f"fracture_spacing={spacing:.3e}, initial_positions='{initial_positions}').")
    if dfn is None or G is None:
        detail += " A DFNWORKS object (dfn=) and a flow graph (G=) will be required."
    raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE + detail)
