
import numpy as np
import skgstat as skg
import matplotlib.pylab as plt

from pysimfrac.src.general.helper_functions import print_error, print_warning

## Variogram is computed using scikit-gstat
## https://scikit-gstat.readthedocs.io
## Returns Variogram object
##
## Mirko Mälicke, Egil Möller, Helge David Schneider, & Sebastian Müller. (2021, May 28).
##
## mmaelicke/scikit-gstat: A scipy flavoured geostatistical variogram analysis toolbox (Version v0.6.0). Zenodo. http://doi.org/10.5281/zenodo.4835779
##
## 
def single_field_variogram(self, surface, num_samples, max_lag, num_lags, model):
    """ Compute the variogram of a single field using scikit-gstat

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Name of desired surface acf to plot. Options are 'aperture', 'top', or 'bottom'
        num_samples : int
            Number of random samples used to compute the variogram
        max_lag : int
            Maximum lag distance (unitless length).
        num_lags : int
            Number of lag bins. Default is 10
        model : str
            See https://scikit-gstat.readthedocs.io for model details. Default is spherical

    Returns
    -------------
        None


    Notes
    -----------------
        scikit-gstat variogram object is attached to the simFrac object. 

        Requesting more than 10,000 samples can take a while.  
    """

    if num_samples > 10000:
        print_warning("--> A LOT of samples were requested. We don't recomend more than 10,000.  Just to let you know, this might take a while. Why don't you go get a coffee or maybe check your email. Okay?")
    index_x = np.random.randint(0, self.nx, num_samples)
    index_y = np.random.randint(0, self.ny, num_samples)
    indices = np.c_[index_y, index_x]
    if surface == "aperture":
        values = np.fromiter( (self.aperture[c[0], c[1]] for c in indices), dtype=float)
    elif surface == "top":
        values = np.fromiter((self.top[c[0], c[1]] for c in indices), dtype=float)
    elif surface == "bottom":
        values = np.fromiter((self.bottom[c[0], c[1]] for c in indices), dtype=float)
    else:
        print_error(
            f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', or 'aperture''"
        )
    ## Make the variogram using SciKit - gstat
    self.variogram[surface] = skg.Variogram(indices, values, model = model, maxlag = max_lag, n_lags = num_lags)
    
def compute_variogram(self, surface = 'all', num_samples = 500, max_lag = None, num_lags = 10, model = 'spherical',):
    """ Compute the variogram of the surface using scikit-gstat.  

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Name of desired surface acf to plot. Options are 'aperture', 'top', 'bottom', or 'all'. Default value is 'all'
        num_samples : int
            Number of random samples used to compute the variogram
        max_lag : int
            Maximum lag distance (unitless length).
        num_lags : int
            Number of lag bins. Default is 10
        model : str
            See https://scikit-gstat.readthedocs.io for model details. Default is spherical

    Returns
    -------------
        None

    Notes
    -----------------
        scikit-gstat variogram object is attached to the simFrac object. 

        Reference:
        Mirko Mälicke, Egil Möller, Helge David Schneider, & Sebastian Müller. (2021, May 28).

        mmaelicke/scikit-gstat: A scipy flavoured geostatistical variogram analysis toolbox (Version v0.6.0). Zenodo. http://doi.org/10.5281/zenodo.4835779


    """


  # default is to comput the correlation lengths for all 3 surfaces
    if surface == 'all':
        surfaces = ["aperture", "top", "bottom"]
        for sf in surfaces:
            print(f"\n--> Computing variogram of {sf} field.")
            #single_field_variogram(self, surface, num_samples, max_lag, num_lags, model)
            self.single_field_variogram(sf, num_samples, max_lag, num_lags, model)
    ## if a single surface is provided, just compute the correlation for that surface
    else:
        print(f"\n--> Computing variogram of {surface} field.")
        self.single_field_variogram(surface, num_samples, max_lag, num_lags, model)

def plot_variogram(self, surface="all", figname=None, show_lags = False):
    """ Creates a plot of the autocorrelation function for surfaces. 

    Parameters
    --------------------
        self : object
            simFrac Class
        surface : str
            Name of desired surface acf to plot. Options are 'aperture', 'top', 'bottom', or 'all'. Default value is 'all'
        figname : str
            Name of figure to be saved. If figname is None (default), then no figure is saved. 
        show_lags : bool
            True / False plot variogram as a function of Lag (unitless) or Lag Distance (units of grid resolution)

    Returns
    --------------------
        None

    Notes
    --------------------
        None
    
    """

    if surface == "all":
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))
        fig.suptitle(f'Variograms of Fracture Surfaces',
                     fontsize=16)
        # Check for ACF for all surfaces
        surfaces = ["top", "bottom", "aperture"]
        for i, sf in enumerate(surfaces):
            # If the variogram hasn't been computed yet, exit
            if not self.variogram[sf]:
                print(
                    f"variogram for {sf} field was not computed yet. Doing that now."
                )
                self.compute_variogram(sf)
            ## Make subplot for current surface
            # self.variogram[sf].plot(axes = ax[i], grid = False)
            # get the parameters
            _bins = self.variogram[sf].bins
            _exp = self.variogram[sf].experimental
            x = np.linspace(0, np.nanmax(_bins), 100)
            # apply the model
            y = self.variogram[sf].transform(x)
            if show_lags:
                ax[i].plot(_bins, _exp, '.b', label = "Data")
                ax[i].plot(x, y, '-g', label = f"Model")
                ax[i].set_xlabel(f"Lag [-]", fontsize=18)
            else:
                ax[i].plot(_bins*self.h, _exp, '.b', label = "Data")
                ax[i].plot(x*self.h, y, '-g', label = f"Model")
                ax[i].set_xlabel(f"Lag Distance [{self.units}]", fontsize=18)
            # Set attributes
            ax[i].set_title(f'{sf}')
            ax[i].grid(True)
            if i == 0:
                ax[i].set_ylabel('Semivariogram', fontsize=18)
            if i == 2:
                ax[i].legend(fontsize = 18, loc = 4)
    else:
        # Check for variogram for specific surface
        if not self.variogram[surface]:
            print(
                f"variogram for {surface} field was not computed yet. Doing that now."
            )
            self.compute_variogram(surface)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(f'Variogram of {surface} field',
                     fontsize=24)
        # get the parameters
        _bins = self.variogram[surface].bins
        _exp = self.variogram[surface].experimental
        x = np.linspace(0, np.nanmax(_bins), 100)
        # apply the model
        y = self.variogram[surface].transform(x)

        if show_lags:
            ax.plot(_bins, _exp, '.b', markersize = 8, label = "Data")
            ax.plot(x, y, '-g', label = f"Model")
            ax.set_xlabel(f"Lag [-]", fontsize=18)
        else:
            ax.plot(_bins*self.h, _exp, '.b', markersize = 8,  label = "Data")
            ax.plot(x*self.h, y, '-g', label = f"Model")
            ax.set_xlabel(f"Lag Distance [{self.units}]", fontsize=18)
        
        ax.set_ylabel('Semivariogram', fontsize=18)
        # ax.set_xlabel(f"Lag Distance [{self.units}]", fontsize=18)
        ax.legend(fontsize = 18, loc = 4)
        ax.grid(True)
        plt.xticks(fontsize = 14)
        plt.yticks(fontsize = 14)

    # Save figure if the user wants it
    if figname:
        print(f"\n--> Saving figure to file {figname}")
        plt.savefig(figname, dpi=150)

    return fig, ax

