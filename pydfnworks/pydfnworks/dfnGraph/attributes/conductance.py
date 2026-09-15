"""
.. module:: conductance.py
   :synopsis: Edge conductance (weight) models for graph flow.

The edge ``weight`` used by the graph-flow Laplacian is the hydraulic
conductance of the fracture flowing surface represented by that edge.
``add_weight`` dispatches to a selectable model:

* ``"karra"`` (default) -- Karra et al. (2018), ``w = K*A/L``.
* ``"doolaeghe"`` -- Doolaeghe et al. (2020) size-aware trapezoid conductance
  with the multiple-paths correction (added in a later phase).
"""

import math

import networkx as nx

from pydfnworks.general.logging import local_print_log, print_log

# registered conductance models (name -> callable(G)); populated below.
CONDUCTANCE_MODELS = {}


def _karra_conductance(G):
    """Karra et al. (2018) edge conductance: ``w = K*A/L``.

    Parameters
    ----------
        G : NetworkX Graph
            graph whose edges carry 'perm' (K), 'area' (A), and 'length' (L)

    Returns
    -------
        None
    """
    for u, v in nx.edges(G):
        if G.edges[u, v]['length'] > 0:
            G.edges[u, v]['weight'] = G.edges[u, v]['perm'] * G.edges[
                u, v]['area'] / G.edges[u, v]['length']


CONDUCTANCE_MODELS["karra"] = _karra_conductance


def _trapezoid_term(D, l):
    """One trapezoid term ln(D/l)/(D-l) from Doolaeghe et al. (2020) Eq 16.

    The l -> D limit of ln(D/l)/(D-l) is 1/D; use it to avoid a 0/0.
    """
    if l <= 0:
        return 0.0
    if abs(D - l) < 1e-12 * max(D, 1.0):
        return 1.0 / D
    return math.log(D / l) / (D - l)


def _doolaeghe_raw_conductance(G, B=1.5):
    """Uncorrected Doolaeghe et al. (2020) trapezoid conductance per edge (Eq 16).

    Returns a dict {(u, v): C} of raw conductances and a dict {frac: [(u, v), ...]}
    grouping edges by fracture. Edges with degenerate geometry fall back to the
    Karra form. Does not write to the graph.
    """
    raw = {}
    frac_edges = {}
    for u, v in nx.edges(G):
        x = G.edges[u, v]['length']
        if x <= 0:
            continue
        if 'diameter' not in G.edges[u, v]:
            local_print_log(
                "Error. doolaeghe conductance requires edge 'diameter' "
                "(call add_diameter first).", 'error')
            return None, None
        T = G.edges[u, v]['perm'] * G.edges[u, v]['b']
        l_u = G.nodes[u]['length']
        l_v = G.nodes[v]['length']
        D = G.edges[u, v]['diameter']
        # close-intersection adjustment (Eqs 17-18)
        D_hat = min(D, 0.5 * (l_u + l_v) + B * x)
        term = _trapezoid_term(D_hat, l_u) + _trapezoid_term(D_hat, l_v)
        if term <= 0:
            # degenerate geometry; fall back to the Karra form for this edge
            C = G.edges[u, v]['perm'] * G.edges[u, v]['area'] / x
        else:
            C = (2.0 * T / x) / term
        raw[(u, v)] = C
        frac_edges.setdefault(G.edges[u, v]['frac'], []).append((u, v))
    return raw, frac_edges


def _doolaeghe_conductance(G, B=1.5, mp_correction="divide"):
    """Doolaeghe et al. size-aware conductance with a multiple-paths correction.

    The base conductance is the trapezoid form (Doolaeghe et al. 2020 Eq 16)
    with the close-intersection adjustment (Eqs 17-18). Because an n-intersection
    fracture forms an n-clique in the intersection graph, the edge conductances
    are then corrected for the redundant paths via ``mp_correction``:

    * ``"divide"`` (default) -- 2020 Eq 20: ``Chat = C / (n_i - 1)``.
    * ``"additive"`` -- 2021 Eq 11: per fracture ``F = (sum(C) - max(C))/(n_i - 1)``
      then ``Chat = max(0, C - F)``. This is an adaptation of the 2021 result,
      which the authors derived on an idealized single-fracture (one source,
      N-1 sinks) setup and noted is not yet fully generalized to DFN graphs.
    * ``"none"`` -- no correction (raw trapezoid conductance).

    where T_i = perm*aperture is the fracture transmissivity, x the distance
    between intersection centers (edge 'length'), l_j/l_k the intersection sizes
    (node 'length'), D_i the fracture diameter (edge 'diameter'), and n_i the
    number of intersections on fracture i.

    Requires 'diameter' on edges (see attributes.perm_area.add_diameter).

    Parameters
    ----------
        G : NetworkX Graph
            intersection graph with 'perm', 'b', 'length', 'frac', 'diameter'
            on edges and 'length', 'frac' on nodes

        B : float
            close-intersection coefficient (Eq 18); Doolaeghe et al. use ~1.5

        mp_correction : str
            multiple-paths correction: 'divide' (default), 'additive', or 'none'

    Returns
    -------
        None
    """
    raw, frac_edges = _doolaeghe_raw_conductance(G, B=B)
    if raw is None:
        return

    # number of intersections on each fracture
    n_int = {}
    for _, d in G.nodes(data=True):
        frac = d.get('frac')
        if frac is None:
            continue
        for f in frac:
            if isinstance(f, int):
                n_int[f] = n_int.get(f, 0) + 1

    if mp_correction == "none":
        for (u, v), C in raw.items():
            G.edges[u, v]['weight'] = C
    elif mp_correction == "divide":
        for frac, elist in frac_edges.items():
            n_i = n_int.get(frac, 2)
            denom = (n_i - 1) if n_i > 1 else 1
            for (u, v) in elist:
                G.edges[u, v]['weight'] = raw[(u, v)] / denom
    elif mp_correction == "additive":
        local_print_log(
            "--> Warning: mp_correction='additive' (2021 F(N)) is experimental "
            "and does not generalize to heterogeneous DFN cliques; it can yield "
            "near-zero bottleneck conductances and off-scale transport. Prefer "
            "'divide' or the deconstructed graph (simplify=True).", 'warning')
        for frac, elist in frac_edges.items():
            n_i = n_int.get(frac, 2)
            Cs = [raw[e] for e in elist]
            c_max = max(Cs)
            F = (sum(Cs) - c_max) / (n_i - 1) if n_i > 1 else 0.0
            # The 2021 clamp is C-F -> 0 for negatives; on a full graph solve an
            # exactly-zero conductance can isolate a node and make the Laplacian
            # singular, so floor at a negligible fraction of the fracture max.
            floor = 1e-12 * c_max
            for (u, v) in elist:
                G.edges[u, v]['weight'] = max(floor, raw[(u, v)] - F)
    else:
        local_print_log(
            f"Error. Unknown mp_correction '{mp_correction}'. "
            "Options: 'divide', 'additive', 'none'.", 'error')


CONDUCTANCE_MODELS["doolaeghe"] = _doolaeghe_conductance


def add_weight(G, model="karra", **model_kwargs):
    """Assign edge conductance ('weight') to every edge using the chosen model.

    Parameters
    ----------
        G : NetworkX Graph
            networkX graph

        model : str
            Conductance model name. Default 'karra' (Karra et al. 2018,
            ``w = K*A/L``). See ``CONDUCTANCE_MODELS`` for the registry.

        **model_kwargs
            forwarded to the model (e.g. B, mp_correction for 'doolaeghe').

    Returns
    -------
        None
    """
    try:
        model_fn = CONDUCTANCE_MODELS[model]
    except KeyError:
        options = ", ".join(sorted(CONDUCTANCE_MODELS))
        local_print_log(
            f"Error. Unknown conductance model '{model}'. Options: {options}.",
            'error')
        return
    model_fn(G, **model_kwargs)
    return
