Fracture Orientation
**************************************************

The orientation of each fracture is defined by its unit normal vector. For a stochastic family, normals are sampled around a mean orientation with either the von Mises-Fisher distribution or the Bingham distribution. These are set with the orientation arguments of ``DFN.add_fracture_family`` (see :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>`), which apply to both ellipse and rectangle families.

.. code-block:: python

    # Fisher distribution (default) around trend 90, plunge 30
    DFN.add_fracture_family(shape="ell", distribution="tpl", alpha=1.8,
                            min_radius=1.0, max_radius=10.0, p32=0.5,
                            orientation_distribution="fisher",
                            trend=90.0, plunge=30.0, kappa=30)

    # Bingham distribution: an elongated cluster around trend 90, plunge 30
    DFN.add_fracture_family(shape="rect", distribution="tpl", alpha=1.8,
                            min_radius=1.0, max_radius=10.0, p32=0.5,
                            orientation_distribution="bingham",
                            trend=90.0, plunge=30.0, kappa1=-30, kappa2=-5)

After generation, the strike, dip, trend, and plunge of every fracture are available as ``DFN.strike``, ``DFN.dip``, ``DFN.trend``, and ``DFN.plunge``.

----

Mean Orientation
=================================

The mean orientation of a family is given in one of three coordinate systems. The system is chosen by which pair of arguments is passed to ``add_fracture_family``, and is stored in :ref:`orientationOption`. The same system must be used for all families.

| 0 : Spherical coordinates (:ref:`theta` / :ref:`phi`)
| 1 : Trend / Plunge (:ref:`trend` / :ref:`plunge`)
| 2 : Dip / Strike (:ref:`dip` / :ref:`strike`)

Spherical Coordinates
----------------------------------

The mean normal vector of the fracture family :math:`\vec{n}` is related to the spherical coordinates :math:`\theta` and :math:`\phi` by

.. math::
    \vec{n}_x = \sin(\theta) \cos(\phi), \quad
    \vec{n}_y = \sin(\theta) \sin(\phi), \quad
    \vec{n}_z = \cos(\theta)

theta
^^^^^^^^^^^^^^

Description: Angle the normal vector of the fracture makes with the z-axis. Stored as ``etheta`` / ``rtheta`` in ``DFN.params``.

phi
^^^^^^^^^^^^^^

Description: Angle that the projection of the normal vector of a fracture onto the x-y plane makes with the x-axis. Stored as ``ephi`` / ``rphi`` in ``DFN.params``.

.. note:: Both radians and degrees are supported for spherical coordinates. Use :ref:`angleOption` to select one. If :ref:`angleOption` = 'radian', the value provided must be less than :math:`2 \pi`.

Trend & Plunge
----------------------------------

dfnWorks uses trend clockwise from North and plunge positive downward. The mean normal vector of the fracture family :math:`\vec{n}` is related to trend and plunge by

.. math::
    \vec{n}_x = -\sin(\text{trend}) \cos(\text{plunge}), \quad
    \vec{n}_y = -\cos(\text{trend}) \cos(\text{plunge}), \quad
    \vec{n}_z = \sin(\text{plunge})

trend
^^^^^^^^^^^^^^

Description: Trend of the mean fracture normal, in degrees clockwise from North. Stored as ``etrend`` / ``rtrend`` in ``DFN.params``.

plunge
^^^^^^^^^^^^^^

Description: Plunge of the mean fracture normal, in degrees, positive downward. Stored as ``eplunge`` / ``rplunge`` in ``DFN.params``.

Dip & Strike
----------------------------------

dfnWorks uses the Right Hand Rule (RHR) with strike clockwise from North. The mean normal vector of the fracture family :math:`\vec{n}` is related to dip and strike by

.. math::
    \vec{n}_x = \sin(\text{dip}) \cos(\text{strike}), \quad
    \vec{n}_y = -\sin(\text{dip}) \sin(\text{strike}), \quad
    \vec{n}_z = \cos(\text{dip})

dip
^^^^^^^^^^^^^^

Description: Dip of the mean fracture plane, in degrees. Stored as ``edip`` / ``rdip`` in ``DFN.params``.

strike
^^^^^^^^^^^^^^

Description: Strike of the mean fracture plane, in degrees clockwise from North (right hand rule). Stored as ``estrike`` / ``rstrike`` in ``DFN.params``.

.. note:: :ref:`angleOption` must be set to degree (default) to use Trend & Plunge or Dip & Strike.

----

orientation_distribution
=================================

Description: Distribution used to sample fracture normals around the mean orientation. Stored as ``eorientation_distribution`` / ``rorientation_distribution`` in ``DFN.params``.

Type: string

Default: 'fisher'

| 'fisher': von Mises-Fisher distribution, set by :ref:`kappa`.
| 'bingham': Bingham distribution, set by :ref:`kappa1` and :ref:`kappa2`.

Fisher and Bingham families can be combined in the same network.

----

Fisher Distribution
=================================

The von Mises-Fisher distribution is rotationally symmetric around the mean orientation,

.. math::
    f({\bf x}; {\boldsymbol \mu}, \kappa ) = \frac{ \kappa \exp( \kappa {\boldsymbol \mu}^{T} {\bf x} )}{ 4 \pi \sinh(\kappa)}~.

where :math:`{\boldsymbol \mu}` is the mean orientation vector and :math:`T` denotes transpose.
The distribution is sampled using the algorithm of `A. Wood, Simulation of the von Mises Fisher distribution, Communications in Statistics - Simulation and Computation 23.1 (1994): 157-164 <https://www.tandfonline.com/doi/abs/10.1080/03610919408813161>`_.

kappa
----------------------------------

Description: The concentration parameter of the von Mises-Fisher distribution, which determines the degree of clustering around the mean orientation. Stored as ``ekappa`` / ``rkappa`` in ``DFN.params``.

Type: float

.. note:: Values of :math:`\kappa` approaching zero result in a uniform distribution of points on the sphere. Larger values create points with a small deviation from mean direction.

.. warning:: The numerical method for sampling the von Mises-Fisher distribution becomes unstable for values greater than 100.

----

Bingham Distribution
=================================

The Bingham distribution allows clusters of fracture normals that are not rotationally symmetric, such as elongated clusters and girdles. In a local frame whose :math:`z`-axis is the mean orientation, normals are sampled from

.. math::
    f({\bf x}) \propto \exp\left( \kappa_1 x_1^2 + \kappa_2 x_2^2 \right),

where :math:`x_1` and :math:`x_2` are the components of the normal along the two local axes perpendicular to the mean orientation. The distribution is sampled by rejection, and normals are returned in the lower hemisphere.

kappa1
----------------------------------

Description: Concentration along the first local axis perpendicular to the mean orientation. Stored as ``ekappa1`` / ``rkappa1`` in ``DFN.params``.

Type: float

kappa2
----------------------------------

Description: Concentration along the second local axis perpendicular to the mean orientation. Stored as ``ekappa2`` / ``rkappa2`` in ``DFN.params``.

Type: float

.. note::
    | Negative values concentrate normals around the mean orientation. Larger magnitudes give tighter clusters.
    | :math:`\kappa_1 = \kappa_2 < 0`: circular cluster (similar to a Fisher distribution).
    | :math:`\kappa_1 \neq \kappa_2`, both negative: elongated (elliptical) cluster, spread more along the axis with the smaller magnitude.
    | One value near zero and the other strongly negative: girdle, with normals spread along a great circle.

See ``examples/bingham_distribution`` for round cap, elliptical cap, elliptical girdle, and asymmetric examples.
