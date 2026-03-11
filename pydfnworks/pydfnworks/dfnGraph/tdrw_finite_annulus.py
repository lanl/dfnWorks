
import numpy as np
import mpmath as mp


def Psi_star_annulus(lmbda, eps, tau0, tau1):
    # Laplace transform of the CDF for diffusion return time in a cylindrical annulus
    #
    # Geometry: cylindrical annulus with inner radius r0 (absorbing, fracture-matrix
    # interface) and outer radius r1 (reflecting, block interior).
    # A particle is released at r' = r0*(1+eps), just inside the absorbing wall.
    #
    # Parameters:
    #   eps  = (r' - r0) / r1   dimensionless release position  (0 < eps << 1)
    #   tau0 = r0^2 / D         inner-radius diffusion timescale
    #   tau1 = r1^2 / D         outer-radius diffusion timescale
    #
    # Bessel functions: mpmath besseli / besselk
    #   mpmath.besseli(n, x) = In(x)    (modified Bessel, first kind)
    #   mpmath.besselk(n, x) = Kn(x)    (modified Bessel, second kind)
    #
    # Stability switch: when |s*tau1| > 100 the unscaled Bessels overflow.
    # Use explicitly scaled forms:
    #   Ie(n,x) = exp(-x) * In(x)   ->   mp.besseli(n,x) * mp.exp(-x)
    #   Ke(n,x) = exp(x)  * Kn(x)   ->   mp.besselk(n,x) * mp.exp(x)
    # with compensating exponential prefactors so the ratio stays finite.
    #
    # F_cdf(s) = F_psi(s) / s

    eps  = mp.mpf(eps)
    tau0 = mp.mpf(tau0)
    tau1 = mp.mpf(tau1)

    arg0     = mp.sqrt(lmbda * tau0)       # sqrt(s * tau0)
    arg0_eps = (1 + eps) * arg0            # (1+eps) * sqrt(s * tau0)
    arg1     = mp.sqrt(lmbda * tau1)       # sqrt(s * tau1)

    if abs(complex(lmbda * tau1)) > 100:
        # scaled Bessels with explicit exponential prefactors
        # matches MATLAB besseli(n,x,1) and besselk(n,x,1)
        I0e_eps = mp.besseli(0, arg0_eps) * mp.exp(-arg0_eps)
        K0e_eps = mp.besselk(0, arg0_eps) * mp.exp( arg0_eps)
        I0e_0   = mp.besseli(0, arg0)     * mp.exp(-arg0)
        K0e_0   = mp.besselk(0, arg0)     * mp.exp( arg0)
        I1e_1   = mp.besseli(1, arg1)     * mp.exp(-arg1)
        K1e_1   = mp.besselk(1, arg1)     * mp.exp( arg1)

        # numerator: exp((2+eps)*sqrt(s*tau0) - 2*sqrt(s*tau1)) * I0e_eps * K1e_1
        #          + exp(-eps*sqrt(s*tau0)) * K0e_eps * I1e_1
        exp_num1 = mp.exp((2 + eps) * arg0 - 2 * arg1)
        exp_num2 = mp.exp(-eps * arg0)
        numerator = exp_num1 * I0e_eps * K1e_1 + exp_num2 * K0e_eps * I1e_1

        # denominator: exp(2*sqrt(s*tau0) - 2*sqrt(s*tau1)) * I0e_0 * K1e_1
        #            + K0e_0 * I1e_1
        exp_den     = mp.exp(2 * arg0 - 2 * arg1)
        denominator = exp_den * I0e_0 * K1e_1 + K0e_0 * I1e_1

    else:
        # standard unscaled Bessel functions, safe for |s*tau1| <= 100
        I0_eps = mp.besseli(0, arg0_eps)
        K0_eps = mp.besselk(0, arg0_eps)
        I0_0   = mp.besseli(0, arg0)
        K0_0   = mp.besselk(0, arg0)
        I1_1   = mp.besseli(1, arg1)
        K1_1   = mp.besselk(1, arg1)

        numerator   = I0_eps * K1_1 + K0_eps * I1_1
        denominator = I0_0   * K1_1 + K0_0   * I1_1

    return numerator / (denominator * lmbda)


def Psi_pdf_star_annulus(lmbda, eps, tau0, tau1):
    # Laplace transform of the first-passage time PDF
    # psi*(s) = s * F_cdf(s)  (removes the 1/s factor)
    return Psi_star_annulus(lmbda, eps, tau0, tau1) * lmbda


def Psi_cdf_annulus(t, eps, tau0, tau1, method="dehoog"):
    # Inverse Laplace transform of Psi_star_annulus at time t
    # Returns cumulative return-time distribution P(T_return <= t)
    if t <= 0:
        return mp.mpf("0.0")
    F = lambda s: Psi_star_annulus(s, eps, tau0, tau1)
    return mp.invertlaplace(F, t, method=method)


def Psi_pdf_annulus(t, eps, tau0, tau1, method="dehoog"):
    # Inverse Laplace transform of the first-passage time density psi(t)
    # Inverts psi*(s) directly for accuracy
    if t <= 0:
        return mp.mpf("0.0")
    F = lambda s: Psi_pdf_star_annulus(s, eps, tau0, tau1)
    return mp.invertlaplace(F, t, method=method)


def _make_inverse_cdf_annulus(num_samples=100, eps=1e-2, tau0=1e-4, tau1=1e0, precision=40):
    # Precompute the inverse CDF table for cylindrical annulus return-time sampling
    #
    # Default parameters match InvLaplace.m:
    #   eps  = 1e-2   dimensionless release position (r'-r0)/r1
    #   tau0 = 1e-4   inner-radius timescale r0^2/D  (dimensionless, tau0/tau1)
    #   tau1 = 1e0    outer-radius timescale r1^2/D  (reference, = 1)
    #
    # Returns (times, cdf_vals) arrays for use with np.interp
    mp.mp.dps = precision

    times    = [10**x for x in np.linspace(-8, 3, num_samples)]
    cdf_vals = np.zeros(num_samples, dtype=float)

    for i, t in enumerate(times):
        cdf_vals[i] = float(Psi_cdf_annulus(t, eps, tau0, tau1, method="dehoog"))

    # sort by cdf value to build the inverse CDF (cdf -> time) lookup
    order      = np.argsort(cdf_vals)
    cdf_sorted = np.clip(cdf_vals[order], 0, 1)
    t_sorted   = np.maximum(np.array(times)[order], 0)

    # remove duplicate cdf values to ensure monotone interpolation
    cdf_unique, idx = np.unique(cdf_sorted, return_index=True)
    t_unique = np.asarray(t_sorted[idx])

    return t_unique, cdf_unique


def limited_matrix_diffusion_annulus(self, G):
    """ Matrix diffusion with finite cylindrical annular block geometry

    Parameters
    ----------
        G : NetworkX graph
            graph obtained from graph_flow

    Returns
    -------
        None

    Notes
    -----
        Samples diffusion return times from a finite cylindrical annular
        matrix block. The inner radius r0 is the absorbing fracture-matrix
        interface; the outer radius r1 is the reflecting block interior.
        A particle is released at r' = r0*(1 + eps), just inside the
        absorbing wall.

        The Laplace-domain solution uses modified Bessel functions I0, I1,
        K0, K1 from the cylindrical geometry, unlike the slab (Dentz) model
        which uses hyperbolic functions.

        Two diffusion timescales parameterize the geometry:
            tau0 = r0^2 / D   (inner radius timescale)
            tau1 = r1^2 / D   (outer radius timescale)

        tau1 is stored on the particle as self.tau_D and used to rescale
        dimensionless sampled return times to physical times [s].

        The inverse CDF table (self.transfer_time, self.trans_prob) must
        be precomputed via _make_inverse_cdf_annulus and attached to the
        particle before transport begins.

        All other parameters are attached to the particle class.
    """

    eps = 1e-2
    b = G.edges[self.curr_node, self.next_node]['b']

    # trapping rate into the cylindrical matrix block
    gamma = (2 * self.matrix_porosity * self.matrix_diffusivity) / (b * eps * self.fracture_spacing)

    # average number of trapping events during this advective step
    average_number_of_trapping_events = self.delta_t * gamma

    # sample number of trapping events from Poisson distribution
    n = np.random.poisson(average_number_of_trapping_events)

    # sample uniform random variables and map to return times via inverse CDF
    # self.tau_D = r1^2 / D rescales dimensionless times to physical times
    xi  = np.random.uniform(size=n)
    tmp = self.tau_D * np.interp(xi, self.trans_prob, self.transfer_time)

    self.delta_t_md = tmp.sum()
