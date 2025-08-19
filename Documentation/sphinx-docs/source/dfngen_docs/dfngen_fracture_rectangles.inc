
Fracture Family Generation Parameters: Rectangle
**************************************************

This section describes generation parameters for families of rectangular fractures. The number of elements in each parameter matches the number of rectangle families in :ref:`nFamRect`. The index of the elements corresponds to the fracture family. The first element of each parameter corresponds to the first family, the second element corresponds to the second family, etc. 

.. warning:: The parameters shown in this section are automatically written to the parameter dictionary (DFN.params) when defining fracture families. Documentation here is meant to provide additional information on the definition of each parameter in the parameter dictionary. For information on setting these parameters see :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>` 


Rectangle: General Parameters
=================================

nFamRect
----------------------------------

Description: Number of rectangle families

Type: Non-Negative Integer
 
Default: 0

Example:

.. code-block:: python

    DFN.params['nFamRect']['value'] = 3 # There will be 3 rectangle families
 
----


rLayer
----------------------------------

Description: Assign each rectangle family to a layer in domain. 

Type: list of :ref:`nFamRect`  integers 

Example:

.. code-block:: python

    DFN.params['rLayer']['value'] = [0,2,1] 
    # Family 1 is assigned to the whole domain
    # Family 2 is assigned to layer 2
    # Family 3 is assigned to layer 1
    
.. note:: Layer 0 is the entire domain. Numbers > 0 correspond to those defined in :ref:`layers`.

.. warning:: Families can only be assigned to either a layer or a region, not both.
 
----


rRegion
----------------------------------

Description: Assign each rectangle family to a region in domain. 

Type: list of :ref:`nFamRect`  integers 

Example:

.. code-block:: python

    DFN.params['rRegion']['value'] = [0,2,1] 
    # Family 1 is assigned to the whole domain
    # Family 2 is assigned to region 2
    # Family 3 is assigned to region 1
    
.. note:: Region 0 is the entire domain. Numbers > 0 correspond to those defined in :ref:`regions`.
 
.. warning:: Families can only be assigned to either a layer or a region, not both.
 

----


r_p32Targets
----------------------------------

Description: Target fracture intensity per family. Fracture intensity :math:`P_{32} [\text{m}^{-1}]` is defined as total surface area of each fracture family divided by the total domain volume. Fractures from each family are inserted into the domain until provided target values are obtained. Generation stops once all desired fracture intensity are obtained.

Type: list of :ref:`nFamRect`  floats 

Example:

.. code-block:: python


    DFN.params['r_p32Targets']['value'] = [0.02,0.4,0.05] 
    # Family 1 has a target p32 of 0.02 
    # Family 2 has a target p32 of 0.4 
    # Family 3 has a target p32 of 0.05
    
.. note:: Only used when :ref:`stopCondition` = 1

.. warning:: The fracture surface area is defined using *both* sides of a fracture. 

----


raspect
----------------------------------

Description: Aspect ratio of fractures

Type: list of :ref:`nFamRect` floats 

Example:

.. code-block:: python

    DFN.params['raspect']['value'] = [1,2,0.5] 
    # Family 1 has an aspect ratio of 1 (circles) 
    # Family 2 has an aspect ratio of 2 - y radius is twice the x radius
    # Family 3 has an aspect ratio of 0.5 - y radius is 1/2 the x radius
    
.. note:: A value of 1 makes squares
 
----



Rectangle: Fracture Orientation
=================================

The fracture orientations are sampled from the three-dimensional von Mises-Fisher distribution,

.. math:: 
    f({\bf x}; {\boldsymbol \mu}, \kappa ) = \frac{ \kappa \exp( \kappa {\boldsymbol \mu}^{T} {\bf x} )}{ 4 \pi \sinh(\kappa)}~.

where :math:`{\boldsymbol \mu}` is the mean orientation vector and :math:`T` denotes transpose. 
The distribution is sampled using the algorithm provided `Simulation of the von Mises Fisher distribution Communications in statistics-simulation and computation 23.1 (1994): 157-164. by Andrew Wood. <https://www.tandfonline.com/doi/abs/10.1080/03610919408813161?casa_token=Cc-XXhvQTLcAAAAA%3A9pwlcB4cnrLeMs6UZWGaA7W84VevBrWD_bMvulGrKyFwFDA4ZYunOvO-XIpmf17XKgHqFQH1gzwZkw&>`_. 

dfnGen accepts spherical coordinates (:math:`\theta`/:math:`\phi`), Trend/Plunge, or Dip/Strike to define the mean orientation of a fracture family. 

.. tip:: 
    :ref:`orientationOption` indicates which of these options are used. This is automatically set based on which option is used during fracture family parameter generation.  The same option must be used for all families.

    | 0 : Spherical Coordinate (Theta/Phi)
    | 1 : Trend / Plunge
    | 2 : Dip / Strike.

----

rkappa
----------------------------------

Description: The concentration parameter of the von Mises-Fisher  distribution, which determines the degree of clustering around the mean orientation. 

Type: list of :ref:`nFamRect` floats 

Example:

.. code-block:: python

    DFN.params['rkappa']['value'] = [0.1, 20, 17] 
    # Fracture Family 1 has a theta value of 45 degrees
    # Fracture Family 2 has a theta value of 78 degrees
    # Fracture Family 3 has a theta value of 0 degrees
    
.. note:: Values of :math:`\kappa` approaching zero result in a uniform distribution of points on the sphere.  Larger values create points with a small deviation from mean direction. 

.. warning:: The numerical method for sampling the von Mises-Fisher  distribution becomes unstable for values greater than 100. 


----


Rectangle: Spherical Coordinates
----------------------------------

The mean normal vector of the fracture family :math:`\vec{n}` is related to the spherical coordinates :math:`\theta` and :math:`\phi` by

.. math::
        \vec{n}_x & = \sin(\theta) \cos(\phi)
.. math::
	\vec{n}_y & = \sin(\theta) \sin(\phi)
.. math::
	\vec{n}_z & = \cos(\theta)

rtheta
^^^^^^^^^^^^^^

Description: Angle the normal vector of the fracture makes with the z-axis 


.. note:: Both radians and degrees are supported. Use :ref:`angleOption` to select one. If :ref:`angleOption` is set to radians :ref:`angleOption` = 'radian', and the value provided must be less than :math:`2 \pi`.  
 
----


rphi
^^^^^^^^^^^^^^

Description: Angle that the projection of the normal vector of a fracture onto the x-y plane makes with the x-axis. 

.. note:: Both radians and degrees are supported. Use :ref:`angleOption` to select one. If :ref:`angleOption` is set to radians :ref:`angleOption` = 'radian', then the value provided must be less than :math:`2 \pi`.  
 

----

Rectangle: Trend & Plunge
----------------------------------
For trend and plunge, dfnWorks uses trend clockwise from North and plunge positive downward. The mean normal vector of the fracture family :math:`\vec{n}` is related to trend and plunge by

.. math::
        \vec{n}_x & = -\sin(\text{trend}) \cos(\text{plunge})
.. math::        
	\vec{n}_y & = -\cos(\text{trend}) \cos(\text{plunge})
.. math::
	\vec{n}_z & = \sin(\text{trend})


Rectangle: Dip & Strike
----------------------------------

For dip and strike, dfnWorks uses the Right Hand Rule (RHR) with strike clockwise from North. The mean normal vector of the fracture family :math:`\vec{n}` is related to dip and strike by

.. math::
        \vec{n}_x & = \sin(\text{dip}) \cos(\text{strike})
.. math::
	    \vec{n}_y & = -\sin(\text{dip}) \sin(\text{strike})
.. math::
	    \vec{n}_z & = \cos(\text{dip})


Rectangle: In Plane Rotation 
----------------------------------

rbetaDistribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Prescribe a rotation around each fracture's normal vector, with the fracture centered on x-y plane at the origin 

Type: list of :ref:`nFamRect` boolean values 

| 0: Uniform distribution on [0, :math:`2 \pi` )
| 1: Constant rotation specified by :ref:`rbeta`
 
.. code-block:: python

    DFN.params['rbetaDistribution']['value'] = [0, 1, 1] 
    # Fracture Family 1 will have a random rotation
    # Fracture Family 2 will have a constant angle of rotation defined in the first entry of ebeta
    # Fracture Family 3 will have a constant angle of rotation defined in the second entry of ebeta


----

rbeta
^^^^^^^^^^^^^^^^

Description: Values for constant angle of rotation around the normal vector 

Type: list of boolean (0/1) 
 
Example:

.. code-block:: python

    DFN.params['rbetaDistribution']['value'] = [45, 270] # For ebetaDistribution: [0, 1, 1] 
    # Fracture Family 2 will have a constant angle of rotation of 45 degrees
    # Fracture Family 3 will have a constant angle of rotation of 270 degrees


.. note:: 
    | 1. The length of rbeta corresponds to the number of *non-zero* entries in :ref:`rbetaDistribution`
    | 2. :ref: `angleOption` defines if the values are in radians or degrees



Rectangle: Fracture Radius Distributions
==================================================================
Fracture radii can be defined using four different distributions: (1) Log-Normal, (2) Truncated Power-law, (3) Exponential, and (4) Constant. Minimum and maximum values must be provided for 1-3 along with the distribution parameters.

----


rdistr
----------------------------------
Description: Assigns fracture radius distribution for each family

Type: list of :ref:`nFamRect` Integers (1,2,3,4)

Example:

.. code-block:: python

    DFN.params['rdistr']['value'] = [1, 2, 4] 
    # Fracture Family 1 will use a LogNormal Distribution
    # Fracture Family 2 will use a Truncated powerlaw distribution
    # Fracture Family 3 will have a constant sized fractures

.. note:: Number of elements in the parameters for each distribution must match number of families assigned to that distribution.

Rectangle: Lognormal Distribution 
----------------------------------

Fracture radii are sampled from a Lognormal distribution with the following probability density function

.. math::
    \frac{1}{x \sigma \sqrt{2\pi}} \exp \left (- \frac{(\ln x -\mu)^2}{2 \sigma^2} \right)

with mean :math:`\mu` and variance :math:`\sigma^2`.

.. warning:: dfnGen uses the mean and standard deviation of the underlying normal distribution that creates the lognormal distribution not the mean and variance of the lognormal distribution.


In order to produce a LogNormal distribution with a desired mean (:math:`\mu`) and variance (:math:`\sigma^2`) one uses

.. math::
    eLogMean = \ln  \left ( \frac{\mu^2}{\sqrt{\mu^2 + \sigma^2}} \right)

and 

.. math::
    esd =  \sqrt{\ln \left ( 1 + \frac{ \sigma^2}{\mu^2} \right )}

For more details see `https://en.wikipedia.org/wiki/Log-normal_distribution <https://en.wikipedia.org/wiki/Log-normal_distribution>`_.
 
----


rLogMean
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Warning:: This value is not the mean of the Log Normal distribution. Use the equations above to convert between the values if needed. 


Description: Mean value of the underlying normal distribution 

Type: list of float. Length is the number of elements in :ref:`rdistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['rLogMean']['value'] = [1.609] # This value along with that in esd produce a lognormal with mean 5 m and variance of 0.1


----

rsd
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. Warning:: This value is not the standard deviation of the Log Normal distribution. Use the equations above to convert between the values if needed.


Description: Standard deviation value of the underlying normal distribution 

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['rsd']['value'] = [0.040] # This value along with that in rLogMean produce a lognormal with mean 5 m and variance of 0.1

----


rLogMin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Minimum radius created by the LogNormal distribution for each family

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['rLogMin']['value'] = [1,0.4] 
    # Lognormal family 1 has a minimum radius of 1 m 
    # Lognormal family 2 has a maximum radius of 0.4 m 
    
.. note:: rLogMin must be less than :ref:`rLogMax` within each family.


rLogMax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Maximum radius created by the LogNormal distribution for each family

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['rLogMax']['value'] = [10,12] 
    # Lognormal family 1 has a maximum radius of 10 m 
    # Lognormal family 2 has a maximum radius of 12 m 
    
.. note:: rLogMax must be greater than :ref:`rLogMin` within each family.

----


Rectangle: Truncated Powerlaw Distribution
--------------------------------------------------------------------
Fracture radii are sampled from a truncated power-law distribution with lower bound :math:`r_0`, upper bound :math:`r_u`, and exponent :math:`\alpha` defined by the following probability density function

.. math:: 

    \frac{\alpha}{r_0} \frac{(r/r_0)^{-1-\alpha}}{1 - (r_u/r_0)^{-\alpha}}. 

----


ralpha
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Exponent of the truncated powerlaw distribution

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 2.

Example: 

.. code-block:: python

    DFN.params['ralpha']['value'] = [1.6, 2.2] 
    # TPL family 1 has an alpha of 1.6
    # TPL family 2 has an alpha of 2.2

.. note:: A value of 0 creates constant sized fractures of size :ref:`rmin`

----


rmin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Lower cutoff of the truncated powerlaw distribution

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 2.

Example: 

.. code-block:: python

    DFN.params['rmin']['value'] = [1.2, 5] 
    # TPL family 1 has an lower cutoff of 1.2 m
    # TPL family 2 has an lower cutoff of 5 m

.. note:: rmin must be less than :ref:`rmax` within each family.

----


rmax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Upper cutoff of the truncated powerlaw distribution

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 2.

Example: 

.. code-block:: python

    DFN.params['rmax']['value'] = [10, 50] 
    # TPL family 1 has an upper cutoff of 10 m
    # TPL family 2 has an upper cutoff of 50 m

.. note:: rmax must be greater than :ref:`rmin` within each family.

 
----


Rectangle: Exponential Distribution
--------------------------------------
Fracture radii are sampled from a exponential distribution with the following probability density function

.. math::

    \lambda e^{-\lambda x}

Where :math:`\lambda` is referred to as the rate parameter. 


----


rExpMean
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Mean value of each exponential distribution

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 3.

Example: 

.. code-block:: python

    DFN.params['rExpMean']['value'] = [10, 25] 
    # Exponential family 1 has a mean value of 10 m
    # Exponential family 2 has a mean value of 25 m

.. note:: rExpMean equal to :math:`1/\lambda` where :math:`\lambda` is the rate parameter of the distribution.

 
----



rExpMin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Lower cutoff of the exponential distribution families

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 3.

Example: 

.. code-block:: python

    DFN.params['rExpMin']['value'] = [1, 7] 
    # Exponential family 1 has a lower cutoff value of 1 m
    # Exponential family 2 has a lower cutoff value of 7 m

.. note:: rExpMin must be less than :ref:`rExpMax` within each family.

 
----


rExpMax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Upper cutoff of the exponential distribution families

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 3.

Example: 

.. code-block:: python

    DFN.params['rExpMax']['value'] = [527, 89] 
    # Exponential family 1 has a upper cutoff value of 527 m
    # Exponential family 2 has a upper cutoff value of 89 m

.. note:: rExpMax must be greater than :ref:`rExpMin` within each family.

 
----


Rectangle: Constant 
----------------------------------
Constant sized fracture families are defined using a single parameter :ref:`rconst`. These families are also referred to as uniform or mono-disperse.


----

rconst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Constant radius for each family 

Type: list of Positive floats. Length is the number of elements in :ref:`rdistr` set to 4.

Example: 

.. code-block:: python

    DFN.params['rconst']['value'] = [1, 7] 
    # Constant family 1 has a x-radius of 1 m 
    # Constant family 2 has a x-radius of 7 m 

----
