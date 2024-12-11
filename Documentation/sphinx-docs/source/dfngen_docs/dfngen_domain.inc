
Domain Parameters
*************************

The following parameters define the domain. All units are in SI (meters for length). 

.. note:: Parameters with (Mandatory) label must be present in python driver script for simulations to run. 

----

domainSize
=================================

Description: (Mandatory) Defines the domain size, which is centered at the origin (0,0,0). The first entry is span in x (east/west), the second entry is span in y (North/South), and the third entry is span in z (Top/Bottom). 

Type: List of three floats

Default : None

Example:

.. code-block:: python

    DFN.parameters['domainSize']['value'] = [10.0,5.0,20.0] 
    # Create a domain of 10 m by 5 m by 20. 
    # Minimum/Maximum x is -5/+5
    # Minimum/Maximum in y is -2.5/+2.5
    # Minimum/Maximum in z is -10/+10.

.. note:: The minimum and maximum in each direction is 1/2 the input value. 

----

domainSizeIncrease
=================================

Description: Temporary :ref:`domainSize` increase for inserting fracture centers outside of the domain defined by :ref:`domainSize`.  After generation is complete, the domain is truncated back to :ref:`domainSize`. First entry is expansion in x (east/west), second entry is expansion in y (North/South), and third entry is expansion in z (Top/Bottom).  This is used to help mitigate edge density effects.

Type: List of three floats

Default: [0,0,0]

Example: 

.. code-block:: python

    DFN.params['domainSizeIncrease']['value'] = [2,1,5] 
    # Increase the domain-size by:
    # adding 1 to the +x, and subtracting 1 to the -x 
    # adding 0.5 to +y, and subtracting -0.5 to -y
    # adding 2.5 to +z, and subtracting -2.5 to -z

.. note:: The domain size increase in each direction must be less than 1/2 the domain size in that direction. 

.. tip:: A good rule of thumb is to set the expansion length to be *at least* the radius of the largest fracture. 

----


numOfLayers
=================================

Description: Defines the number of stratographic layers in the domain. If numOfLayers is 0, then there are no layers.  For *N* layers, there must be *N* sets of minimum and maximum heights defined in :ref:`layers`. Each stochastic fracture set is assigned to a layer when creating a fracture family (See :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>`). 

Type: Non-Negative Integer (*N* > 0)

Default: 0

Example:

.. code-block:: python

    DFN.params['numOfLayers']['value'] = 2 # There will be two layers in the domain


----

layers
=================================

Description. Defines the lower and upper limits for each layer. The first layer listed is layer 1, the second is layer 2, etc. Every stochastic families *must* be assigned to a layer. If the family is assigned to layer 0, then the family in generated through the entire domain.

Type: List of :ref:`numOfLayers` lists with two elements. [zMin, zMax]

Default: None

Example: 

.. code-block:: python

    DFN.params['layers']['value'] =  [[-50, -30],  # Minimum and Maximum height of layer 1 is -50 m and -30 m
    					[10, 40]] # Minimum and Maximum height of layer 2 is 10 m and 40 m

.. note:: 
    | First entry (zMin) must be less than second entry (zMax)
    | Layers can overlap

----

numOfRegions
=================================

Description: Defines the number of cuboid regions in the domain. If numOfRegions is 0, then there are no regions.  There must be *N* sets of defined by :ref:`regions`. Each stochastic fracture set is assigned to a region during fracture family creation (See :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>`).

Type: Non-Negative Integer (*N* > 0)

Default: 0

Example:

.. code-block:: python

    DFN.params['numOfRegions']['value'] = 1 # There will be one region in the domain

----


regions
=================================
Description: Defines the bounding box of each region. The first region listed is region 1, the region is region 2, etc. Stochastic families *must* be assigned to theses regions. If the family is assigned to region 0, then the family in generated through the entire domain.

Type: List of :ref:`numOfRegions` lists with six elements. [minX, maxX, minY, maxY, minZ, maxZ]. 

Default: None

Example:

.. code-block:: python

    DFN.params['regions']['value'] = [[-5, 5, -10, 10, -20, 10],
	  				[0, 10, -5, 15, 10, 20]]  
					# Will create two regions for sampling 
					# The first region with
					# x-min: -5, x-max: 5
					# y-min: -10, y-max: 10
					# z-min: -20, z-max: 10

.. note::  
    | Min/Max values for each direction do not need to be the same.
    | Minimum value must be less than the maximum value in each direction
    | Regions can overlap

----


ignoreBoundaryFaces
=================================

Description: Selection of using the boundary faces option.

Type: boolean

| False: use :ref:`boundaryFaces` option
| True: ignore :ref:`boundaryFaces` option and keep all clusters 

Example:

.. code-block:: python

    DFN.params['ignoreBoundaryFaces']['value'] = True

.. warning:: All clusters are retained only if :ref:`keepOnlyLargestCluster` is set to 0.

----


boundaryFaces
=================================

Description: Selects domain boundaries for flow. The generation will only keep clusters of fractures with connections to domain boundaries which are set to 1.

Type: list of six boolean values corresponding to each face of the domain. 

    | boundaryFaces[0] = +X domain boundary
    | boundaryFaces[1] = -X domain boundary
    | boundaryFaces[2] = +Y domain boundary
    | boundaryFaces[3] = -Y domain boundary
    | boundaryFaces[4] = +Z domain boundary
    | boundaryFaces[5] = -Z domain boundary    

Default: [1,1,0,0,0,0]

Example: 

.. code-block:: python

    DFN.params['boundaryFaces']['value'] = [1,1,0,0,0,0] # Keep fractures within a cluster that connect the X boundaries

.. warning:: :ref:`ignoreBoundaryFaces` must be False (default) when using this feature 

----


General Network Generation Parameters
**************************************************

The following parameters define the general network properties. 

.. note:: parameters with (Mandatory) label must be present in python driver script for simulations to run.


----


stopCondition
=================================

Description: Selection criteria for when network generation stops. 

Type: boolean (0/1)

Default: 1

| 0: stop generation once :ref:`nPoly` fractures are accepted
| 1: stop generation once all fracture family p32 values have been meet

Example:

.. code-block:: python

    DFN.params['stopCondition']['value'] = 1 

.. note:: p32 values are defined for each family during the creation of the fracture family. If stopCondition = 0 the :ref:`famProb` of a fracture belonging to a family is set during the creation of the fracture family (See :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>`). 

----


nPoly
=================================

Description: The total number of fractures requested in the domain. dfnGen will stop generation once there are *nPoly* number of fractures. 

Type: Positive Integer (*nPoly* > 0)

Default: None

Example:

.. code-block:: python

    DFN.params['nPoly']['value'] = 100 # Stop generation once 100 fractures are accepted into the network

.. note:: Only used if :ref:`stopCondition` is set to 0


----


famProb
=================================

Description: Probability of occurrence for each family of stochastically generated fractures. Values of *famProb* elements must add up to 1.0. The probabilities are saved in order of families starting with all stochastic ellipses, and then all stochastic rectangles.

Type: List of length number of stochastic fracture families (:ref:`nFamEll` + :ref:`nFamRect`)

This list is automatically generated. The values are defined with the creation of each fracture family (See :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>`).

.. note:: User defined ellipses, rectangles, and polygons are inserted into the domain prior to any stochastic fractures. However, there is a possibility they will be rejected if FRAM constraints are not met.


----

  
orientationOption
=================================

Description: Selection of fracture family orientation definition.  

Type: Value of 0,1,2  

| 0 : Spherical Coordinates
| 1 : Trend / Plunge 
| 2 : Dip / Strike 

This value is set automatically with the definition of fracture families (See :ref:`pydfnGen <dfnWorks-python-chapter-dfnGen>`).

.. note:: 
    | For spherical coordinates, values are defined using the function parameters :ref:`theta <dfnWorks-python-chapter-dfnGen>`/:ref:`phi <dfnWorks-python-chapter-dfnGen>`. 
    | For Trend/Plunge,  values are defined using :ref:`trend <dfnWorks-python-chapter-dfnGen>`/:ref:`plunge <dfnWorks-python-chapter-dfnGen>`.
    | For Dip/Strike, values are defined using :ref:`dip <dfnWorks-python-chapter-dfnGen>`/:ref:`strike <dfnWorks-python-chapter-dfnGen>`.

.. warning:: 
    | When using Trend / Plunge or Dip / Strike, :ref:`angleOption` must be set to degree (default), :ref:`angleOption` = 'degree'

----

angleOption
=================================

Description: Selection of fracture family angle units. All stochastically generated fracture families will use the specified units 

Type: String of either 'degree' or 'radian'

Default: 'degree'

Example:

.. code-block:: python

    DFN.params['angleOption']['value'] = 'radian'

.. warning::
    | When using Trend / Plunge or Dip / Strike, :ref:`angleOption` must be set to degree (default), :ref:`angleOption` = 'degree'

----

h
=================================

Description: (Mandatory) Minimum feature size accepted into the network.

Type: Positive float

.. note:: 
    | The following constraints are imposed on h to keep the final mesh size reasonable, unless :ref:`disableFram` is turned on.

    | 1. h must be greater than :math:`10^{-5} \cdot \sqrt{x^2 + y^2 + z^2}` where x,y,z are the elements of :ref:`domainSize`.
    | 2. h must be smaller than 1/10th the minimum fracture size
    | 3. h must be larger than 1/1000th than minimum fracture size
    | 4. h must be non-zero

Default: None

Example:

.. code-block:: python

    DFN.params['h']['value'] = .1

.. warning:: A clear understanding of h is required for network generation and meshing. Refer to `\J. D. Hyman, C. W. Gable, S. L. Painter, and N. Makedonska. Conforming Delaunay triangulation of stochastically generated three dimensional discrete fracture networks: A feature rejection algorithm for meshing strategy. SIAM J. Sci. Comput., 36(4):A1871–A1894, 2014 <https://epubs.siam.org/doi/abs/10.1137/130942541>`_. for a complete discussion of h. 


----


disableFram
=================================

.. danger:: disableFram: If FRAM is turned off (disableFram: True) the resulting network can only be meshed using the coarse visual mode. You cannot mesh DFN or run flow and transport if the network is generated with disableFram: True. 


Description: (Mandatory) Turn FRAM on/off. Having FRAM on is required for full DFN capabilities of meshing, flow, and transport. If FRAM is off then capabilities will be limited. 

Type: boolean

| False: FRAM is on 
| True: FRAM is off  

Default: False

Example:

.. code-block:: python

    DFN.params['disableFram']['value'] = False

.. note:: disableFram: True and :ref:`visualizationMode` :1 are recommended if the intention is to use an upscaled octree mesh using the :ref:`UDFM <dfnWorks-python-chapter-dfnGen>` module in pydfnWorks.
 

----

printRejectReasons
=================================

Description: Option to print rejection information to screen during network generation. 

Type: boolean

| False: off.  Limited rejection information will be printed to screen during generation.
| True: on. Detailed fracture information will be printed to screen during generation.

Default: False

Example:

.. code-block:: python

    DFN.params['printRejectReasons']['value'] = True

.. tip:: Turning this feature on is useful for debugging and initial network construction. Having this turned off is more efficient for network generation. 

----


rejectsPerFracture
=================================

Description: If fracture is rejected, it will be re-translated to a new position *rejectsPerFracture* number of times. Increasing this value can help hit distribution targets for stochastic families.

Type: Positive Integer

Default: 10

Example:

.. code-block:: python

    DFN.params['rejectsPerFracture']['value'] = 10 # If a fracture is rejected, it will be translated to a new point in the domain 10 times before being completely rejected

.. note:: Default is 10. Set equal to 1 to ignore. 

----

radiiListIncrease
=================================

Description: Increases the length of the radii list in the sampling queue by this percentage. Fracture radii are sampled and ordered (largest to smallest) prior to beginning network generation. If the target distributions are not being properly resolved due to rejection, then increasing this value can help provide a more uniform representation of the distribution. Once the original list is exhausted, then fracture radii are sampled from the distribution at random and only smaller fractures are likely to be accepted. 

Type: Positive Double

Default: 0.1

Example:

.. code-block:: python

    DFN.params['radiiListIncrease']['value'] = 0.10 # Increase the length of the possible samples by 10%. 

.. note:: Set to 0 to ignore.

.. tip:: Examine the dfnGen output report to check if the prescribed distributions are being properly resolved. Run DFN.output_report() in the python work file after generation is complete to generate the output report. 


----


visualizationMode
=================================

.. warning:: No longer supported. Selection of visual mode should be done using the pydfnWorks function DFN.mesh_network(visual_mode=True)

Description: Selection if you want to mesh to be coarse, for quick visualization but cannot run flow and transport, or standard mesh.

Type: boolean


| False: Create full DFN mesh (full_mesh.inp) for flow and transport
| True: Create reduced DFN mesh (reduced_mesh.inp) for quick visualization

Default: False

Example:

.. code-block:: python

    DFN.params['visualizationMode']['value'] = False


----


seed
=================================

Description: Seed for random generator. Setting the seed equal to 0 will seed off the clock and a unique network will be produced. Setting the seed equal to a value > 0 will create the same network every time, which is useful for reproducibility. 

Type: Non-negative integer

Default: 1

Example:

.. code-block:: python

    DFN.params['seed']['value'] = 42069

.. tip:: If you set seed to 0, the seed used in the generation is saved in the file DFN_output.txt created by dfnGen.

----


keepOnlyLargestCluster
=================================

Description: Selection to retain multiple clusters that connect boundaries or only the largest cluster. The largest cluster is defined by the number of fractures in the cluster.

Type: boolean


| False: Keep all clusters that connect the specified boundary faces in :ref:`boundaryFaces`
| True: Keep only the largest cluster that connects the specified boundary faces in :ref:`boundaryFaces`

Default: True

Example:

.. code-block:: python

    DFN.params['keepOnlyLargestCluster']['value'] = False


----


keepIsolatedFractures
=================================

Description: Selection to keep isolated fractures in the domain after generation is complete. 

Type: boolean

| False: Remove isolated fractures from the domain
| True: Keep isolated in the domain.

Default: False

Example:

.. code-block:: python

    DFN.params['keepIsolatedFractures']['value'] = False

.. note:: Isolated fractures do not contribute to flow in the DFN as they are not connected to flow boundaries. If you are running a DFN,  keepIsolatedFractures should be set to False. You can keep isolated fractures in the domain for UDFM meshing.

.. danger:: Full DFN-meshing will fail if isolated fractures are not removed.  Reduced meshing for visualization can still be performed. 


----


tripleIntersections
=================================

Description: Selection of whether triple intersection are accepted into the network.

Type: boolean

| False: Reject all triple intersections
| True: Accept triple intersections that meet FRAM criteria.

Default: False

Example:

.. code-block:: python

    DFN.params['tripleIntersections']['value'] = True

.. note:: Even if *tripleIntersections = True*, triple intersections can be rejected if they create a feature on the network smaller than h.

.. warning:: dfnTrans does not support triple intersections.


----


removeFracturesLessThan
=================================

Description: All fractures with radius less than *removeFracturesLessThan* are removed from the network after generation is complete.

Type: Non-Negative double

Default: 0

Example:

.. code-block:: python

    DFN.params['removeFracturesLessThan']['value'] = 5 # Remove all fracture with radius less than 5 meters.

.. note:: The lower cutoff of fracture size is defined using fracture family generation, e.g., :ref:`emin` for ellipses sampled from a truncated powerlaw. If this parameter is non-zero, then the network will be generated with fractures down to the lower cutoff, but only those with a radius greater than removeFracturesLessThan will be output for meshing.

----

insertUserRectanglesFirst
=================================

Description: Select order for how user defined rectangles and user defined ellipses are inserted into the domain. 

Type: boolean

| False: Insert user defined ellipses first
| True: Insert user defined rectangles first

Default: True

Example:

.. code-block:: python

    DFN.params['insertUserRectanglesFirst']['value'] = False

.. note:: User defined fractures (ellipses, rectangles, and polygons) are *always* inserted prior to stochastic fractures.  

----


forceLargeFractures
=================================

Description: Insert the largest fracture from each family into the domain prior to sampling sequential from family based on their respective probabilities.

Type: boolean

| False: Do not force the largest fractures
| True: Force the largest fractures

Default: False

.. code-block:: python

    DFN.params['forceLargeFractures']['value'] = True

.. warning:: No Longer Supported. Fractures are sorted by size prior to being inserted into the domain. Larger fractures are inserted first to minimize rejections.

----



General Network Output Parameters
**************************************************

outputAllRadii
=================================

Description: Create an output file of all fracture radii, both accepted and rejected fractures. 

| Filename: radii_AllAccepted.dat
| Format: xRadius yRadius Distribution # (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)

Type: boolean

| False: Do not create file
| True: Create file

Default: False

Example

.. code-block:: python

    DFN.params['outputAllRadii']['value'] = False

----


outputAcceptedRadiiPerFamily
=================================

Description: Create one file that contains the radius of every fracture per family prior to isolated fractures removed. 

| Filename: radii/radii_AllAccepted_Fam_1.dat
| Format: xRadius yRadius DistributionNumber (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)

Type: boolean

| False: Do not create file
| True: Create file

Default: False

Example:

.. code-block:: python

    DFN.params['outputAcceptedRadiiPerFamily']['value'] = False

----


outputFinalRadiiPerFamily
=================================

Description: Create one file that contains the radius of every fracture per family after to isolated fractures removed. 

| Filename: radii/radii_Final_Fam_1.dat
| Format: xRadius yRadius DistributionNumber (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)

Type: boolean

| False: Do not create file
| True: Create file

Default: False

Example:

.. code-block:: python

    DFN.params['outputFinalRadiiPerFamily']['value'] = False


----


