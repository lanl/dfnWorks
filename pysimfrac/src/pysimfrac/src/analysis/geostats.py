import numpy as np
from scipy import stats
import seaborn as sns
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


def single_field_correlation_length(A, num_lags, h):
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
        tmp : dict
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
    tmp = {
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

    return tmp


def compute_correlation_length(self, surface='all', num_lags=None):
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
        None
    
    """

    # default is to comput the correlation lengths for all 3 surfaces
    if surface == 'all':
        surfaces = ["aperture", "top", "bottom"]
        for sf in surfaces:
            print(f"\n--> Computing correlation length of {sf} field.")
            if sf == "aperture":
                self.correlation[sf] = single_field_correlation_length(
                    self.aperture, num_lags, self.h)
            elif sf == "top":
                self.correlation[sf] = single_field_correlation_length(
                    self.top, num_lags, self.h)
            elif sf == "bottom":
                self.correlation[sf] = single_field_correlation_length(
                    self.bottom, num_lags, self.h)

            print(
                f"--> Correlation length of {sf} field in the X-direction : {self.correlation[sf]['x']['correlation']:0.2e} [{self.units}] "
            )
            print(
                f"--> Correlation length in {sf} field in the Y-direction : {self.correlation[sf]['y']['correlation']:0.2e} [{self.units}] "
            )

    ## if a single surface is provided, just compute the correlation for that surface
    else:
        print(f"\n--> Computing correlation length of {surface} field.")
        if surface == "aperture":
            self.correlation[surface] = single_field_correlation_length(
                self.aperture, num_lags, self.h)
        elif surface == "top":
            self.correlation[surface] = single_field_correlation_length(
                self.top, num_lags, self.h)
        elif surface == "bottom":
            self.correlation[surface] = single_field_correlation_length(
                self.bottom, num_lags, self.h)
        else:
            print_error(
                f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', 'aperture', or 'all'"
            )

        print(
            f"--> Correlation length of {surface} field in the X-direction : {self.correlation[surface]['x']['correlation']:0.2e} [{self.units}] "
        )
        print(
            f"--> Correlation length in {surface} field in the Y-direction : {self.correlation[surface]['y']['correlation']:0.2e} [{self.units}] "
        )


def print_moments(self):
    """ Print the moments of the distribution to screen

    Parameters
    --------------------
        self : object
            simFrac Class
    
    Returns
    --------------------
        None

    Notes
    --------------------
        None
    
    """

    surfaces = ["aperture", "top", "bottom"]
    moments = ["mean", "variance", "skewness", "kurtosis"]
    # Check if the moments have been computed before printing them
    if self.moments["aperture"]["mean"] is None:
        self.compute_moments()

    # Print the moments to screen
    for surface in surfaces:
        for moment in moments:
            print(
                f"Field: {surface} - {moment}: {self.moments[surface][moment]:0.2e} [mm]"
            )
        print("")


def compute_moments(self):
    """ Compute the moments of the distribution to screen

    Parameters
    --------------------
        self : object
            simFrac Class
    
    Returns
    --------------------
        None

    Notes
    --------------------
        None
    
    """

    print("--> Computing moments of the surface and aperture field: Starting")

    surfaces = ["aperture", "top", "bottom"]
    for surface in surfaces:
        if surface == "aperture":
            A = np.reshape(self.aperture, self.nx * self.ny)
        elif surface == "top":
            A = np.reshape(self.top, self.nx * self.ny)
        elif surface == "bottom":
            A = np.reshape(self.bottom, self.nx * self.ny)
        self.moments[surface]["mean"] = np.mean(A)
        self.moments[surface]["variance"] = np.var(A)
        self.moments[surface]["skewness"] = stats.skew(A)
        self.moments[surface]["kurtosis"] = stats.kurtosis(A)
    self.print_moments()
    print("--> Computing moments of the surface and aperture field: complete")


def create_pdf(vals,
               num_bins,
               spacing="log",
               x=None,
               weights=None,
               a_low=None,
               a_high=None,
               bin_edge="center"):
    """  create pdf of vals 

    Parameters
    ----------
        vals : array
           array of values to be binned
        num_bins : int
            Number of bins in the pdf
        spacing : string 
            spacing for the pdf, options are linear and log
        x : array
            array of bin edges
        weights :array
            weights corresponding to vals to be used to create a weighted pdf
        a_low : float
            lower value of bin range. If no value provided 0.95*min(vals) is used
        a_high : float
            upper value of bin range. If no value is provided max(vals) is used
        bin_edge: string
            which bin edge is returned. options are left, center, and right

    Returns
    -------
        bx : array
            bin edges or centers (x values of the pdf)
        pdf : array
            values of the pdf, normalized so the Riemann sum(pdf*dx) = 1.
    """

    # Pick bin range
    if not a_low:
        a_low = np.min(vals)
    if not a_high:
        a_high = np.max(vals)

    # Create bins
    if not x:
        if spacing == "linear":
            x = np.linspace(a_low, a_high, num_bins + 1)
        elif spacing == "log":
            if min(a_low, a_high) > 0:
                x = np.logspace(np.log10(a_low), np.log10(a_high),
                                num_bins + 1)
            else:
                x = np.logspace(-10, 1, num_bins + 1, endpoint=False)
                A = np.max(x)
                B = np.min(x)
                x = (x - A) * (a_low - a_high) / (B - A) + a_high
        else:
            print("Warning. Unknown spacing type. Using Linear spacing")
            x = np.linspace(a_low, a_high, num_bins + 1)

    # Create PDF
    pdf, bin_edges = np.histogram(vals, bins=x, weights=weights, density=True)

    # Return arrays of the same size
    if bin_edge == "left":
        return bin_edges[:-1], pdf

    elif bin_edge == "right":
        return bin_edges[1:], pdf

    elif bin_edge == "center":
        bx = bin_edges[:-1] + 0.5 * np.diff(bin_edges)
        return bx, pdf

    else:
        print(f"Unknown bin edge type {bin_edge}. Returning left edges")
        return bin_edge[:-1], pdf


def create_cdf(vals, weights=None):
    """  Create emperical CDF of array 

    Parameters
    ----------
        vals : array
           array of values to be binned
        weights :array
            weights corresponding to vals to be used to create a weighted pdf

    Returns
    -------
        x : array
            x values of the cdf
        cdf : array
            values of the cdf, normalized so cummulative sum = 1
    """

    index_sort = np.argsort(vals)
    x = vals[index_sort]
    if weights is None:
        weights = np.ones(len(vals))
    cdf = weights[index_sort]
    cdf = np.cumsum(cdf) / cdf.sum()

    return (x, cdf)


def get_surface_pdf(self,
                    surface,
                    num_bins,
                    spacing="linear",
                    x=None,
                    weights=None,
                    a_low=None,
                    a_high=None,
                    bin_edge="center"):
    """  create probability density function of a surface 

    Parameters
    ----------
        surface : string
            Select the surface of the fracture, Acceptable surfaces are 'top', 'bottom', 'aperture'. 
        num_bins : int
            Number of bins in the pdf
        spacing : string 
            spacing for the pdf, options are linear and log, default is linear binning.
        x : array
            array of bin edges
        weights :array
            weights corresponding to vals to be used to create a weighted pdf
        a_low : float
            lower value of bin range. If no value provided 0.95*min(vals) is used
        a_high : float
            upper value of bin range. If no value is provided max(vals) is used
        bin_edge: string
            which bin edge is returned. options are left, center, and right

    Returns
    -------
        bx : array
            bin edges or centers (x values of the pdf)
        pdf : array
            values of the pdf, normalized so the Riemann sum(pdf*dx) = 1.
    """

    print(f"--> Getting PDF of {surface} surface")
    if surface == 'aperture':
        A = np.reshape(self.aperture, self.nx * self.ny)
    elif surface == "top":
        A = np.reshape(self.top, self.nx * self.ny)
    elif surface == "bottom":
        A = np.reshape(self.bottom, self.nx * self.ny)
    else:
        print_error(
            f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', 'aperture'"
        )
    x, pdf = create_pdf(A, num_bins, spacing, x, weights, a_low, a_high,
                        bin_edge)
    print(f"--> Getting PDF of {surface} surface: Done")
    return x, pdf


def get_surface_cdf(self, surface):
    """  create emperical CDF of surface of the fracture 

    Parameters
    ----------
        surface : string
            which surface of the fracture, Acceptable surfaces are 'top', 'bottom', 'aperture'. 

    Returns
    -------
        x : array
            x values of the cdf
        cdf : array
            y valyes of the cdf
          
    """

    print(f"--> Getting CDF of {surface} surface:")
    if surface == 'aperture':
        A = np.reshape(self.aperture, self.nx * self.ny)
    elif surface == "top":
        A = np.reshape(self.top, self.nx * self.ny)
    elif surface == "bottom":
        A = np.reshape(self.bottom, self.nx * self.ny)
    else:
        print_error(
            f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', 'aperture'"
        )
    x, cdf = create_cdf(A)
    print(f"--> Getting CDF of {surface} surface: Done")
    return x, cdf



def plot_surface_pdf(self, surface='all', bins='auto', figname=None):
    """  Plots the probability density function of the fracture surface / aperture

    Parameters
    --------------------
        surface : string
            which surface of the fracture, Acceptable surfaces are 'top', 'bottom', 'aperture', or 'all'. 
        bins : str, number, vector, or a pair of such values
            Generic bin parameter that can be the name of a reference rule, the number of bins, or the breaks of the bins.
        figname : str
            Name of figure to save. If None, so figure is saved. 

    Returns
    --------------------
        None

    Notes
    --------------------
        Uses Seaborn displot
          
    """

    if surface == "all":
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))
        fig.suptitle(
            f'Probability Density Functions of Fracture Surface heights',
            fontsize=16)
        # Check for ACF for all surfaces
        surfaces = ["top", "bottom", "aperture"]
        for i, sf in enumerate(surfaces):
            if sf == 'aperture':
                A = np.reshape(self.aperture, self.nx * self.ny)
            elif sf == "top":
                A = np.reshape(self.top, self.nx * self.ny)
            elif sf == "bottom":
                A = np.reshape(self.bottom, self.nx * self.ny)
            sns.histplot(data=A, bins=bins, ax=ax[i], kde=True, stat="density")

            # Set attributes
            ax[i].set_title(f'{sf}')
            if i == 0:
                ax[i].set_ylabel('PDF', fontsize=12)
            else:
                ax[i].set_ylabel('', fontsize=12)
            ax[i].set_xlabel(f'Surface height [{self.units}]', fontsize=12)

    else:
        print(f"--> Plotting PDF of {surface} surface")
        if surface == 'aperture':
            A = np.reshape(self.aperture, self.nx * self.ny)
        elif surface == "top":
            A = np.reshape(self.top, self.nx * self.ny)
        elif surface == "bottom":
            A = np.reshape(self.bottom, self.nx * self.ny)
        else:
            print_error(
                f"Error. Unknown surface provided - {surface}. Acceptable surfaces are 'top', 'bottom', 'aperture', or 'all'"
            )

        fig, ax = plt.subplots(figsize=(10, 10))
        fig.suptitle(f'PDF of {surface} values', fontsize=24)
        sns.histplot(data=A, bins=bins, ax=ax, kde=True, stat="density")
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel(f'Surface height [{self.units}]', fontsize=18)
        plt.ylabel(f'Probability Density Function', fontsize=18)
        print(f"--> Plotting PDF of {surface} surface: complete")

    # Save figure if the user wants it
    if figname:
        print(f"\n--> Saving figure to file {figname}")
        plt.savefig(figname, dpi=150)

    return fig, ax

