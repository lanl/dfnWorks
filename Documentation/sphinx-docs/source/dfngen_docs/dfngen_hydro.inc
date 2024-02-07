
Hydrological Properties
**************************************************
Hydraulic properties can be assigned when generating creating stochastic and user defined fractures. For information about adding into the network see 

.. warning:: These parameters are not going to be supported in future versions. Use the pydfnWorks function dump_hydraulic_values to specific hydraulic properties of fractures (hydraulic aperture, permeability, and transmissivity) after generation is complete. Using that function, values can be assigned by fracture family, which can correlated with depth using layers or regions. 


Hydraulic Aperture  
==================================
Description: Specification of hydraulic aperture option. 

| 1) Log Normal distribution with parameters :ref:`meanAperture` and :ref:`stdAperture`.

| 2) Aperture from Transmissivity defined using :ref:`apertureFromTransmissivity`

| 3) Constant Aperture defined using :ref:`constantAperture`

| 4) Aperture perfectly correlated to fracture length using :ref:`lengthCorrelatedAperture`

Type: Integer 1,2,3,4

.. note:: Detailed description of each option is provided below.

----


Option 1) Log Normal Distribution 
------------------------------------------------
Aperture values are uncorrelated with fracture size and sampled from a log normal distribution with assigned mean and standard deviation. This model is often referred to as the *uncorrelated* model.

dfnGen uses the mean and standard deviation of the underlying normal distribution that creates the lognormal distribution. 

These parameters define the aperture sampled from a Lognormal distribution with the following probability density function

.. math::
    \frac{1}{x \sigma \sqrt{2\pi}} \exp \left (- \frac{(\ln x -\mu)^2}{2 \sigma^2} \right)


In order to produce a LogNormal distribution with a desired mean (:math:`\mu`) and variance (:math:`\sigma^2`) one uses

.. math::
    meanAperture = \ln  \left ( \frac{\mu^2}{\sqrt{\mu^2 + \sigma^2}} \right)

and 

.. math::
    stdAperture = \sqrt{\ln \left ( 1 + \frac{ \sigma^2}{\mu^2} \right )}

For more details see `https://en.wikipedia.org/wiki/Log-normal_distribution <https://en.wikipedia.org/wiki/Log-normal_distribution>`_.
 

----


meanAperture
^^^^^^^^^^^^^^^^^^^^
Description: Mean value of the underlying normal distribution 

Type: Double

.. Warning:: This value is not the mean of the Log Normal distribution. Use the equations above to convert between the values if needed. 

----

stdAperture  
^^^^^^^^^^^^^^^^^^^^
Description: Standard deviation of the underlying normal distribution 

Type: Double

.. Warning:: This value is not the mean of the Log Normal distribution. Use the equations above to convert between the values if needed. 


----

Option 2: Aperture from Transmissivity 
--------------------------------------------------------------
Description: Determines the hydraulic aperture based on an assigned fracture transmissivity. First, the transmissivity is defined using 

.. math:: 
    T  = F\cdot r^k

where *F* and *k* are user defined parameters assigned here and *r* is the mean fracture radius. Once *T* is defined, then the aperture is determined using the cubic law

.. math:: 
    b = \sqrt[3]{12 T}

----

apertureFromTransmissivity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Parameters *F* and *k* to define transmissivity from fracture radius. 

Type: Tuple of double values.

Example:

.. code-block:: c

    apertureFromTransmissivity: {1.6e-9, 0.8} // F = 1.6-9 and k = 0.8

----


Option 3: Constant Aperture
--------------------------------------------------------------
All fractures are assigned the same aperture value regardless of family, location, or size. 

constantAperture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Value of fracture aperture in meters

Type: Double

.. code-block:: c

    constantAperture: 1e-5 

----

Option 3: Aperture perfectly correlated to fracture radius
--------------------------------------------------------------
Fracture aperture is assigned as a function of fracture size using the following equation

.. math:: 
    b  = F\cdot r^k
 
where *F* and *k* are user defined parameters assigned here and *r* is the mean fracture radius.


----


lengthCorrelatedAperture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Parameters *F* and *k* to define the relationship between fracture size and aperture.

Type: Tuple of double values.

Example:

.. code-block:: c

    lengthCorrelatedAperture: {5e-5, 0.5} // F = 5e-5 and k =  0.5


----


Permeability
==================
Permeability can be defined in two ways. Either derived from the fracture aperture using the cubic law or assigned a constant value. 


----


permOption
------------------------

Description: Selection of permeability option

Type: Integer value of 0 or 1

| 0) Permeability of each fracture is a function of fracture aperture, given by 

.. math::

        k=b^2/12

where *b* is an aperture and *k* is permeability. 

| 1) Constant Permeability for all fractures defined using :ref:`constantPermeability`

----


constantPermeability
------------------------
.. danger:: Using this option will result in inconsistent permeability values of aperture with mesh volume rescaling for FEHM and PFLOTRAN.


Description: Value of constant permeability for all fractures. Value is in :math:`m^2`

Type: Double

Example:

.. code-block:: c

    constantPermeability: 1e-12 // all fractures will have a permeability of 1e-12 m^2
