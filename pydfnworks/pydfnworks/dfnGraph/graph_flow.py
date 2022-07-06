import networkx as nx
import numpy as np
import sys
import scipy.sparse

# pydfnworks modules
from pydfnworks.dfnGraph import dfn2graph as d2g
from pydfnworks.dfnGen.meshing import mesh_dfn_helper as mh


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

    A = nx.to_scipy_sparse_matrix(G,
                                  nodelist=nodelist,
                                  weight=weight,
                                  dtype=dtype,
                                  format=format)

    (n, n) = A.shape
    data = np.asarray(A.sum(axis=1).T)
    D = scipy.sparse.spdiags(data, 0, n, n, format=format)
    return D, A


def prepare_graph_with_attributes(inflow, outflow, G=None):
    """ Create a NetworkX graph, prepare it for flow solve by equipping edges with  attributes, renumber vertices, and tag vertices which are on inlet or outlet
    
    Parameters
    ----------
        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

    Returns
    -------
        Gtilde : NetworkX graph
    """

    if G == None:
        G = d2g.create_intersection_graph(
            inflow, outflow, intersection_file="intersection_list.dat")

        Gtilde = G.copy()
        # need to add aperture
        d2g.add_perm(Gtilde)
        d2g.add_area(Gtilde)
        d2g.add_weight(Gtilde)

    else:
        Gtilde = G
        d2g.add_perm(Gtilde)
        d2g.add_area(Gtilde)
        d2g.add_weight(Gtilde)

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['inletflag'] = False
        Gtilde.nodes[v]['outletflag'] = False

    if len(list(nx.neighbors(Gtilde, 's'))) == 0:
        error = "Error. There are no nodes in the inlet.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)

    for v in nx.neighbors(Gtilde, 's'):
        Gtilde.nodes[v]['inletflag'] = True

    if len(list(nx.neighbors(Gtilde, 't'))) == 0:
        error = "Error. There are no nodes in the outlet.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)

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
        Gtilde : NetworkX graph 
            Gtilde is updated with vertex pressures, edge fluxes and travel times
    """

    print("--> Starting Graph flow")

    Inlet = [v for v in nx.nodes(G) if G.nodes[v]['inletflag']]
    Outlet = [v for v in nx.nodes(G) if G.nodes[v]['outletflag']]

    if not set(Inlet).isdisjoint(set(Outlet)):
        error = "Incompatible graph: Vertex connected to both source and target\n"
        sys.stderr.write(error)
        sys.exit(1)

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

    print("--> Solving sparse system")
    pressure = scipy.sparse.linalg.spsolve(L, b)
    print("--> Updating graph edges with flow solution")

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
        if delta_p > 0:
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

    print("--> Graph flow complete")
    return H


def compute_dQ(self, G):
    """ Computes the value dQ from the graph flow G

    """
    print(
        "--> Computing fracture intensity (p32) and flow channeling density indicator (dQ)"
    )

    fracture_surface_area = 2 * np.genfromtxt("surface_area_Final.dat",
                                              skip_header=1)
    _, _, _, _, domain = mh.parse_params_file(quiet=True)
    domain_volume = domain['x'] * domain['y'] * domain['z']

    num_frac = len(fracture_surface_area)
    Qf = np.zeros(num_frac)
    ## walk through fractures
    for curr_frac in range(1, num_frac + 1):
        # print(f"\nstarting on fracture {curr_frac}")
        # Gather nodes on current fracture
        current_nodes = []
        for u, d in G.nodes(data=True):
            for f in d["frac"]:
                if f == curr_frac:
                    current_nodes.append(u)
        # cycle through nodes on the fracture and get the outgoing / incoming
        # volumetric flow rates
        for u in current_nodes:
            neighbors = G.neighbors(u)
            for v in neighbors:
                if v not in current_nodes:
                    # outgoing
                    Qf[curr_frac - 1] += abs(G[u][v]['vol_flow_rate'])
                    for f in G.nodes[v]['frac']:
                        if f != curr_frac and f != 's' and f != 't':
                            # incoming onto the other fracture.
                            Qf[f - 1] += abs(G[u][v]['vol_flow_rate'])
        # cut by 1/2 to remove up double counting
        Qf *= 0.5

    p32 = fracture_surface_area.sum() / domain_volume
    top = sum(fracture_surface_area * Qf)**2
    bottom = sum(fracture_surface_area * Qf**2)
    dQ = (1.0 / domain_volume) * (top / bottom)
    print(f"--> P32: {p32:0.2e} [1/m]")
    print(f"--> dQ: {dQ:0.2e} [1/m]")
    print(f"--> Geometric equivalent spacing {1/p32:0.2e} m")
    print(f"--> Hydrological equivalent spacing {1/dQ:0.2e} m")
    print("--> Complete \n")
    return p32, dQ


def run_graph_flow(self,
                   inflow,
                   outflow,
                   pressure_in,
                   pressure_out,
                   fluid_viscosity=8.9e-4,
                   phi=1,
                   G=None):
    """ Run the graph flow portion of the workflow

    Parameters
    ----------
        self : object
            DFN Class


        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

        pressure_in : double
            Value of pressure (in Pa) at inlet
        
        pressure_out : double
            Value of pressure (in Pa) at outlet

        fluid_viscosity : double
            optional, in Pa-s, default is for water
            
        phi : double
            Porosity, default is 1

        G : Input Graph 

    Returns
    -------
        Gtilde : NetworkX graph 
            Grtilde is updated with vertex pressures, edge fluxes and travel times

    Notes
    -----
    Information on individual functions in found therein
    """
    Gtilde = prepare_graph_with_attributes(inflow, outflow, G)
    Gtilde = solve_flow_on_graph(Gtilde, pressure_in, pressure_out,
                                 fluid_viscosity, phi)

    return Gtilde
