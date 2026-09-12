import networkx as nx
import numpy as np
import sys
import scipy.sparse
import h5py

# pydfnworks modules
from pydfnworks.dfnGraph.construction.intersection_graph import create_intersection_graph
from pydfnworks.dfnGraph.attributes.perm_area import add_perm, add_area, add_diameter, fracture_diameter
from pydfnworks.dfnGraph.attributes.conductance import add_weight
from pydfnworks.dfnGraph.algorithms.deconstruct import deconstruct_intersection_graph
from pydfnworks.dfnGraph.flow.metrics import dump_graph_flow_values
from pydfnworks.general.logging import local_print_log, print_log

def get_laplacian_sparse_mat(G,
                             nodelist=None,
                             weight=None,
                             dtype=None,
                             format='lil'):
    """ Get the matrices D, A that make up the Laplacian sparse matrix in desired sparsity format. Used to enforce boundary conditions by modifying rows of L = D - A

    Parameters
    ----------
        G : object
            NetworkX graph equipped with weight attribute

        nodelist : list
            list of nodes of G for which laplacian is desired. Default is None in which case, all the nodes
        
        weight : string
            For weighted Laplacian, else all weights assumed unity
        
        dtype :  default is None, cooresponds to float
        
        format: string
            sparse matrix format, csr, csc, coo, lil_matrix with default being lil

    Returns
    -------
        D : sparse 2d float array       
            Diagonal part of Laplacian
            
        A : sparse 2d float array
            Adjacency matrix of graph
    """

    A = nx.to_scipy_sparse_array(G,
                                  nodelist=nodelist,
                                  weight=weight,
                                  dtype=dtype,
                                  format=format)

    (n, n) = A.shape
    data = np.asarray(A.sum(axis=1).T)
    D = scipy.sparse.spdiags(data, 0, n, n, format=format)
    return D, A


def prepare_graph_with_attributes(inflow, outflow, G=None,
                                  conductance_model="doolaeghe", diameter=None,
                                  simplify=False, normal_vectors=None,
                                  **conductance_kwargs):
    """ Create a NetworkX graph, prepare it for flow solve by equipping edges with  attributes, renumber vertices, and tag vertices which are on inlet or outlet

    Parameters
    ----------
        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

        G : NetworkX graph

        conductance_model : string
            edge conductance model. 'karra' (default) or 'doolaeghe'. See
            pydfnworks.dfnGraph.attributes.conductance.

        diameter : array-like
            per-fracture diameter (e.g. from attributes.perm_area.fracture_diameter).
            Required when conductance_model == 'doolaeghe'.

        simplify : bool
            if True, remove crossing (redundant) edges per fracture via the
            Doolaeghe et al. (2021) deconstructed-graph method. Requires
            normal_vectors.

        normal_vectors : array-like
            per-fracture unit normals (e.g. self.normal_vectors). Required when
            simplify is True.

        **conductance_kwargs
            forwarded to the conductance model (e.g. B, mp_correction).

    Returns
    -------
        Gtilde : NetworkX graph
    """

    if G == None:
        G = create_intersection_graph(inflow, outflow)

        Gtilde = G.copy()
        # need to add aperture
        add_perm(Gtilde)
        add_area(Gtilde)

    else:
        Gtilde = G
        #add_perm(Gtilde)
        #add_area(Gtilde)

    if conductance_model == "doolaeghe":
        if diameter is None:
            local_print_log(
                "Error. conductance_model='doolaeghe' requires per-fracture "
                "diameter (see attributes.perm_area.fracture_diameter).", 'error')
        add_diameter(Gtilde, diameter)
    add_weight(Gtilde, model=conductance_model, **conductance_kwargs)

    if simplify:
        if normal_vectors is None:
            local_print_log(
                "Error. simplify=True requires normal_vectors "
                "(pass normal_vectors=self.normal_vectors).", 'error')
        deconstruct_intersection_graph(Gtilde, normal_vectors)

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['inletflag'] = False
        Gtilde.nodes[v]['outletflag'] = False

    if len(list(nx.neighbors(Gtilde, 's'))) == 0:
        error = "Error. There are no nodes in the inlet.\nExiting"
        local_print_log(error, 'error')

    for v in nx.neighbors(Gtilde, 's'):
        Gtilde.nodes[v]['inletflag'] = True

    if len(list(nx.neighbors(Gtilde, 't'))) == 0:
        error = "Error. There are no nodes in the outlet.\nExiting"
        local_print_log(error, 'error')

    for v in nx.neighbors(Gtilde, 't'):
        Gtilde.nodes[v]['outletflag'] = True

    Gtilde.remove_node('s')
    Gtilde.remove_node('t')

    Gtilde = nx.convert_node_labels_to_integers(Gtilde,
                                                first_label=0,
                                                ordering="sorted",
                                                label_attribute="old_label")

    return Gtilde


def solve_flow_on_graph(G, pressure_in, pressure_out, fluid_viscosity, phi):
    """ Given a NetworkX graph prepared  for flow solve, solve for vertex pressures, and equip edges with attributes (Darcy) flux  and time of travel

    Parameters
    ----------
        G : NetworkX graph

        pressure_in : double
            Value of pressure (in Pa) at inlet
        
        pressure_out : double
            Value of pressure (in Pa) at outlet
        
        fluid_viscosity : double
            optional, in Pa-s, default is for water

        phi : double
            Porosity, default is 1

    Returns
    -------
        H : Acyclic Directed NetworkX graph 
            H is updated with vertex pressures, edge fluxes and travel times. The only edges that exists are those with postive flow rates. 

    Notes
    ----------
        None

    """

    local_print_log("--> Starting Graph flow")

    Inlet = [v for v in nx.nodes(G) if G.nodes[v]['inletflag']]
    Outlet = [v for v in nx.nodes(G) if G.nodes[v]['outletflag']]

    if not set(Inlet).isdisjoint(set(Outlet)):
        error = "Incompatible graph: Vertex connected to both source and target\n"
        local_print_log(error, 'error')

    D, A = get_laplacian_sparse_mat(G, weight='weight', format='lil')

    b = np.zeros(G.number_of_nodes())

    for v in Inlet:
        b[v] = pressure_in
        A[v, :] = 0
        D[v, v] = 1.0
    for v in Outlet:
        b[v] = pressure_out
        A[v, :] = 0
        D[v, v] = 1.0
    L = D - A  # automatically converts to csr when returning L

    local_print_log("--> Solving Linear System for pressure at nodes")
    pressure = scipy.sparse.linalg.spsolve(L, b)
    if not np.all(np.isfinite(pressure)):
        local_print_log(
            "Error. Graph flow solve produced non-finite pressures. The system "
            "is singular -- typically isolated nodes or zero-conductance edges "
            "(e.g. from an over-aggressive conductance/simplification choice).",
            'error')
    local_print_log("--> Updating graph edges with flow solution")

    for v in nx.nodes(G):
        G.nodes[v]['pressure'] = pressure[v]

    H = nx.DiGraph()
    H.add_nodes_from(G.nodes(data=True))

    for u, v in nx.edges(G):
        # Find direction of flow
        if G.nodes[u]['pressure'] > G.nodes[v]['pressure']:
            upstream = u
            downstream = v
        elif G.nodes[v]['pressure'] >= G.nodes[u]['pressure']:
            upstream = v
            downstream = u

        delta_p = G.nodes[upstream]['pressure'] - G.nodes[downstream][
            'pressure']
        if delta_p > 1e-16:
            ## Create new edge in DiGraph
            H.add_edge(upstream, downstream)
            # Transfer edge attributes
            for att in [
                    'perm', 'iperm', 'length', 'weight', 'area', 'frac', 'b'
            ]:
                H.edges[upstream, downstream][att] = G.edges[upstream,
                                                             downstream][att]

            H.edges[upstream, downstream]['flux'] = (
                H.edges[upstream, downstream]['perm'] / fluid_viscosity) * (
                    delta_p / H.edges[upstream, downstream]['length'])

            H.edges[upstream, downstream]['vol_flow_rate'] = H.edges[
                upstream, downstream]['flux'] * H.edges[upstream,
                                                        downstream]['area']

            # H.edges[downstream, upstream]['vol_flow_rate'] =  -1*H.edges[upstream, downstream]['vol_flow_rate']

            H.edges[upstream,
                    downstream]['velocity'] = H.edges[upstream,
                                                      downstream]['flux'] / phi
            H.edges[upstream,
                    downstream]['time'] = H.edges[upstream, downstream][
                        'length'] / (H.edges[upstream, downstream]['velocity'])

    local_print_log("--> Graph flow complete")
    return H


def run_graph_flow(self,
                   inflow,
                   outflow,
                   pressure_in,
                   pressure_out,
                   fluid_viscosity=8.9e-4,
                   phi=1,
                   G=None,
                   graph_flow_name = "graph_flow.hdf5",
                   conductance_model="doolaeghe",
                   diameter_from="area",
                   simplify=False,
                   **conductance_kwargs):
    """ Solve for pressure driven steady state flow on a graph representation of the DFN.

    Parameters
    ----------
        self : object
            DFN Class

        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

        pressure_in : double
            Value of pressure at inlet [Pa]
        
        pressure_out : double
            Value of pressure at outlet [Pa]

        fluid_viscosity : double
            optional,  default is for water. [Pa*s]
            
        phi : double
            Fracture porosity, default is 1 [-]

        G : Input Graph

        conductance_model : string
            edge conductance model, 'doolaeghe' (default) or 'karra'. See
            pydfnworks.dfnGraph.attributes.conductance.

        diameter_from : string
            fracture-diameter source for the 'doolaeghe' model: 'area' (default,
            area-equivalent 2*sqrt(surface_area/pi)) or 'max_radius'
            (2*self.radii[:, 2]).

        simplify : bool
            if True, remove crossing (redundant) edges per fracture via the
            Doolaeghe et al. (2021) deconstructed-graph method.

        **conductance_kwargs
            forwarded to the conductance model (e.g. B, mp_correction='additive').

    Returns
    -------
        Gtilde : NetworkX graph
            Gtilde is a directed acyclic graph with vertex pressures, fluxes, velocities, volumetric flow rates, and travel times

    """
    self.print_log("\n--> Graph Flow: Starting")
    self.print_log(f"--> Inflow Boundary Name: {inflow}")
    self.print_log(f"--> Outflow: {outflow}")
    self.print_log(f"--> Inflow Pressure: {pressure_in} [Pa]")
    self.print_log(f"--> Outflow Pressure: {pressure_out} [Pa]")
    self.print_log(f"--> Fluid viscosity: {fluid_viscosity} [Pa*s]")
    self.print_log(f"--> Fracture Porosity: {phi} [-]")
    self.print_log(f"--> Conductance model: {conductance_model}")

    if G == None:
        self.print_log("\n--> No Graph provided, building one")
        G = self.create_graph("intersection", inflow, outflow)
    else:
         self.print_log("\n--> Graph provided")

    diameter = None
    if conductance_model == "doolaeghe":
        radii = self.radii[:, 2] if getattr(self, "radii", None) is not None else None
        surface_area = getattr(self, "surface_area", None)
        if diameter_from == "area" and surface_area is None and radii is not None:
            self.print_log(
                "--> Warning: surface_area unavailable; falling back to "
                "diameter_from='max_radius'.", 'warning')
            diameter_from = "max_radius"
        diameter = fracture_diameter(surface_area=surface_area, radii=radii,
                                     method=diameter_from)
    normals = getattr(self, "normal_vectors", None)
    Gtilde = prepare_graph_with_attributes(inflow, outflow, G,
                                           conductance_model=conductance_model,
                                           diameter=diameter,
                                           simplify=simplify,
                                           normal_vectors=normals,
                                           **conductance_kwargs)
    Gtilde = solve_flow_on_graph(Gtilde, pressure_in, pressure_out,
                                 fluid_viscosity, phi)

    dump_graph_flow_values(Gtilde, graph_flow_name)
    self.print_log("--> Graph Flow: Complete\n")
    return Gtilde
