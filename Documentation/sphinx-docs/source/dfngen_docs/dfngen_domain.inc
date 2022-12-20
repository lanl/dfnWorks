
Domain Parameters
*************************

The following parameters define the domain. All units are in SI (meters for length).

----

domainSize
=================================

Description: (Mandatory) Defines the domain size, which is centered at the origin (0,0,0). The first entry is span in x (east/west), the second entry is span in y (North/South), and the third entry is span in z (Top/Bottom). 

Type: Array of three doubles

Example:

.. code-block:: c

    domainSize: {10,5,20} 
    // Create a domain of 10 m by 5 m by 20. 
    // Minimum/Maximum x is -5/+5
    // Minimum/Maximum in y is -2.5/+2.5
    // Minimum/Maximum in z is -10/+10.

.. note:: The minimum and maximum in each direction is 1/2 the input value. 

----

domainSizeIncrease
=================================

Description: (Mandatory) Temporary :ref:`domainSize` increase for inserting fracture centers outside of the domain defined by :ref:`domainSize`.  After generation is complete, the domain is truncated back to :ref:`domainSize`. First entry is expansion in x (east/west), second entry is expansion in y (North/South), and third entry is expansion in z (Top/Bottom).  This is used to help mitigate edge density effects.

Type: Array of three doubles

Example: 

.. code-block:: c

    domainSizeIncrease:{2,1,5} 
    // Increase the domain-size by:
    // adding 1 to the +x, and subtracting 1 to the -x 
    // adding 0.5 to +y, and subtracting -0.5 to -y
    // adding 2.5 to +z, and subtracting -2.5 to -z

.. note:: The domain size increase in each direction must be less than 1/2 the domain size in that direction. 

.. tip:: A good rule of thumb is to set the expansion length to be *at least* the radius of the largest fracture. 

----


numOfLayers
=================================

Description: (Mandatory) Defines the number of stratographic layers in the domain. If numOfLayers is 0, then there are no layers.  For *N* layers, there must be *N* sets of minimum and maximum heights defined in :ref:`layers`. Each stochastic fracture set is assigned to a layer using :ref:`eLayer` for ellipses and :ref:`rLayer` for rectangles. 

Type: Non-Negative Integer (*N* > 0)

.. code-block:: c

    numOfLayers: 2 // There will be two layers in the domain


----

layers
=================================

Description. Defines the lower and upper limits for each layer. The first layer listed is layer 1, the second is layer 2, etc. Every stochastic families *must* be assigned to a layer. If the family is assigned to layer 0, then the family in generated through the entire domain.

Type: Set of :ref:`numOfLayers` arrays with two elements. {zMin, zMax}

Example: 

.. code-block:: c

    layers: 
    {-50, -30} // Minimum and Maximum height of layer 1 is -50 m and -30 m
    {10, 40} // Minimum and Maximum height of layer 2 is 10 m and 40 m

.. note:: 
    | Each layer must be on a new line
    | First entry (zMin) must be less than second entry (zMax)
    | Layers can overlap

----

numOfRegions
=================================

Description: (Mandatory) Defines the number of cuboid regions in the domain. If numOfRegions is 0, then there are no regions.  There must be *N* sets of defined by :ref:`regions`. Each stochastic fracture set is assigned to a region using :ref:`eRegion` for ellipses and :ref:`rRegion` for rectangles. 

Type: Non-Negative Integer (*N* > 0)

.. code-block:: c

    numOfRegions: 1 // There will be one region in the domain

----


regions
=================================
Description: (Mandatory) Defines the bounding box of each region. The first region listed is region 1, the region is region 2, etc. Stochastic families *must* be assigned to theses regions. If the family is assigned to region 0, then the family in generated through the entire domain.

Type: Set of :ref:`numOfRegions` arrays with six elements. {minX, maxX, minY, maxY, minZ, maxZ}. 

Example:

.. code-block:: c

    regions:
    {-5, 5, -10, 10, -20, 10}  
    // Will create a region for sampling with
    // x-min: -5, x-max: 5
    // y-min: -10, y-max: 10
    // z-min: -20, z-max: 10

.. note:: 
    | Each region must be on a new line. 
    | Min/Max values for each direction do not need to be the same.
    | Minimum value must be less than the maximum value in each direction
    | Regions can overlap

----


ignoreBoundaryFaces
=================================

Description: Selection of using the boundary faces option.

Type: boolean (0/1)

| 0: use :ref:`boundaryFaces` option
| 1: ignore :ref:`boundaryFaces` option and keep all clusters 

.. warning:: All clusters are retained only if :ref:`keepOnlyLargestCluster` is set to 0.

----


boundaryFaces
=================================

Description: (Mandatory) Selects domain boundaries for flow. The generation will only keep clusters of fractures with connections to domain boundaries which are set to 1.

Type: Array of six boolean values corresponding to each face of the domain. 

    | boundaryFaces[1] = +X domain boundary
    | boundaryFaces[2] = -X domain boundary
    | boundaryFaces[3] = +Y domain boundary
    | boundaryFaces[4] = -Y domain boundary
    | boundaryFaces[5] = +Z domain boundary
    | boundaryFaces[6] = -Z domain boundary    

Example: 

.. code-block:: c

    boundaryFaces: {1,1,0,0,0,0} // Keep fractures within a cluster that connect the X boundaries

.. warning:: Set :ref:`ignoreBoundaryFaces` to 0 when using this feature 

----


General Network Generation Parameters
**************************************************

The following parameters define the general network properties. Individual fracture family parameters are described in :ref:`Fracture Family Generation Parameters: Ellipse`, and :ref:`Fracture Family Generation Parameters: Rectangle`.


----


stopCondition
=================================

Description: (Mandatory) Selection criteria for when network generation stops. 

Type: boolean (0/1)

| 0: stop generation once :ref:`nPoly` fractures are accepted
| 1: stop generation once all fracture family p32 values have been meet

.. note:: p32 values are defined for each family in :ref:`e_p32Targets` for ellipses and :ref:`r_p32Targets` for rectangles

----


nPoly
=================================

Description: The total number of fractures requested in the domain. dfnGen will stop generation once there are *nPoly* number of fractures. 

Type: Positive Integer (*nPoly* > 0)

.. code-block:: c

    nPoly: 100 // Stop generation once 100 fractures are accepted into the network

.. note:: Only used if :ref:`stopCondition` is set to 0


----


famProb
=================================

Description: Probability of occurrence for each family of stochastically generated fractures. Values of *famProb* elements must add up to 1.0. The probabilities are listed in order of families starting with all stochastic ellipses, and then all stochastic rectangles.

Type: Array of length number of stochastic fracture families (:ref:`nFamEll` + :ref:`nFamRect`)

Example: 

.. code-block:: c
    :caption: If there are two ellipse families, each with probability 30%, and two rectangle families, each with probability 20%:

    famProb: {0.3,0.3,0.2,0.2} 

.. note:: User defined ellipses, rectangles, and polygons are inserted into the domain prior to any stochastic fractures. However, there is a possibility they will be rejected if FRAM constraints are not met.


----

  
orientationOption
=================================

Description: (Mandatory) Selection of fracture family orientation definition.  

Type: Value of 0,1,2  

| 0 : Spherical Coordinates
| 1 : Trend / Plunge 
| 2 : Dip / Strike 


.. code-block:: c

    orientationOption: 1 // Fracture Orientations will be defined using Trend/Plunge

.. note:: 
    | For spherical coordinates, values are defined using :ref:`etheta`/:ref:`ephi` for ellipses and :ref:`rtheta`/:ref:`rphi`. 
    | For Trend/Plunge,  values are defined using :ref:`etrend`/:ref:`eplunge` for ellipses and :ref:`rtrend`/:ref:`rplunge`.
    | For Dip/Strike, values are defined using :ref:`edip`/:ref:`estrike` for ellipses and :ref:`rdip`/:ref:`estrike`.

.. warning:: 
    | When using Trend / Plunge or Dip / Strike, :ref:`eAngleOption`/:ref:`rAngleOption` must be set to degrees, :ref:`eAngleOption`/:ref:`rAngleOption` = 1

----


h
=================================

Description: (Mandatory) Minimum feature size accepted into the network.

Type: Positive Double

.. note:: 
    | The following constraints are imposed on h to keep the final mesh size reasonable, unless :ref:`disableFram` is turned on.

    | 1. h must be greater than :math:`10^{-5} \cdot \sqrt{x^2 + y^2 + z^2}` where x,y,z are the elements of :ref:`domainSize`.
    | 2. h must be smaller than 1/10th the minimum fracture size
    | 3. h must be larger than 1/1000th than minimum fracture size
    | 4. h must be non-zero

.. warning:: A clear understanding of h is required for network generation and meshing. Refer to `\J. D. Hyman, C. W. Gable, S. L. Painter, and N. Makedonska. Conforming Delaunay triangulation of stochastically generated three dimensional discrete fracture networks: A feature rejection algorithm for meshing strategy. SIAM J. Sci. Comput., 36(4):A1871–A1894, 2014 <https://epubs.siam.org/doi/abs/10.1137/130942541>`_. for a complete discussion of h. 


----


disableFram
=================================

.. danger:: disableFram: If FRAM is turned off (disableFram: 1) the resulting network can only be meshed using the coarse visual mode. You cannot mesh DFN or run flow and transport if the network is generated with disableFram: 1. 


Description: (Mandatory) Turn FRAM on/off. Having FRAM on is required for full DFN capabilities of meshing, flow, and transport. If FRAM is off then capabilities will be limited. 

Type: boolean (0/1)

| 0: FRAM is on 
| 1: FRAM is off  

.. note:: disableFram: 1 and :ref:`visualizationMode` :1 are recommended if the intention is to use an upscaled octree mesh using the :ref:`UDFM <dfnWorks-python-chapter-dfnGen>` module in pydfnWorks.
 

----

printRejectReasons
=================================

Description: (Mandatory) Option to print rejection information to screen during network generation. 

Type: boolean (0/1)

| 0: off.  Limited rejection information will be printed to screen during generation.
| 1: on. Detailed fracture information will be printed to screen during generation.


.. tip:: Turning this feature on is useful for debugging and initial network construction. Having this turned off is more efficient for network generation. 

----


rejectsPerFracture
=================================

Description: (Mandatory)  If fracture is rejected, it will be re-translated to a new position *rejectsPerFracture* number of times. Increasing this value can help hit distribution targets for stochastic families.

Type: Positive Integer

.. code-block:: c

    rejectsPerFracture: 10 // If a fracture is rejected, it will be translated to a new point in the domain 10 times before being completely rejected

.. note:: Suggested default is 10. Set equal to 1 to ignore. 

----

radiiListIncrease
=================================

Description: (Mandatory) Increases the length of the radii list in the sampling queue by this percentage. Fracture radii are sampled and ordered (largest to smallest) prior to beginning network generation. If the target distributions are not being properly resolved due to rejection, then increasing this value can help provide a more uniform representation of the distribution. Once the original list is exhausted, then fracture radii are sampled from the distribution at random and only smaller fractures are likely to be accepted. 

Type: Positive Double

Example:

.. code-block:: c

    radiiListIncrease: 0.1 // Increase the length of the possible samples by 10%. 

.. note:: Set to 0 to ignore.

.. tip:: Examine the dfnGen output report to check if the prescribed distributions are being properly resolved. Run DFN.output_report() in the python work file after generation is complete to generate the output report. 


----


visualizationMode
=================================

.. warning:: No longer supported. Selection of visual mode should be done using the pydfnWorks function DFN.mesh_network(visual_mode=True)

Description: (Mandatory) Selection if you want to mesh to be coarse, for quick visualization but cannot run flow and transport, or standard mesh.

Type: boolean (0/1)


| 0: Create full DFN mesh (full_mesh.inp) for flow and transport
| 1: Create reduced DFN mesh (reduced_mesh.inp) for quick visualization


.. note:: Default should be 1. However, the selection of this value does not affect network generation. 


----


seed
=================================

Description: (Mandatory) Seed for random generator. Setting the seed equal to 0 will seed off the clock and a unique network will be produced. Setting the seed equal to a value > 0 will create the same network every time, which is useful for reproducibility. 

Type: Non-negative integer

.. tip:: If you set seed to 0, the seed used in the generation is saved in the file DFN_output.txt created by dfnGen.

----


keepOnlyLargestCluster
=================================

Description: (Mandatory) Selection to retain multiple clusters that connect boundaries or only the largest cluster. The largest cluster is defined by the number of fractures in the cluster.

Type: boolean (0/1)


| 0: Keep all clusters that connect the specified boundary faces in :ref:`boundaryFaces`
| 1: Keep only the largest cluster that connects the specified boundary faces in :ref:`boundaryFaces`


----


keepIsolatedFractures
=================================

Description: (Mandatory) Selection to keep isolated fractures in the domain after generation is complete. 

Type: boolean (0/1)

| 0: Remove isolated fractures from the domain
| 1: Keep isolated in the domain.

.. note:: Isolated fractures do not contribute to flow in the DFN as they are not connected to flow boundaries. If you are running a DFN,  keepIsolatedFractures should be set to 0. You can keep isolated fractures in the domain for UDFM meshing.

.. danger:: Full DFN-meshing will fail if isolated fractures are not removed.  Reduced meshing for visualization can still be performed. 


----


tripleIntersections
=================================

Description: (Mandatory) Selection of whether triple intersection are accepted into the network.

Type: boolean (0/1)

| 0: Reject all triple intersections
| 1: Accept triple intersections that meet FRAM criteria.

.. note:: Even if *tripleIntersections: 1*, triple intersections can be rejected if they create a feature on the network smaller than h.

.. warning:: dfnTrans does not support triple intersections.


----


removeFracturesLessThan
=================================

Description: (Mandatory)  All fractures with radius less than *removeFracturesLessThan* are removed from the network after generation is complete.

Type: Non-Negative double

Example:

.. code-block:: c

    removeFracturesLessThan: 5 // Remove all fracture with radius less than 5 meters.

.. note:: The lower cutoff of fracture size is defined using fracture family generation, e.g., :ref:`emin` for ellipses sampled from a truncated powerlaw. If this parameter is non-zero, then the network will be generated with fractures down to the lower cutoff, but only those with a radius greater than removeFracturesLessThan will be output for meshing.

----

insertUserRectanglesFirst
=================================

Description: (Mandatory) Select order for how user defined rectangles and user defined ellipses are inserted into the domain. 

Type: boolean (0/1)

| 0: Insert user defined ellipses first
| 1: Insert user defined rectangles first

.. note:: User defined fractures (ellipses, rectangles, and polygons) are *always* inserted prior to stochastic fractures.  

----


forceLargeFractures
=================================

Description: (Mandatory)  Insert the largest fracture from each family into the domain prior to sampling sequential from family based on their respective probabilities.

Type: boolean (0/1)

| 0: Do not force the largest fractures
| 1: Force the largest fractures

.. warning:: No Longer Supported. Fractures are sorted by size prior to being inserted into the domain. Larger fractures are inserted first to minimize rejections.

----



General Network Output Parameters
**************************************************

outputAllRadii
=================================

Description: (Mandatory)  Create an output file of all fracture radii, both accepted and rejected fractures. 

| Filename: radii_AllAccepted.dat
| Format: xRadius yRadius Distribution # (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)

Type: boolean (0/1)

| 0: Do not create file
| 1: Create file


----


outputAcceptedRadiiPerFamily
=================================

Description: (Mandatory)  Create one file that contains the radius of every fracture per family prior to isolated fractures removed. 

| Filename: radii/radii_AllAccepted_Fam_1.dat
| Format: xRadius yRadius DistributionNumber (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)

Type: boolean (0/1)

| 0: Do not create file
| 1: Create file

----


outputFinalRadiiPerFamily
=================================

Description: (Mandatory)  Create one file that contains the radius of every fracture per family after to isolated fractures removed. 

| Filename: radii/radii_Final_Fam_1.dat
| Format: xRadius yRadius DistributionNumber (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)

Type: boolean (0/1)

| 0: Do not create file
| 1: Create file

----


