"""
dfnGen uses the mean and standard deviation of the underlying normal distribution that creates the lognormal distribution. 

This script provides a way for the user to convert the desired mean and variance of the lognormal into parameters for dfnGen. 

In order to produce a LogNormal distribution with a desired mean (m) and variance (s) one uses

mu = ln [ m^2 / sqrt(m^2 + s^2)]

and 

sigma = ln ( 1 + m^2 / s^2)

For more details see https://en.wikipedia.org/wiki/Log-normal_distribution
"""

import sys
import numpy as np

def get_mu_and_sigma(m,s):
    mu = np.log(m**2/np.sqrt(m**2 + s**2))
    sigma2 = np.sqrt(np.log(1 + s**2/m**2))
    return mu,sigma2

if __name__ == '__main__':

    print("Running lognormal_params.py\n")
    if len(sys.argv) != 3:
        print(f"Incorrect number of command line args. {len(sys.argv)} values provide.\nRequired format is\n>> python lognormal_params.py [mean_of_lognormal] [variance_of_lognormal]")
        sys.exit(1)
    else:
        mean_of_lognormal = float(sys.argv[1])
        variance_of_lognormal = float(sys.argv[2])
        print(f"Desired mean of Log-normal_distribution {mean_of_lognormal}")
        print(f"Desired variance of Log-normal_distribution {variance_of_lognormal}\n")
    mu,sigma2 = get_mu_and_sigma(mean_of_lognormal,variance_of_lognormal)
    print(f"Mean of underlying normal distribution {mu:0.3f}")
    print(f"Variance of underlying normal distribution {sigma2:0.3f}")

