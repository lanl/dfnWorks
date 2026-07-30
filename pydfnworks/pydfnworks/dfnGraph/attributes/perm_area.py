import numpy as np
import networkx as nx
import sys



def add_perm(G):
    """ Add fracture permeability to Graph. If Graph representation is
    fracture, then permeability is a node attribute. If graph representation 
    is intersection, then permeability is an edge attribute


    Parameters
    ---------- 
        G :networkX graph
            NetworkX Graph based on the DFN
   
        fracture_infor : str
                filename for fracture information
    Returns
    -------
 
    Notes
    -----

"""

    # Use the DFN's actual aperture (column 2), not sqrt(12*perm). The two agree
    # only under the cubic law; sourcing the real aperture keeps 'b' consistent
    # with the aperture used in add_area (and hence with the karra conductance,
    # the doolaeghe transmissivity T=perm*b, TDRW, and the volume output).
    _finfo = np.genfromtxt("dfnGen_output/fracture_info.dat", skip_header=1)
    _finfo = np.atleast_2d(_finfo)
    perm = _finfo[:, 1]
    aperture = _finfo[:, 2]

    if G.graph['representation'] == "fracture":
        for n in nx.nodes(G):
            if n != 's' and n != 't':
                G.nodes[n]['perm'] = perm[n - 1]
                G.nodes[n]['b'] = aperture[n - 1]
                G.nodes[n]['iperm'] = 1.0 / perm[n - 1]
            else:
                G.nodes[n]['perm'] = 1.0
                G.nodes[n]['b'] = 1.0
                G.nodes[n]['iperm'] = 1.0

    elif G.graph['representation'] == "intersection":
        for u, v in nx.edges(G):
            frac = G[u][v]['frac']
            if frac != 's' and frac != 't':
                G[u][v]['perm'] = perm[frac - 1]
                G[u][v]['b'] = aperture[frac - 1]
                G[u][v]['iperm'] = 1.0 / perm[frac - 1]
            else:
                G[u][v]['perm'] = 1.0
                G[u][v]['b'] = 1.0
                G[u][v]['iperm'] = 1.0

    elif G.graph['representation'] == "bipartite":
        # add fracture info
        with open("dfnGen_output/fracture_info.dat") as f:
            f.readline()
            data = f.read().strip()
            for fracture, line in enumerate(data.split('\n'), 1):
                c, perm, aperture = line.split(' ')
                G.nodes[fracture]['perm'] = float(perm)
                G.nodes[fracture]['iperm'] = 1.0 / float(perm)
                G.nodes[fracture]['b'] = float(aperture)


def add_area(G):
    ''' Read Fracture aperture from fracture_info.dat and 
    load on the edges in the graph. Graph must be intersection to node
    representation
    
    Parameters
    ----------
        G : NetworkX Graph
            networkX graph 
        fracture_info : str
            filename for fracture information
    
    Returns
    -------
        None
'''

    aperture = np.genfromtxt("dfnGen_output/fracture_info.dat",
                             skip_header=1)[:, 2]
    edges = list(nx.edges(G))
    for u, v in edges:
        x = G.edges[u, v]['frac']
        if x != 's' and x != 't':
            G.edges[u,
                    v]['area'] = aperture[x - 1] * (G.nodes[u]['length'] +
                                                    G.nodes[v]['length']) / 2.0
        else:
            G.edges[u, v]['area'] = 1.0
    return


def fracture_diameter(surface_area=None, radii=None, method="area"):
    ''' Per-fracture representative diameter for the size-aware conductance model.

    Parameters
    ----------
        surface_area : array-like
            per-fracture surface area (e.g. self.surface_area). Required for
            method='area'.

        radii : array-like
            per-fracture representative radius (e.g. self.radii[:, 2]). Required
            for method='max_radius'.

        method : str
            'area' (default): area-equivalent disk diameter 2*sqrt(A/pi). This is
            shape-agnostic and reflects domain clipping (surface_area is the
            actual, post-clip fracture area), and reduces to 2R for an ideal disk.
            'max_radius': 2 * max(x,y) radius -- the nominal (pre-clip) size.

    Returns
    -------
        diameter : numpy array
            per-fracture diameter, indexed by fracture number - 1
    '''
    if method == "area":
        if surface_area is None:
            local_print_log(
                "Error. fracture_diameter(method='area') requires surface_area.",
                'error')
        return 2.0 * np.sqrt(np.asarray(surface_area, dtype=float) / np.pi)
    elif method == "max_radius":
        if radii is None:
            local_print_log(
                "Error. fracture_diameter(method='max_radius') requires radii.",
                'error')
        return 2.0 * np.asarray(radii, dtype=float)
    else:
        local_print_log(
            f"Error. Unknown fracture_diameter method '{method}'. "
            "Options: 'area', 'max_radius'.", 'error')


def add_diameter(G, diameter, clamp_to_intersection=True):
    ''' Load fracture diameter onto each edge of an intersection graph. Used by
    the size-aware (Doolaeghe et al. 2020) conductance model.

    Parameters
    ----------
        G : NetworkX Graph
            intersection graph (edges carry a 'frac' fracture id, nodes a 'length')

        diameter : array-like
            per-fracture diameter, indexed by fracture number - 1 (e.g. from
            fracture_diameter()).

        clamp_to_intersection : bool
            if True (default), the diameter on a fracture is raised to at least
            the longest intersection on that fracture. A clipped fracture's
            area-equivalent diameter can otherwise fall below an intersection
            length (a chord of the fracture), pushing the trapezoid model out of
            its regime.

    Returns
    -------
        None

    Notes
    -----
        Source/target edges (frac 's'/'t') get a placeholder value; they are
        skipped by the conductance models (length == 0).
    '''
    max_l = {}
    if clamp_to_intersection:
        for _, d in G.nodes(data=True):
            frac = d.get('frac')
            length = d.get('length')
            if frac is None or length is None:
                continue
            for f in frac:
                if isinstance(f, int):
                    max_l[f] = max(max_l.get(f, 0.0), length)

    for u, v in nx.edges(G):
        frac = G.edges[u, v]['frac']
        if isinstance(frac, (int, np.integer)):
            D = float(diameter[frac - 1])
            if clamp_to_intersection:
                D = max(D, max_l.get(int(frac), 0.0))
            G.edges[u, v]['diameter'] = D
        else:
            G.edges[u, v]['diameter'] = 1.0
    return
