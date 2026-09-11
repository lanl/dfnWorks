"""
.. module:: metrics.py
   :synopsis: Post-processing metrics and IO for the graph flow solution
              (flow channeling density dQ, and HDF5 dump of flow variables).
"""

import numpy as np
import h5py

from pydfnworks.general.logging import local_print_log, print_log


def compute_dQ(self, G):
    """ Computes the DFN fracture intensity (p32) and flow channeling density indicator from the graph flow solution on G

    Parameters
    -----------------
        self : object
            DFN Class

        G : networkX graph
            Output of run_graph_flow

    Returns
    ---------------
        p32 : float
            Fracture intensity

        dQ : float flow channeling density indicator

    Notes
    ------------
        For definitions of p32 and dQ along with a discussion see " Hyman, Jeffrey D. "Flow channeling in fracture networks: characterizing the effect of density on preferential flow path formation." Water Resources Research 56.9 (2020): e2020WR027986. "

    """
    self.print_log(
        "--> Computing fracture intensity (p32) and flow channeling density indicator (dQ)"
    )

    fracture_surface_area = 2*self.surface_area
    domain_volume = self.domain['x'] * self.domain['y'] * self.domain['z']

    Qf = np.zeros(self.num_frac)
    ## convert to undirected
    H = G.to_undirected()
    ## walk through fractures
    for curr_frac in range(1, self.num_frac + 1):
        # print(f"\nstarting on fracture {curr_frac}")
        # Gather nodes on current fracture
        current_nodes = []
        for u, d in H.nodes(data=True):
            for f in d["frac"]:
                if f == curr_frac:
                    current_nodes.append(u)
        # cycle through nodes on the fracture and get the outgoing / incoming
        # volumetric flow rates
        for u in current_nodes:
            neighbors = H.neighbors(u)
            for v in neighbors:
                if v not in current_nodes:
                    # outgoing vol flow rate
                    Qf[curr_frac - 1] += abs(H[u][v]['vol_flow_rate'])
                    for f in H.nodes[v]['frac']:
                        if f != curr_frac and f != 's' and f != 't':
                            # incoming vol flow rate
                            Qf[f - 1] += abs(H[u][v]['vol_flow_rate'])
    # Divide by 1/2 to remove up double counting
    Qf *= 0.5
    p32 = fracture_surface_area.sum() / domain_volume
    top = sum(fracture_surface_area * Qf)**2
    bottom = sum(fracture_surface_area * Qf**2)
    dQ = (1.0 / domain_volume) * (top / bottom)
    self.print_log(f"--> P32: {p32:0.2e} [1/m]")
    self.print_log(f"--> dQ: {dQ:0.2e} [1/m]")
    self.print_log(f"--> Active surface percentage {100*dQ/p32:0.2f}")
    self.print_log(f"--> Geometric equivalent fracture spacing {1/p32:0.2e} m")
    self.print_log(f"--> Hydrological equivalent fracture spacing {1/dQ:0.2e} m")
    self.print_log("--> Complete \n")
    return p32, dQ, Qf


def dump_graph_flow_values(G,graph_flow_filename):
    """
    Writes graph flow information to an h5 file named graph_flow_name.

    Parameters
    --------------------
        G : NetworkX graph
            graph with flow variables attached

        graph_flow_filename : string
            name of output file

    Returns
    ---------------
        None

    Notes
    ---------------
        name of graph_flow_filename is set in run_graph_flow for primary workflow. Default is graph_flow.hdf5

    """

    local_print_log(f'\n--> Writting flow variables into h5df file: {graph_flow_filename}')
    local_print_log('--> Starting')
    num_edges = G.number_of_edges()
    velocity = np.zeros(num_edges)
    lengths = np.zeros_like(velocity)
    vol_flow_rate = np.zeros_like(velocity)
    area = np.zeros_like(velocity)
    aperture = np.zeros_like(velocity)
    volume = np.zeros_like(velocity)

    for i, val in enumerate(G.edges(data=True)):
        u, v, d = val
        velocity[i] = d['velocity']
        lengths[i] = d['length']
        vol_flow_rate[i] = d['vol_flow_rate']
        area[i] = d['area']
        aperture[i] = d['b']
        volume[i] = area[i] * aperture[i]

    with h5py.File(graph_flow_filename, "w") as f5file:
        h5dset = f5file.create_dataset('velocity', data=velocity)
        h5dset = f5file.create_dataset('length', data=lengths)
        h5dset = f5file.create_dataset('vol_flow_rate', data=vol_flow_rate)
        h5dset = f5file.create_dataset('area', data=area)
        h5dset = f5file.create_dataset('aperture', data=aperture)
        h5dset = f5file.create_dataset('volume', data=volume)
    local_print_log('--> Complete')
