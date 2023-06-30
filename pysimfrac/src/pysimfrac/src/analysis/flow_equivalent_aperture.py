import numpy as np

def convert_aperture_to_perm(self):
    # Converting aperture to perm using the cubic law
    self.perm = (12*self.aperture**2)/12

def setup_solution_matrix(self):
    A = np.zeros((self.ny, self.ny))
    