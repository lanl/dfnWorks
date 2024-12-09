"""
  :filename: distributions.py
  :synopsis: Analytic expressions for fracture radii distributions
  :version: 1.0
  :maintainer: Jeffrey Hyman 
  :moduleauthor: Jeffrey Hyman <jhyman@lanl.gov>
"""

from scipy import stats, special
import numpy as np


##### Truncated Power Law Distribution Functions ########
def tpl_cdf(xmin, alpha, x):
    """ Returns the analytical values of the power law CDF with exponent a

    Parameters
    --------------
        xmin : double
            The lower bound of the truncated power law distribution.
        alpha  : double
             The alpha parameter in the power law distribution.
        x : numpy array
            x values

    Returns
    ----------
        cdf : numpy array
            Analytical values of the power law CDF
    """
    cdf = 1 - ((xmin / x)**alpha)
    return cdf


def tpl_pdf(norm_const, xmin, alpha, x):
    """ Returns the analytical power laws PDF values.

    p(r) \propto x ^ -{alpha+1}

    Parameters
    --------------
        norm_const : double 
            The normalization constant for the PDF
        xmin : double
            The lower bound of the truncated power law distribution.
        alpha  : double
             The alpha parameter (decay rate / exponent) in the power law distribution.
        x : numpy array
            x-values of the function
    Returns
    --------
        pdf : numpy array
            Analytical values of the power law PDF

    """
    pdf = norm_const * ((alpha * (xmin**alpha)) / x**(alpha + 1))
    return pdf


def tpl(alpha, xmin, xmax):
    """ Returns the PDF and CDF of a truncated Power-law distribution with exponent alpha over the range [xmin,xmax]. 
    
    Parameters
    -----------
        alpha  : double
             The alpha parameter (decay rate / exponent) in the power law distribution. (alpha > 0)
        xmin : double
            Minimum x-value
        xmax : double
            Maximum x-value

    Returns
    ---------
        x : numpy array
            x-values of the function
        pdf : numpy array
            pdf values of the truncated powerlaw
        cdf : numpy array
            cdf values of truncated powerlaw distribution

    Notes
    -------
        dfnWorks uses the convention of pdf(x) = C x^{-(alpha +1)}, rather than pdf(x) = C x^{-alpha} for a powerlaw.

    """

    x = np.linspace(xmin, xmax, 1000)
    norm_const = 1.0 / (tpl_cdf(xmin, alpha, xmax) -
                        tpl_cdf(xmin, alpha, xmin))
    pdf = tpl_pdf(norm_const, xmin, alpha, x)
    cdf = tpl_cdf(xmin, alpha, x)
    return x, pdf, cdf


##### Exponential Distribution Functions ########
def exp_pdf(norm_const, eLambda, x):
    """ Returns the analytical values of the PDF of the exponential distribution with exponent eLambda for values of x.

    Parameters
    -------------
        norm_const : double 
            The normalization constant for the PDF
        eLambda  : double
            The exponent of the exponential distribution
        x : numpy array
            x-values of the function
    Returns
    --------
        pdf : numpy array
            Analytical values of the power law PDF

    Notes
    ---------
        None
    """
    pdf = norm_const * eLambda * np.e**(-eLambda * x)
    return pdf


def exp_cdf(eLambda, x, xmin):
    """ Returns the analytical values of the CDF of the exponential distribution with exponent eLambda for values of x.

    Parameters
    -------------
        eLambda  : double
            The exponent of the exponential distribution
        x : numpy array
            x-values of the function
    Returns
    --------
        cdf : numpy array
            Analytical values of the exponential CDF

    Notes
    ---------
        None
    """
    cdf = 1 - (np.e**(-eLambda * (x - xmin)))
    return cdf


def exponential(eLambda, xmin, xmax):
    """ Returns the PDF and CDF of an exponential distribution with exponent eLambda over the range [xmin,xmax]. 
    
    Parameters
    -----------
        eLambda  : double
            The exponent of the exponential distribution
        xmin : double
            Minimum x-value
        xmax : double
            Maximum x-value

    Returns
    ---------
        x : numpy array
            x-values of the function
        pdf : numpy array
            pdf values of the exponential distribution
        cdf : numpy array
            cdf values of exponential distribution

    Notes
    -------
        None

    """
    x = np.linspace(xmin, xmax, 1000)
    const = 1.0 / (exp_cdf(eLambda, xmax, xmin) - exp_cdf(eLambda, xmin, xmin))
    pdf = exp_pdf(const, eLambda, x)
    cdf = exp_cdf(eLambda, x, xmin)
    return x, pdf, cdf


##### Log-Normal Distribution Functions ########
def lognormal_cdf(x, mu, sigma):
    """ Returns the analytical values of the CDF of the lognormal distribution with parameters mu and sigma

    Parameters
    -------------
        x : numpy array
            x-values of the function
        mu  : double
            Lognormal distribution parameter #1
        sigma : double
            Lognormal distribution parameter #1 (sigma > 0)            
    Returns
    --------
        cdf : numpy array
            Analytical values of the CDF for the Log-Normal distribution

    Notes
    ---------
        None
    """
    cdf = 0.5 + (0.5 * special.erf((np.log(x) - mu) / (np.sqrt(2) * sigma)))
    return cdf


def lognormal_pdf(x, mu, sigma):
    """ Returns the analytical values of the CDF of the lognormal distribution with parameters mu and sigma

    Parameters
    -------------
        x : numpy array
            x-values of the function
        mu  : double
            Lognormal distribution parameter #1
        sigma : double
            Lognormal distribution parameter #1 (sigma > 0)            
    Returns
    --------
        pdf : numpy array
            Analytical values of the PDF for the Log-Normal distribution

    Notes
    ---------
        None
    """
    constant = 1 / (x * sigma * np.sqrt(2 * np.pi))
    exp_term = (-1.0 * (np.log(x) - mu)**2 / (2 * sigma**2))
    pdf = constant * np.exp(exp_term)
    return pdf


def lognormal(mu, sigma, xmin, xmax):
    """ Returns the PDF and CDF of a LogNormal distribution with parameters mu and sigma over the range [xmin,xmax]. 
    
    Parameters
    -----------
        mu  : double
            Lognormal distribution parameter #1
        sigma : double
            Lognormal distribution parameter #1 (sigma > 0)
        xmin : double
            Minimum x-value
        xmax : double
            Maximum x-value

    Returns
    ---------
        x : numpy array
            x-values of the function
        pdf : numpy array
            pdf values of the lognormal distribution
        cdf : numpy array
            cdf values of lognormal distribution

    Notes
    -------
        dfnGen uses the mean and standard deviation of the underlying normal distribution that creates the lognormal distribution. 

        In order to produce a LogNormal distribution with a desired mean (m) and variance (s) one uses

        mu = ln [ m^2 / sqrt(m^2 + s^2)]

        and 

        sigma = ln ( 1 + m^2 / s^2)

        For more details see https://en.wikipedia.org/wiki/Log-normal_distribution
"""

    x = np.linspace(xmin, xmax, 1000)
    const = 1.0 / (lognormal_cdf(xmax, mu, sigma) -
                   lognormal_cdf(xmin, mu, sigma))
    pdf = lognormal_pdf(x, mu, sigma)
    cdf = lognormal_cdf(x, mu, sigma)
    return x, pdf, cdf


def create_ecdf(vals):
    """  Returns the Empirical Cumulative Density function of provided values 

    Parameters
    ----------
        vals : array
           array of values to be binned

    Returns
    -------
        x : numpy array
            sorted input values
        cdf : numpy array
            values of the cdf, normalized so cumulative sum = 1

    Notes
    ------
        None

    """

    vals.sort()
    cdf = np.ones(len(vals))
    cdf = np.cumsum(cdf) / sum(cdf)
    return vals, cdf
