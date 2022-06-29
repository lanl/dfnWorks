import numpy as np
import scipy.special


def limited_matrix_diffusion(self, G):
    
    print("here we go!")
    
def unlimited_matrix_diffusion(self, G):
    """ Matrix diffusion part of particle transport

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None
    """

    b = np.sqrt(12.0 * G.edges[self.curr_node, self.next_node]['perm'])
    a_nondim = self.matrix_porosity * np.sqrt(self.matrix_diffusivity) / b
    xi = np.random.uniform(size=1, low=0, high=1)[0]
    self.delta_t_md = ((a_nondim * self.delta_t /
                        scipy.special.erfcinv(xi))**2)


