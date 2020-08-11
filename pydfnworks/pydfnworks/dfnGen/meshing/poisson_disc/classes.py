import cfg as c
import numpy as np
import math
from random import random
class quasirandom:
    """ naive quasi random-number generator"""
    def __init__(self):
        self.seed=random()
        self.i=0
        self.phi=2/(np.sqrt(5)+1)
    def next(self):
        self.seed=(self.seed+self.i*self.phi)%1
        self.i=self.i+1
        return self.seed
    def count(self):
        return self.i
    def reset(self):
        self.i=0

