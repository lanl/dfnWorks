
Fracture Family Generation Parameters: Ellipse
**************************************************

This section describes generation parameters for families of disc-shaped fractures. The number of elements in each parameter matches the number of ellipse families in :ref:`nFamEll`. The index of the elements corresponds to the fracture family. The first element of each parameter corresponds to the first family, the second element corresponds to the second family, etc. 

.. warning:: The parameters shown in this section are automatically written to the parameter dictionary (DFN.params) when defining fracture families. Documentation here is meant to provide additional information on the definition of each parameter in the parameter dictionary. For information on setting these parameters see :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>` 


Ellipse: General Parameters
=================================

nFamEll
----------------------------------

Description: Number of ellipse families

Type: Non-Negative Integer
 
Default: 0

Example:

.. code-block:: python

    DFN.params['nFamEll']['value'] = 3 # There will be 3 ellipse families
 
----


eLayer
----------------------------------

Description: Assign each ellipse family to a layer in domain. 

Type: list of :ref:`nFamEll`  integers 

Example:

.. code-block:: python

    DFN.params['eLayer']['value'] = [0,2,1] 
    # Family 1 is assigned to the whole domain
    # Family 2 is assigned to layer 2
    # Family 3 is assigned to layer 1
    
.. note:: Layer 0 is the entire domain. Numbers > 0 correspond to those defined in :ref:`layers`.

.. warning:: Families can only be assigned to either a layer or a region, not both.
 
----


eRegion
----------------------------------

Description: Assign each ellipse family to a region in domain. 

Type: list of :ref:`nFamEll`  integers 

Example:

.. code-block:: python

    DFN.params['eRegion']['value'] = [0,2,1] 
    # Family 1 is assigned to the whole domain
    # Family 2 is assigned to region 2
    # Family 3 is assigned to region 1
    
.. note:: Region 0 is the entire domain. Numbers > 0 correspond to those defined in :ref:`regions`.
 
.. warning:: Families can only be assigned to either a layer or a region, not both.
 

----


e_p32Targets
----------------------------------

Description: Target fracture intensity per family. Fracture intensity :math:`P_{32} [\text{m}^{-1}]` is defined as total surface area of each fracture family divided by the total domain volume. Fractures from each family are inserted into the domain until provided target values are obtained. Generation stops once all desired fracture intensity are obtained.

Type: list of :ref:`nFamEll`  floats 

Example:

.. code-block:: python


    DFN.params['e_p32Targets']['value'] = [0.02,0.4,0.05] 
    # Family 1 has a target p32 of 0.02 
    # Family 2 has a target p32 of 0.4 
    # Family 3 has a target p32 of 0.05
    
.. note:: Only used when :ref:`stopCondition` = 1

.. warning:: The fracture surface area is defined using *both* sides of a fracture. 

----


enumPoints
----------------------------------

Description:  Number of vertices defining the boundary of each elliptical fracture

Type: list of :ref:`nFamEll` integers 

Example:

.. code-block:: python

    DFN.params['enumPoints']['value'] = [8,12,16] 
    # Fractures from family 1 are defined using 8 points
    # Fractures from family 2 are defined using 12 points
    # Fractures from family 3 are defined using 16 points
    
.. note:: 
    | 1. Values must be greater than 4, which corresponds to a rectangle
    | 2. Increasing this value lead to more challenging acceptance criteria via FRAM due to smaller edge lengths between vertices on the fracture boundary
    | 3. Suggested value: 8
 
----



easpect
----------------------------------

Description: Aspect ratio of fractures

Type: list of :ref:`nFamEll` floats 

Example:

.. code-block:: python

    DFN.params['easpect']['value'] = [1,2,0.5] 
    # Family 1 has an aspect ratio of 1 (circles) 
    # Family 2 has an aspect ratio of 2 - y radius is twice the x radius
    # Family 3 has an aspect ratio of 0.5 - y radius is 1/2 the x radius
    
.. note:: A value of 1 makes circles

.. tip:: As the aspect ratio increases, the shape of the ellipse can degrade accuracy unless :ref:`enumPoints` is also increased
 
----



Ellipse: Fracture Orientation
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

ekappa
----------------------------------

Description: The concentration parameter of the von Mises-Fisher  distribution, which determines the degree of clustering around the mean orientation. 

Type: list of :ref:`nFamEll` floats 

Example:

.. code-block:: python

    DFN.params['ekappa']['value'] = [0.1, 20, 17] 
    # Fracture Family 1 has a theta value of 45 degrees
    # Fracture Family 2 has a theta value of 78 degrees
    # Fracture Family 3 has a theta value of 0 degrees
    
.. note:: Values of :math:`\kappa` approaching zero result in a uniform distribution of points on the sphere.  Larger values create points with a small deviation from mean direction. 

.. warning:: The numerical method for sampling the von Mises-Fisher  distribution becomes unstable for values greater than 100. 


----


Ellipse: Spherical Coordinates
----------------------------------


The mean normal vector of the fracture family :math:`\vec{n}` is related to the spherical coordinates :math:`\theta` and :math:`\phi` by

.. math::
        \vec{n}_x & = \sin(\theta) \cos(\phi)\\
.. math::
	\vec{n}_y & = \sin(\theta) \sin(\phi)\\
.. math::
	\vec{n}_z & = \cos(\theta)

etheta
^^^^^^^^^^^^^^

Description: Angle the normal vector of the fracture makes with the z-axis 

Type: list of :ref:`nFamEll` floats 

Example:

.. code-block:: python

    DFN.params['etheta']['value'] = [45, 78, 0] 
    # Fracture Family 1 has a theta value of 45 degrees
    # Fracture Family 2 has a theta value of 78 degrees
    # Fracture Family 3 has a theta value of 0 degrees
    
.. note:: Both radians and degrees are supported. Use :ref:`angleOption` to select one. If :ref:`angleOption` is set to radians :ref:`angleOption` = 'radian', and the value provided must be less than :math:`2 \pi`.  
 
----


ephi
^^^^^^^^^^^^^^

Description: Angle that the projection of the normal vector of a fracture onto the x-y plane makes with the x-axis. 


Type: list of :ref:`nFamEll` float 

Example:

.. code-block:: python

    DFN.params['ephi']['value'] =  [0, 56, 12] 
    # Fracture Family 1 has a phi value of 0 degrees
    # Fracture Family 2 has a phi value of 56 degrees
    # Fracture Family 3 has a phi value of 12 degrees

.. note:: Both radians and degrees are supported. Use :ref:`angleOption` to select one. If :ref:`angleOption` is set to radians :ref:`angleOption` = 'radian', then the value provided must be less than :math:`2 \pi`.  
 


----

Ellipse: Trend & Plunge
----------------------------------

The mean normal vector of the fracture family :math:`\vec{n}` is related to trend and plunge by

.. math::
        \vec{n}_x & = -\sin(\text{trend}) \cos(\text{plunge})\\
.. math::        
	\vec{n}_y & = -\cos(\text{trend}) \cos(\text{plunge})\\
.. math::
	\vec{n}_z & = \sin(\text{trend})


etrend
^^^^^^^^^^^^^^^^

Description: Trend of fracture families 

Type: list of :ref:`nFamEll` float 

Example 

.. code-block:: python

    DFN.params['etrend']['value'] = [0, 56, 12] 
    # Fracture Family 1 has a trend value of 0 degrees
    # Fracture Family 2 has a trend value of 56 degrees
    # Fracture Family 3 has a trend value of 12 degrees

.. note:: :ref:`angleOption` must be set to degree (angleOption = 'degree') to use Trend  & Plunge


----


eplunge
^^^^^^^^^^^^^^^^

Description: Plunge of fracture families

Type: list of :ref:`nFamEll` float 
 
Example 

.. code-block:: python

    DFN.params['eplunge']['value'] = [0, 56, 12] 
    # Fracture Family 1 has a plunge value of 0 degrees
    # Fracture Family 2 has a plunge value of 56 degrees
    # Fracture Family 3 has a plunge value of 12 degrees

.. note:: :ref:`angleOption` must be set to degree (angleOption = 'degree')  to use Trend  & Plunge


----

Ellipse: Dip & Strike
----------------------------------
For dip and strike, dfnWorks uses the Right Hand Rule (RHR) with strike clockwise from North. The mean normal vector of the fracture family :math:`\vec{n}` is related to dip and strike by

.. math::
        \vec{n}_x & = \sin(\text{dip}) \cos(\text{strike})\\
.. math::
	    \vec{n}_y & = -\sin(\text{dip}) \sin(\text{strike})\\
.. math::
	    \vec{n}_z & = \cos(\text{dip})

----

estrike
^^^^^^^^^^^^^^^^

Description: Strike of fracture families

Type: list of :ref:`nFamEll` float 
 
Example 

.. code-block:: python

    DFN.params['estrike']['value'] = [0, 56, 12] 
    # Fracture Family 1 has a strike value of 0 degrees
    # Fracture Family 2 has a strike value of 56 degrees
    # Fracture Family 3 has a strike value of 12 degrees

.. note:: :ref:`angleOption` must be set to degree (angleOption = 'degree')  to use Dip  & Strike


----


edip
^^^^^^^^^^^^^^^^

Description: Dip of fracture families

Type: list of :ref:`nFamEll` float 
 
Example 

.. code-block:: python

    DFN.params['edip']['value'] = [0, 56, 12] 
    # Fracture Family 1 has a dip value of 0 degrees
    # Fracture Family 2 has a dip value of 56 degrees
    # Fracture Family 3 has a dip value of 12 degrees

.. note:: :ref:`angleOption` must be set to degree (angleOption = 'degree')  to use Dip  & Strike


----

Ellipse: In Plane Rotation 
----------------------------------

ebetaDistribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Prescribe a rotation around each fracture's normal vector, with the fracture centered on x-y plane at the origin 

Type: list of :ref:`nFamEll` boolean values 

| 0: Uniform distribution on [0, :math:`2 \pi` )
| 1: Constant rotation specified by :ref:`ebeta`
 
.. code-block:: python

    DFN.params['ebetaDistribution']['value'] = [0, 1, 1] 
    # Fracture Family 1 will have a random rotation
    # Fracture Family 2 will have a constant angle of rotation defined in the first entry of ebeta
    # Fracture Family 3 will have a constant angle of rotation defined in the second entry of ebeta


----

ebeta
^^^^^^^^^^^^^^^^

Description: Values for constant angle of rotation around the normal vector 

Type: list of boolean (0/1) 
 
Example:

.. code-block:: python

    DFN.params['ebetaDistribution']['value'] = [45, 270] # For ebetaDistribution: [0, 1, 1] 
    # Fracture Family 2 will have a constant angle of rotation of 45 degrees
    # Fracture Family 3 will have a constant angle of rotation of 270 degrees


.. note:: 
    | 1. The length of ebeta corresponds to the number of *non-zero* entries in :ref:`ebetaDistribution`
    | 2. :ref:`angleOption` defines if the values are in radians or degrees



Ellipse: Fracture Radius Distributions
==================================================================
Fracture radii can be defined using four different distributions: (1) Log-Normal, (2) Truncated Power-law, (3) Exponential, and (4) Constant. Minimum and maximum values must be provided for 1-3 along with the distribution parameters.

----


edistr
----------------------------------
Description: Assigns fracture radius distribution for each family

Type: list of :ref:`nFamEll` Integers (1,2,3,4)

Example:

.. code-block:: python

    DFN.params['edistr']['value'] = [1, 2, 4] 
    # Fracture Family 1 will use a LogNormal Distribution
    # Fracture Family 2 will use a Truncated powerlaw distribution
    # Fracture Family 3 will have a constant sized fractures

.. note:: Number of elements in the parameters for each distribution must match number of families assigned to that distribution.

Ellipse: Lognormal Distribution 
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


eLogMean
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Warning:: This value is not the mean of the Log Normal distribution. Use the equations above to convert between the values if needed. 


Description: Mean value of the underlying normal distribution 

Type: list of float. Length is the number of elements in :ref:`edistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['eLogMean']['value'] = [1.609] # This value along with that in esd produce a lognormal with mean 5 m and variance of 0.1


----

esd
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. Warning:: This value is not the standard deviation of the Log Normal distribution. Use the equations above to convert between the values if needed.


Description: Standard deviation value of the underlying normal distribution 

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['esd']['value'] = [0.040] # This value along with that in eLogMean produce a lognormal with mean 5 m and variance of 0.1

----


eLogMin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Minimum radius created by the LogNormal distribution for each family

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['eLogMin']['value'] = [1,0.4] 
    # Lognormal family 1 has a minimum radius of 1 m 
    # Lognormal family 2 has a maximum radius of 0.4 m 
    
.. note:: eLogMin must be less than :ref:`eLogMax` within each family.


eLogMax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Maximum radius created by the LogNormal distribution for each family

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 1.

Example: 

.. code-block:: python

    DFN.params['eLogMax']['value'] = [10,12] 
    # Lognormal family 1 has a maximum radius of 10 m 
    # Lognormal family 2 has a maximum radius of 12 m 
    
.. note:: eLogMax must be greater than :ref:`eLogMin` within each family.

----


Ellipse: Truncated Powerlaw Distribution
--------------------------------------------------------------------
Fracture radii are sampled from a truncated power-law distribution with lower bound :math:`r_0`, upper bound :math:`r_u`, and exponent :math:`\alpha` defined by the following probability density function

.. math:: 

    \frac{\alpha}{r_0} \frac{(r/r_0)^{-1-\alpha}}{1 - (r_u/r_0)^{-\alpha}}. 

----


ealpha
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Exponent of the truncated powerlaw distribution

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 2.

Example: 

.. code-block:: python

    DFN.params['ealpha']['value'] = [1.6, 2.2] 
    # TPL family 1 has an alpha of 1.6
    # TPL family 2 has an alpha of 2.2

.. note:: A value of 0 creates constant sized fractures of size :ref:`emin`

----


emin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Lower cutoff of the truncated powerlaw distribution

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 2.

Example: 

.. code-block:: python

    DFN.params['emin']['value'] = [1.2, 5] 
    # TPL family 1 has an lower cutoff of 1.2 m
    # TPL family 2 has an lower cutoff of 5 m

.. note:: emin must be less than :ref:`emax` within each family.

----


emax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Upper cutoff of the truncated powerlaw distribution

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 2.

Example: 

.. code-block:: python

    DFN.params['emax']['value'] = [10, 50] 
    # TPL family 1 has an upper cutoff of 10 m
    # TPL family 2 has an upper cutoff of 50 m

.. note:: emax must be greater than :ref:`emin` within each family.

 
----


Ellipse: Exponential Distribution
--------------------------------------
Fracture radii are sampled from a exponential distribution with the following probability density function

.. math::

    \lambda e^{-\lambda x}

Where :math:`\lambda` is referred to as the rate parameter. 


----


eExpMean
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Mean value of each exponential distribution

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 3.

Example: 

.. code-block:: python

    DFN.params['eExpMean']['value'] = [10, 25] 
    # Exponential family 1 has a mean value of 10 m
    # Exponential family 2 has a mean value of 25 m

.. note:: eExpMean equal to :math:`1/\lambda` where :math:`\lambda` is the rate parameter of the distribution.

 
----



eExpMin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Lower cutoff of the exponential distribution families

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 3.

Example: 

.. code-block:: python

    DFN.params['eExpMin']['value'] = [1, 7] 
    # Exponential family 1 has a lower cutoff value of 1 m
    # Exponential family 2 has a lower cutoff value of 7 m

.. note:: eExpMin must be less than :ref:`eExpMax` within each family.

 
----


eExpMax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Upper cutoff of the exponential distribution families

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 3.

Example: 

.. code-block:: python

    DFN.params['eExpMax']['value'] = [527, 89] 
    # Exponential family 1 has a upper cutoff value of 527 m
    # Exponential family 2 has a upper cutoff value of 89 m

.. note:: eExpMax must be greater than :ref:`eExpMin` within each family.

 
----


Ellipse: Constant 
----------------------------------
Constant sized fracture families are defined using a single parameter :ref:`econst`. These families are also referred to as uniform or mono-disperse.


----

econst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Constant radius for each family 

Type: list of Positive floats. Length is the number of elements in :ref:`edistr` set to 4.

Example: 

.. code-block:: python

    DFN.params['econst']['value'] = [1, 7] 
    # Constant family 1 has a x-radius of 1 m 
    # Constant family 2 has a x-radius of 7 m 

----
