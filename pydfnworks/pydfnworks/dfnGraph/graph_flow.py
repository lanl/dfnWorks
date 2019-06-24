import networkx as nx
import numpy as np
import sys
import scipy.sparse

# pydfnworks modules
from pydfnworks.dfnGraph import dfn2graph as d2g


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


def prepare_graph_with_attributes(inflow, outflow):
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

    G = d2g.create_intersection_graph(
        inflow, outflow, intersection_file="intersection_list.dat")
    Gtilde = G.copy()
    d2g.add_perm(Gtilde)
    d2g.add_area(Gtilde)
    d2g.add_weight(Gtilde)

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['inletflag'] = False
        Gtilde.nodes[v]['outletflag'] = False

    for v in nx.neighbors(Gtilde, 's'):
        Gtilde.nodes[v]['inletflag'] = True

    for v in nx.neighbors(Gtilde, 't'):
        Gtilde.nodes[v]['outletflag'] = True

    Gtilde.remove_node('s')
    Gtilde.remove_node('t')

    Gtilde = nx.convert_node_labels_to_integers(Gtilde,
                                                first_label=0,
                                                ordering="sorted",
                                                label_attribute="old_label")

    return Gtilde


def solve_flow_on_graph(Gtilde, Pin, Pout, fluid_viscosity=8.9e-4):
    """ Given a NetworkX graph prepared  for flow solve, solve for vertex pressures, and equip edges with attributes (Darcy) flux  and time of travel

    Parameters
    ----------
        Gtilde : NetworkX graph

        Pin : double
            Value of pressure (in Pa) at inlet
        
        Pout : double
            Value of pressure (in Pa) at outlet
        
        fluid_viscosity : double
            optional, in Pa-s, default is for water
    
    Returns
    -------
        Gtilde : NetworkX graph 
            Gtilde is updated with vertex pressures, edge fluxes and travel times
    """

    Inlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['inletflag']]
    Outlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['outletflag']]

    if not set(Inlet).isdisjoint(set(Outlet)):
        error = "Incompatible graph: Vertex connected to both source and target"
        sys.stderr.write(error)
        sys.exit(1)

    D, A = get_laplacian_sparse_mat(Gtilde, weight='weight', format='lil')

    rhs = np.zeros(Gtilde.number_of_nodes())

    for v in Inlet:
        rhs[v] = Pin
        A[v, :] = 0
        D[v, v] = 1.0
    for v in Outlet:
        rhs[v] = Pout
        A[v, :] = 0
        D[v, v] = 1.0
    L = D - A  # automatically converts to csr when returning L

    print("Solving sparse system")
    Phat = scipy.sparse.linalg.spsolve(L, rhs)
    print("Updating graph edges with flow solution")

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['pressure'] = Phat[v]

    for u, v in nx.edges(Gtilde):
        delta_p = abs(Gtilde.nodes[u]['pressure'] -
                      Gtilde.nodes[v]['pressure'])
        if delta_p > np.spacing(Gtilde.nodes[u]['pressure']):
            Gtilde.edges[u, v]['flux'] = (
                Gtilde.edges[u, v]['perm'] / fluid_viscosity
            ) * abs(Gtilde.nodes[u]['pressure'] -
                    Gtilde.nodes[v]['pressure']) / Gtilde.edges[u, v]['length']
            Gtilde.edges[u, v]['time'] = Gtilde.edges[u, v][
                'length'] / Gtilde.edges[u, v]['flux']
        else:
            Gtilde.edges[u, v]['flux'] = 0

    print("Graph flow complete")
    return Gtilde


def run_graph_flow(self, inflow, outflow, Pin, Pout, fluid_viscosity=8.9e-4):
    """ Run the graph flow portion of the workflow

    Parameters
    ----------
        self : object
            DFN Class


        inflow : string
            name of file containing list of DFN fractures on inflow boundary

        outflow: string
            name of file containing list of DFN fractures on outflow boundary

        Pin : double
            Value of pressure (in Pa) at inlet
        
        Pout : double
            Value of pressure (in Pa) at outlet
        
        fluid_viscosity : double
            optional, in Pa-s, default is for water
    
    Returns
    -------
        Gtilde : NetworkX graph 
            Grtilde is updated with vertex pressures, edge fluxes and travel times

    Notes
    -----
    Information on individual functions in found therein
    """
    Gtilde = prepare_graph_with_attributes(inflow, outflow)
    Gtilde = solve_flow_on_graph(Gtilde, Pin, Pout, fluid_viscosity)
    return Gtilde
