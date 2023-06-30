
import numpy as np
from scipy import stats
import matplotlib.pylab as plt

from pysimfrac.src.general.helper_functions import print_error


def find_first_zero_crossing(lags, acf):
    """ Finds the first zero crossing of the autocorrelation function and returns the corresponding distance where the crossing occurs

    Parameters
    --------------------
        lags : numpy array
            Distances of the autocorrelation functoin
        acf : numpy array
            Autocorrelation function values

    Returns
    --------------------
        value : float 
            Distance where acf first crossing the zero line

    Notes
    --------------------
        Returns -1 is acf does not cross 0 
    
    
    """
    for i, val in enumerate(acf):
        if val < 0:
            return lags[i]
    return -1


def autocorr(x, lag=1):
    """ Computes the autocorrelation function at a distance of lag

    Parameters
    --------------------
        x : numpy array
            field values (1D array)
        lag : int
            lag distance

    Returns
    --------------------
        correlation : float
            correlation at distance of lag

    Notes
    --------------------
        None
    
    """
    return np.corrcoef(np.array([x[0:len(x) - lag], x[lag:len(x)]]))[0, 1]


def compute_autocorr_y(A, num_lags=None):

    # clear this garbage up dude
    [n, _] = np.shape(A)
    if not num_lags:
        num_lags = int(0.25 * n)
    tmp = np.zeros((n, num_lags))

    for j in range(n):
        B = A[j, :]
        for i in range(num_lags):
            tmp[j, i] = autocorr(B, i)

    acf = np.zeros(num_lags)
    for i in range(num_lags):
        acf[i] = np.mean(tmp[:, i])

    lags = np.array(range(num_lags)).astype(float)
    return lags, acf


def compute_autocorr_x(A, num_lags=None):

    [_, m] = np.shape(A)
    if not num_lags:
        num_lags = int(0.25 * m)
    tmp = np.zeros((m, num_lags))

    for j in range(m):
        B = A[:, j]
        for i in range(num_lags):
            tmp[j, i] = autocorr(B, i)

    acf = np.zeros(num_lags)
    for i in range(num_lags):
        acf[i] = np.mean(tmp[:, i])

    lags = np.array(range(num_lags)).astype(float)
    return lags, acf


def single_field_acf(A, num_lags, h):
    """ Compute the correlation length of a field, both in x and y direction.

    Parameters
    --------------------
        A : numpy array
            field values (2D array)
        num_lag : int
            maximum number of lags
        h : float
            discretization length scale 

    Returns
    --------------------
        acf_dict : dict
            dictionary with values of the correlation length, lags, and autocorrelation function in both x and y direction

    Notes
    --------------------
        None
    
    """

    ## Compute Autocorrelation function in x direction
    lags_x, acf_x = compute_autocorr_x(A, num_lags)
    lags_x *= h
    ## compute first zero crossing of ACF in X
    corr_x = find_first_zero_crossing(lags_x, acf_x)

    ## Compute Autocorrelation function in y direction
    lags_y, acf_y = compute_autocorr_y(A, num_lags)
    lags_y *= h
    ## compute first zero crossing of ACF in Y
    corr_y = find_first_zero_crossing(lags_y, acf_y)

    ## create dictionary holding all the autocorrelation information
    acf_dict = {
        "x": {
            "correlation": corr_x,
            "lags": lags_x,
            "acf": acf_x
        },
        "y": {
            "correlation": corr_y,
            "lags": lags_y,
            "acf": acf_y
        },
        "anisotropy": corr_x / corr_y
    }

    return acf_dict


def compute_acf(self, surface='all', num_lags=None):
    """ Compute the correlation length of a field, both in x and y direction.

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Named of desired surface to plot. Options are 'aperture', 'top', 'bottom', and 'all'(default). 
        num_lag : int
            Maximum number of lags. If no value is provided, num_lags is set to 1/4 the domain size in that direction. 

    Returns
    --------------------
        None

    Notes
    --------------------
        Autocorrelation functions and first crossing estimates of correlation lengths are attached to the simfrac object. 
    
    """

    # default is to comput the correlation lengths for all 3 surfaces
    if surface == 'all':
        surfaces = ["aperture", "top", "bottom"]
        for sf in surfaces:
            print(f"\n--> Computing correlation length of {sf} field.")
            if sf == "aperture":
                self.acf[sf] = single_field_acf(
                    self.aperture, num_lags, self.h)
            elif sf == "top":
                self.acf[sf] = single_field_acf(
                    self.top, num_lags, self.h)
            elif sf == "bottom":
                self.acf[sf] = single_field_acf(
                    self.bottom, num_lags, self.h)

            print(
                f"--> Correlation length of {sf} field in the X-direction : {self.acf[sf]['x']['correlation']:0.2e} [{self.units}] "
            )
            print(
                f"--> Correlation length in {sf} field in the Y-direction : {self.acf[sf]['y']['correlation']:0.2e} [{self.units}] "
            )

    ## if a single surface is provided, just compute the correlation for that surface
    else:
        print(f"\n--> Computing correlation length of {surface} field.")
        if surface == "aperture":
            self.acf[surface] = single_field_acf(
                self.aperture, num_lags, self.h)
        elif surface == "top":
            self.acf[surface] = single_field_acf(
                self.top, num_lags, self.h)
        elif surface == "bottom":
            self.acf[surface] = single_field_acf(
                self.bottom, num_lags, self.h)
        else:
            print_error(
                f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', 'aperture', or 'all'"
            )

        print(
            f"--> Correlation length of {surface} field in the X-direction : {self.acf[surface]['x']['correlation']:0.2e} [{self.units}] "
        )
        print(
            f"--> Correlation length in {surface} field in the Y-direction : {self.acf[surface]['y']['correlation']:0.2e} [{self.units}] "
        )


def plot_acf(self, surface="all", figname=None):
    """ Creates a plot of the autocorrelation function for surfaces. 

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Name of desired surface acf to plot. Options are 'aperture', 'top', 'bottom', or 'all'. Default value is 'all'
        figname : str
            Name of figure to be saved. If figname is None (default), then no figure is saved. 

    Returns
    --------------------
        fig : Figure
        ax : Axes 

    Notes
    --------------------
        The autocorrelation functions will be computed if they have not be computed already. 
    
    """

    if surface == "all":
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))
        fig.suptitle(f'Autocorrelation Function of Fracture Surfaces',
                     fontsize=16)
        # Check for ACF for all surfaces
        surfaces = ["top", "bottom", "aperture"]
        for i, sf in enumerate(surfaces):
            # If the ACF hasn't been computed yet, do that first.
            if not self.acf[sf]["anisotropy"]:
                print(
                    f"ACF for {sf} field was not computed yet. Doing that now."
                )
                self.compute_acf(sf)

            ## Make subplot for current surface
            p = ax[i].plot(self.acf[sf]['x']['lags'],
                           self.acf[sf]['x']['acf'],
                           label="X-Direction")
            ax[i].plot(self.acf[sf]['x']['correlation'],
                       0,
                       color=p[0].get_color(),
                       marker="s",
                       markersize=10)
            p = ax[i].plot(self.acf[sf]['y']['lags'],
                           self.acf[sf]['y']['acf'],
                           label="Y-Direction")
            ax[i].plot(self.acf[sf]['y']['correlation'],
                       0,
                       color=p[0].get_color(),
                       marker="d",
                       markersize=10)

            # Set attributes
            ax[i].set_title(f'{sf}')
            if i == 0:
                ax[i].set_ylabel('ACF', fontsize=18)
            ax[i].set_xlabel(f"Distance [{self.units}]", fontsize=18)
            if i == 2:
                ax[i].legend(fontsize=16)
            ax[i].grid(True)
            ax[i].axis([
                0,
                max(max(self.acf[sf]['x']['lags']),
                    max(self.acf[sf]['y']['lags'])), -0.6, 1
            ])

    else:
        # Check for ACF for spe
        if not self.acf[surface]["anisotropy"]:
            print(
                f"ACF for {surface} field was not computed yet. Doing that now."
            )
            self.compute_acf(surface)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(f'Autocorrelation function of {surface} field',
                     fontsize=24)
        p = ax.plot(self.acf[surface]['x']['lags'],
                    self.acf[surface]['x']['acf'],
                    label="X-Direction")
        ax.plot(self.acf[surface]['x']['correlation'],
                0,
                color=p[0].get_color(),
                marker="s",
                markersize=20)
        p = ax.plot(self.acf[surface]['y']['lags'],
                    self.acf[surface]['y']['acf'],
                    label="Y-Direction")
        ax.plot(self.acf[surface]['y']['correlation'],
                0,
                color=p[0].get_color(),
                marker="d",
                markersize=20)

        plt.ylabel('ACF', fontsize=18)
        plt.xlabel(f"Distance [{self.units}]", fontsize=18)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax.legend(fontsize=18)
        plt.grid(True)

    # Save figure if the user wants it
    if figname:
        print(f"\n--> Saving figure to file {figname}")
        plt.savefig(figname, dpi=150)

    return fig, ax

