#!/usr/bin/env python

import networkx as nx
import numpy as np
import dfn2graph
import sys
import scipy.sparse



def get_laplacian_sparse_mat(G, nodelist=None, weight=None, dtype=None, format='lil'):
    ''' Get the matrices D, A that make up the Laplacian sparse matrix in desired sparsity format. Useful if boundary conditions have to be enforced  by modifying rows of L = D - A

    Inputs:
    G: NetworkX graph equipped with weight attribute
    nodelist: list of nodes of G for which laplacian is desired. Default is None in which case, all the nodes
    weight: For weighted Laplacian, else all weights assumed unity
    dtype: default is None, cooresponds to float
    format: sparse matrix format, csr, csc, coo, lil_matrix with default being lil
    Outputs: D, A
    '''

    A = nx.to_scipy_sparse_matrix(G, nodelist=nodelist, weight=weight, dtype=dtype, format=format)

    (n, n) = A.shape
    data = np.asarray(A.sum(axis=1).T)
    D = scipy.sparse.spdiags(data, 0, n, n, format=format)
    return D, A

 
def prepare_graph_with_attributes(inflow, outflow):
    ''' Create a NetworkX graph, prepare it for flow solve by equipping edges with  attributes, renumber vertices, and tag vertices which are on inlet or outlet
    
        Inputs:
        inflow: file containing list of DFN fractures on inflow boundary
        outflow: file containing list of DFN fractures on outflow boundary

        Output: G (NetworkX graph)
    '''



    G = dfn2graph.create_intersection_graph(inflow, outflow, intersection_file="intersection_list.dat")

    Gtilde = G.copy()

    dfn2graph.add_perm(Gtilde)
    dfn2graph.add_area(Gtilde)
    dfn2graph.add_weight(Gtilde)

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['inletflag']= False
        Gtilde.nodes[v]['outletflag'] = False

    for v in nx.neighbors(Gtilde, 's'):
        Gtilde.nodes[v]['inletflag'] = True

    for v in nx.neighbors(Gtilde, 't'):
        Gtilde.nodes[v]['outletflag'] = True


    Gtilde.remove_node('s')
    Gtilde.remove_node('t')
    sys_size = Gtilde.number_of_nodes()

    mapping = dict(zip(Gtilde, range(0, sys_size)))
    Gtilde = nx.relabel_nodes(Gtilde, mapping, copy=False)

    return Gtilde





def solve_flow_on_graph(Gtilde, Pin, Pout, fluid_viscosity=8.9e-4):
    ''' Given a NetworkX graph prepared  for flow solve, solve for vertex pressures, and equip edges with attributes (Darcy) flux  and time of travel

    Inputs:
    Gtilde: Prepared NetworkX graph
    Pin: Value of pressure (in Pa) at inlet
    Pout: Value of pressure (in Pa) at outlet
    fluid_viscosity: optional, in Pa-s, assumed to be that of water as if not provided
    Output: NetworkX graph updated with vertex pressures, edge fluxes and travel times
    '''


    Inlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['inletflag']]
    Outlet = [v for v in nx.nodes(Gtilde) if Gtilde.nodes[v]['outletflag']]


    if not set(Inlet).isdisjoint(set(Outlet)):
        sys.exit("Incompatible graph: Vertex connected to both source and target")


    D, A = get_laplacian_sparse_mat(Gtilde, weight='weight', format='lil')


    rhs = np.zeros(Gtilde.number_of_nodes())

    for v in Inlet:
        rhs[v] = Pin
        A[v,:] = 0
        D[v, v] = 1.0
    for v in Outlet:
        rhs[v]  = Pout
        A[v, :] = 0
        D[v, v] = 1.0
    L = D - A # automatically converts to csr when returning L


    print "Solving sparse system..."

    Phat = scipy.sparse.linalg.spsolve(L, rhs)
    
    print "Updating graph edges with flow solution..."

    for v in nx.nodes(Gtilde):
        Gtilde.nodes[v]['pressure'] = Phat[v]

    for u,v in nx.edges(Gtilde):
        delta_p = abs(Gtilde.nodes[u]['pressure'] - Gtilde.nodes[v]['pressure'] )
        if delta_p > np.spacing(Gtilde.nodes[u]['pressure']):
            Gtilde.edges[u, v]['flux'] =  (Gtilde.edges[u, v]['perm']/fluid_viscosity) * abs( Gtilde.nodes[u]['pressure'] - Gtilde.nodes[v]['pressure'] ) / Gtilde.edges[u, v]['length']
            Gtilde.edges[u, v]['time'] = Gtilde.edges[u, v]['length'] / Gtilde.edges[u, v]['flux']
        else:
            Gtilde.edges[u, v]['flux'] = 0
    
    print "Graph flow complete"
    return Gtilde


def run_graph_flow(self, inflow, outflow, Pin, Pout, fluid_viscosity=8.9e-4):

    Gtilde = prepare_graph_with_attributes(inflow, outflow)
    Gtilde = solve_flow_on_graph(Gtilde, Pin, Pout,fluid_viscosity) 
    return Gtilde
