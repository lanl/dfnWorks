.. _dfngen-chapter:

dfnGen
^^^^^^

Keywords
-------- 

The following is an example input file with all keywords and
explanation of each keyword.

.. code-block:: c

    //==========================================================================
    //Gereral Options & Fracture Network Parameters: 
    /*
    stopCondition: 0 /* 0: stop once nPoly fractures are accepted (Defined
    below) 1: stop once all family's p32 values are equal or greater than the
    families target p32 values (defined in stochastic family sections) */             

    nPoly: 3 /* Used when stopCondition = 0 Total number of fractures you would
    like to have in the domain you defined. The program will complete once you
    have nPoly number of fractures, maxPoly number of polygon/fracture
    rejections, rejPoly number of rejections in a row, or reach a specified
    fracture cluster size if using stoppingParameter = -largestSize  */


    outputAllRadii: 0  /* 0: Do not output all radii file.  1: Include file of
    all raddii (acepted+rejected fractures) in output files.  */
	                      

    domainSize: {1,1,1} /* Mandatory Parameter.  Creates a domain with dimension
    x*y*z centered at the origin.*/

    numOfLayers: 0    //number of layers


    layers: {-500,0} {0,500}

    /*  Layers need to be listed line by line Format: {minZ, maxZ}
	    
        The first layer listed is layer 1, the second is layer 2, etc Stochastic
        families can be assigned to theses layers (see stochastic shape familiy
        section) */   


    h: 0.050 /* Minimum fracture length scale(meters) Any fracture with a
    feature, such as and intersection, of less than h will be rejected. */

	   
    //==========================================================================//
    /* Fracture Network Parameters:
    */

    tripleIntersections: 1 /* Options:     0: Off 1: On    */

    printRejectReasons: 0 /* Useful in debugging, This option will print all
    fracture rejection reasons as they occur.  0: disable 1: print all rejection
    reasons to screen */

    visualizationMode: 0 /* Options: 0 or 1 Used during meshing: 0: creates a
    fine mesh, according to h parameter; 1: produce only first round of
    triangulations. In this case no modeling of flow and transport is possible.
    */ 

    seed: 92731535 //Seed for random generator. 
	        

    domainSizeIncrease: {0,0,0} //temporary size increase for inserting fracture
    centers outside domain //increases the entire width by this ammount. So,
    {1,1,1} will increase //the domain by adding .5 to the +x, and subbtracting
    .5 to the -x, etc


    keepOnlyLargestCluster: 0 /* 0 = Keep any clusters which connects the
    specified boundary faces in boundaryFaces option below
	       
           1 = Keep only the largest cluster which connects the specified
           boundary faces in boundaryFaces option below */

    ignoreBoundaryFaces: 1  /* 0 = use boundaryFaces option below 

         1 = ignore boundaryFaces option and keep all clusters and will still
         remove fractures with no intersections               */
	     
	          
    boundaryFaces: {1,1,0,0,0,0} /*  DFN will only keep clusters with
    connections to domain boundaries which are set to 1:

        boundaryFaces[0] = +X domain boundary boundaryFaces[1] = -X domain
        boundary boundaryFaces[2] = +Y domain boundary boundaryFaces[3] = -Y
        domain boundary boundaryFaces[4] = +Z domain boundary boundaryFaces[5] =
        -Z domain boundary    
	    
        Be sure to set ignoreBoundaryFaces to 0 when using this feature.     */
	                          

    rejectsPerFracture: 10  /*If fracture is rejected, it will be re-translated
    to a new position this number of times. 
	                         
                             This helps hit distribution targets for stochastic
                             families (Set to 1 to ignore this feature)    */





    //===========================================================================
    //                  Shape and Probability Parameters
    //===========================================================================

    //user rectangles and user Ellipses defined in their cooresponding files

    famProb: {.5,.5} /* Probability of occurrence of each family of randomly
    distrubuted rectangles and ellipses.  User-ellipses and user-rectangles
    insertion will be attempted with 100% likelihood, but with possability they
    may be rejected.  The famProb elements should add up to 1.0 (for %100).  The
    probabilities are listed in order of families starting with all stochastic
    ellipses, and then all stochastic rectangles.
	   
       For example: If  then there are two ellipse families, each with
       probabiliy .3, and two rectangle families, each with probabiliy .2,
       famProb will be: famProb: {.3,.3,.2,.2} Notice: famProb elements add to 1
       */
	 
	 
	 
	 
    /*===========================================================================*/
    //===========================================================================
    //                      Elliptical Fracture Options
    //      NOTE: Number of elements must match number of ellipse families  //
    (first number in nShape input parameter)
    //===========================================================================
    /*===========================================================================*/

    //Number of ellipse families nFamEll: 0 //Having this option = 0 will ignore
    all rectangle family variables

    eLayer: {0,0} /* Defines which domain the family belings to.  Layer 0 is the
    entire domain.  Layers numbered > 0 coorespond to layers defined above 1
    corresponts to the first layer listed, 2 is the next layer listed, etc */

    //edist is a mandatory parameter if using statistically generated ellipses
    edistr: {2,3}   /* Ellipse statistical distribution options: 1 - lognormal
    distribution 2 - truncated power law distribution   3 - exponential
    distribution 4 - constant */
	                                                                                       
	                      
    ebetaDistribution: {1,1}   /* Beta is the rotation around the polygon's
    normal vector, with the polygon centered on x-y plane at the orgin 
	                    
                        0 - uniform distribution [0, 2PI]    1 - constant angle
                        (specefied below by "ebeta")    */                
	    
	    
    e_p32Targets: {.1,.1} /* Elliptical families target fracture intensity per
    family.  When using stopCondition = 1 (defined at the top of the input
    file), families will be inserted untill the families desired fracture
    intensity has been reached.  Once all families desired fracture intensity
    has been met, fracture generation will be complete.  */                      
	                      
    //===========================================================================
    // Parameters used by all stochastic ellipse families // Mandatory
    Parameters if using statistically generated ellipses  

    easpect: {1,1}  /* Aspect ratio. Used for lognormal and truncated power law
    distribution. */

    enumPoints: {12, 12} /*Number of vertices used in creating each elliptical
    fracture family. Number of elements must match number of ellipse families
    (first number in nShape) */

    eAngleOption: 0     /* All angles for ellipses: 0 - degrees 1 - radians
    (Must use numerical value for PI) */
	                        
    etheta: {-45, 45,} /*Ellipse fracture orientation.  The angle the normal
    vector makes with the z-axis */

    ephi: {0,0}   /* Ellipse fracture orientation.  The angle the projection of
    the normal onto the x-y plane makes with the x-axis */

    ebeta: {0, 0}   /* rotation around the normal vector */


    ekappa: {8,8}  /*Parameter for the fisher distribnShaprutions. The bigger,
    the more similar (less diverging) are the elliptical familiy's normal
    vectors */                

    //===========================================================================
    // Options Specific For Ellipse Lognormal Distribution (edistr=1): //
    Mandatory Parameters if using ellispes with lognormal distribution 

    //          NOTE: Number of elements must match number of //
    ellipse families (first number in nShape)

    eLogMean: {2}  //Mean value For Lognormal Distribution.       
	               
    eLogMax: {100} eLogMin: {1}

    esd: {.5} // Standard deviation for lognormal distributions of ellipses

    //===========================================================================
    //     Options Specific For Ellipse Exponential Distribution (edistr=3): //
    Mandatory Parameters if using ellispes with exponential distribution 


    eExpMean: {2}  //Mean value for Exponential  Distribution     eExpMax: {3}
    //Mean value for Exponential  Distribution     eExpMin: {1}  //Mean value
    for Exponential  Distribution     

    //===========================================================================
    //    Options Specific For Constant Size of ellipses (edistr=4):

    econst: {10, 10, 10}  // Constant radius, defined per family     
	               
    //===========================================================================
    // Options Specific For Ellipse Truncated Power-Law Distribution (edistr=2)
    // Mandatory Parameters if using ellipses with truncated power-law dist. 

    // NOTE: Number of elements must match number //       of ellipse families
    (first number in nShape)

    emin: {1} // Minimum radius for each ellipse family.  // For power law
    distributions. 

    emax: {6}  // Maximum radius for each ellipse family.  // For power law
    distributions. 
	                    
    ealpha: {2.4} // Alpha. Used in truncated power-law // distribution
    calculation





    /*==================================================================*/
    /*===================================================================*/ /*
    Rectangular Fractures Options           */ /* NOTE: Number of elements must
    match number of rectangle families   */ /*       (second number in nShape
    parameter)                            */
    /*=============================================================*/
    /*======================================================================*/

    //Number of rectangle families nFamRect: 0 //Having this option = 0 will
    ignore all rectangle family variables


    rLayer: {0,0} /* Defines which domain the family belings to.  Layer 0 is the
    entire domain.  Layers numbered > 0 coorespond to layers defined above 1
    corresponts to the first layer listed, 2 is the next layer listed, etc */


    /*rdist is a mandatory parameter if using statistically generated rectangles
    */ rdistr: {2,3}   /*  Rectangle statistical distribution options: 1 -
    lognormal distribution 2 - truncated power law distribution 3 - exponential
    distribution 4 - constant */

    rbetaDistribution: {1,1}   /* Beta is the rotation/twist about the z axis
    with the polygon centered on x-y plane at the orgin before rotation into 3d
    space
	                    
                        0 - uniform distribution [0, 2PI]    1 - constant angle
                        (specefied below by "rbeta")
	                    
                    */                                                 
	                
    r_p32Targets: {.1,.1} /* Rectangle families target fracture intensity per
    family.  When using stopCondition = 1 (defined at the top of the input
    file), familiies will be inserted untill the families desired fracture
    intensity has been reached. Once all families desired fracture intensity has
    been met, fracture generation will be complete.  */      
	                 
    //============================================================================
    // Parameters used by all stochastic rectangle families // Mandatory
    Parameters if using statistically generated rectangles   

    raspect: {1,1}  /* Aspect ratio */
	 
    rAngleOption: 0     /* All angles for rectangles: 0 - degrees 1 - radians
    (must be numerical value, cannot use "Pi") */
	 
    rtheta: {-45,45} /*Rectangle fracture orientation.  The angle the normal
    vector makes with the z-axis */

    rphi: {0,45} /* Rectangle fracture orientation.  The angle the projection of
    the normal onto the x-y plane makes with the x-axis */
	      
    rbeta: {0,0}   /* rotation around the normal vector */

    rkappa: {8,8}  /*Parameter for the fisher distributions. The bigger, the
    more similar (less diverging) are the rectangle familiy's normal vectors  */

    //=============================================================================
    // Options Specific For Rectangle Lognormal Distribution (rdistr=1): //
    Mandatory Parameters if using rectangles with lognormal distribution 

    rLogMean: {1.6}   /*For Lognormal Distribution.  Mean radius (1/2 rectangle
    length) in lognormal distribution for rectangles. */
	                   

    rLogMax: {100} rLogMin: {1}

    rsd: {.4}     /* Standard deviation for lognormal distributions of
    rectangles */

    //=============================================================================
    // Options Specific For Rectangle Truncated Power-Law Distribution
    (rdistr=2): // Mandatory Parameters if using rectangles with power-law
    distribution 

     rmin: {1,1}         /* Minimum radius for each rectangle family.  For power
     law distributions. */

     rmax: {6,5}   /* Maximum radius for each rectangle family.  For power law
     distributions. */

     ralpha: {2.4,2.5}   // Alpha. Used in truncated power-law // distribution
     calculation


    /*===========================================================================*/
    /* Options Specific For Rectangle Exponential Distribution (edistr=3):
    */ /* Mandatory Parameters if using rectangules with exponential
    distribution   */

    rExpMean: {2}  //Mean value for Exponential  Distribution rExpMax: {100}
    rExpMin: {1}

    /*===========================================================================*/
    /* Options Specific For Constant Size of rectangles (edistr=4):
    */

    rconst: {4,4}  // Constant radius, defined per rectangular family       
	               
    /*===========================================================================*/
    /*===========================================================================*/
    /* User-Specified Ellipses
    */ /* Mandatory Parameters if using user-ellipses
    */ /* NOTE: Number of elements must match number of user-ellipse families
    */ /*(third number in nShape parameter)
    */
    /*===========================================================================*/
    /* NOTE: Only one user-ellipse is placed into the domain per defined
    user-ellipse, with possibility of being rejected  */

	   
    userEllipsesOnOff: 0    //0 - User Ellipses off //1 - User Ellipses on

    UserEll_Input_File_Path: ./TestCases/test/uEllInput.dat

    /*===========================================================================*/
    /*===========================================================================*/
    /*  User-Specified Ellipses
    */ /*  Mandatory Parameters if using user-ellipses
    */ /*  NOTE: Number of elements must match number of user-ellipse families.
    */ /*  NOTE: Only one user-ellipse is placed into the domain per defined
    */ /*        user-ellipse, with possibility of being rejected
    */
    /*===========================================================================*/
    /*===========================================================================*/

    userEllByCoord: 0 /*  0 - User ellipses defined by coordinates off 1 - User
    ellipses defined by coordinates on */

    EllByCoord_Input_File_Path:
    /home/jharrod/GitProjects/DFNGen/DFNC++Version/inputFiles/
    userPolygons/ellCoords.dat



    /*===========================================================================*/
    /* User-Specified Rectangles
    */ /* Mandatory Parameters if using user-rectangles
    */ /* NOTE: Number of elements must match number of user-ellipse families
    */ /* (fourth number in nShape parameter)
    */
    /*===========================================================================*/
    /* NOTE: Only one user-rectangle is placed into the domain per defined
    user-rectangle, with possibility of being rejected  */
	         

    userRectanglesOnOff: 1    //0 - User Rectangles off //1 - User Rectangles on
	                          
    UserRect_Input_File_Path: /home/nknapp/dfnWorks-Version2.0/
    tests/define_4_user_rects.dat 

    /*===========================================================================*/
    /* If you would like to input user specified rectangles according to their
    coordinates, you can use the parameter userDefCoordRec. In that case, all
    of the user specified rectangles will have to be according to coordinates.
    */

    userRecByCoord: 0 //  0 - user defined rectangles not used //  1 - user
    defined rectangles used and defined by input file:

    RectByCoord_Input_File_Path: ./inputFiles/userPolygons/rectCoords.dat


    /*WARNING: userDefCoordRec can cause LaGriT errors because the polygon
    vertices are not put in clockwise or counter-clockwise order.  If errors
    (Usualy seg fualt during meshing if using LaGriT), try to reorder the points
    till u get it right.  Also, coordinates must be co-planar */

    /*===========================================================================*/
    // Aperture [m] /* Mandatory parameter, and can be specified in several
    ways: - 1)meanAperture and stdAperture for using LogNormal distribution.  -
    2)apertureFromTransmissivity, first transmissivity is defined, and then,
    using a cubic law, the aperture is calculated; - 3)constantAperture, all
    fractures, regardless of their size, will have the same aperture value; -
    4)lengthCorrelatedAperture, aperture is defined as a function of fracture
    size*/

    //NOTE: Only one aperture type may be used at a time 

    aperture: 3  //choise of aperture option described above

    //(**** 1)meanAperture and stdAperture for using LogNormal
    distribution.********) meanAperture:  -3 /*Mean value for aperture using
    normal distribution */ stdAperture: 0.8  //Standard deviation     

    /*(****** 2)apertureFromTransmissivity, first transmissivity is defined, and
    then, using a cubic law, the aperture is calculated;***************/
    apertureFromTransmissivity: {1.6e-9, 0.8} /* Transmissivity is calculated as
    transmissivity = F*R^k, where F is a first element in
    aperturefromTransmissivity, k is a second element and R is a mean radius of
    a polygon.  Aperture is calculated according to cubic law as
    b=(transmissivity*12)^1/3 */
	       
    /*(****** 3)constantAperture, all fractures, regardless of their size, will
    have the same aperture value;    **********************************/
	      
    constantAperture: 1e-5  //Sets constant aperture for all fractures 

    /*(******** 4)lengthCorrelatedAperture, aperture is defined as a function of
    fracture size *******************/
	       
    lengthCorrelatedAperture: {5e-5, 0.5} /*Length Correlated Aperture Option:
    Aperture is calculated by: b=F*R^k, where F is a first element in
    lengthCorrelatedAperture, k is a second element and R is a mean radius of a
    polygon.*/


    //============================================================================
    //Permeability /* Options: 0: Permeability of each fracture is a function of
    fracture aperture, given by k=(b^2)/12, where b is an aperture and k is
    permeability 1: Constant permeabilty for all fractures */

    permOption: 1  //See above for options

    constantPermeability: 1e-12  //Constant permeability for all fractures 

    //=============================================================================

    outputAcceptedRadiiPerFamily:1 /* output radii files for each family
    containing the final radii chosen */

    disableFram:0 /* 0 if FRAM (feature rejection algorithm for meshing) is
    disabled, 1 otherwise */

    outputFinalRadiiPerFamily:1 /* output radii files for each family containing
    the final radii chosen */

    insertUserRectanglesFirst:1 /* 1 if user defined rectangles should be
    inserted first, 0 otherwise */

    forceLargeFractures:0 /* Force large fractures to be included in the network
    */

    radiiListIncrease: 0.1 /* Increase the length of the initially generated
    radii list (before rejections) by this percentage */

    removeFracturesLessThan: 0 /*Used to change the lower cutoff of fracture
    size*/
	 

Fracture Cluster Management
---------------------------

Introduction
************* 
This section covers dfnGen 2.0’s cluster group management system
and the isolated fracture removal process. 

Fracture clusters are used in dfnGen for isolated fracture removal after the DFN
has been generated and before dfnGen generates its output files. An isolated
fracture is a fracture that does not intersect any other fractures and will not
contribute to flow. Fracture clusters are also considered isolated when the
cluster does not connect the users defined domain boundary faces.

NOTE: Isolated fracture removal only removes fractures with no intersections
when the input option ``ignoreBoundaryFaces`` is set to 1. 

Fracture cluster data is kept and updated with each new polygon/fracture added
to a DFN.

Algorithm Overview
*******************
In the dfnGen source code, relevant
functions are:
1. ``intersectionChecking()``, found in ``computationalGeometry.cpp``
2. ``assignGroup()``, found in ``clusterGroups.cpp``
3. ``updateGroups()``, found in ``clusterGroups.cpp``
4. ``getCluster()``, found in ``clusterGroups.cpp``
 	
As a new polygon is being tested for intersections and for feature sizes less
than ``h`` (these checks happen one intersection at a time), three lists are
maintained:
-a.	Intersected polygons list (variable ``tempIntersectList`` in
``intersectionChecking()``).  This list contains indices/pointers to all the
polygons which the new polygon has intersected in the order that they occur. 
-b. Intersections list (variable ``tempIntPts`` in ``intersectionChecking()``). This
list contains all new intersections (``IntPoints`` structures) created by the
new polygon in the order that they occur. 
-c.	Encountered cluster groups list
(variable ``encounteredGroups`` in ``intersectionChecking()``). This list
contains all other cluster group numbers which the new polygon has intersected
with after the new polygon already has been assigned a group number. 

E.g. If from the first intersection, the new polygon is assigned to group 5, and
the next intersection is with a fracture in group 2, ‘2’ is the first group
saved to the encountered groups.

When a polygon bridges more than one group, there will be several different
cluster groups to update. 

If for any reason the fracture is rejected (FRAM rejects it while checking an
intersection for features of size less than ``h``), these lists are deleted and
the fracture is either re-translated to a new position, or a new fracture is
generated. If the fracture is accepted, the data in these lists are used to
update the permanent fracture cluster data. 

Code overview
+++++++++++++++

1.	Go through previously accepted polygons and test
for intersections with the new polygon being added to the DFN.  Once an
intersection is found (by function ``intersectionChecking()``) and has passed
the FRAM tests, several things happen:
2.	The intersection structure for the newest intersection is appended to the
   temp intersection array ``tempIntPts``.
3.	The index of the fracture the new polygon intersects with is appended to the
   intersected polygons list ``tempIntersectList``.
4.	The index to the new intersection structure’s place in the permanent intPts
   array, if the new polygon is accepted, is calculated and appended to the new
   polygons list ``intersectionIndex``. That is, the index that is saved is the
   index the intersection will have once moved to the permanent array if it is
   not rejected.
5.	Any triple intersection points are saved to a temporary list of structure
   tempData. This structure contains the triple intersection point, and the
   index to the place in the permanent triplePoints list of where it will go if
   the polygon is not rejected (similar to step 4).
6.	New Polygon Gets a Cluster Group Number (``groupNum`` in the Poly struct).
   a.	If it is the first intersection found, the new polygon inherits the
   cluster group number of the intersecting polygon.  b.	If the new polygon
   has already been given a cluster group number from intersecting another
   fracture), the intersecting polygon’s cluster group number is added to the
   encountered cluster groups list ``encounteredGroups``. This will be used to
   update the fractures and cluster groups (merging the two groups together) IF
   the new polygon does not end up being rejected (it still has more polygons to
   check for intersections with).

Numbers 2 to 5 repeat until all fractures have been checked for intersections
with the new polygon. If the polygon has not been rejected during the process: 

7.	If no intersections were found after searching through previously accepted
   polygons, the new polygon is given a new cluster group number using the
   ``assignGroup()`` function (details below).

8.	The new polygon is moved to the permanent ``acceptedPoly`` list.

9.	If there were new intersections, they are now appended to the permanent
   ``intPts`` list.

10.	All intersected polygons will have their ``intersectionIndex`` list updated
    with the indices of the new intersections. We do this by adding the index of
    each new intersection to its corresponding polygon in the same order which
    they were found. The list for polygons we encountered is in the variable
    ``tempIntersectList``. 

E.g. if the permanent ``intPts`` intersection list already has 10 (indexes 0 -
9) intersections from  previous fractures and we just added 3 more fractures and
intersections, and each fracture can only intersect with the new polygon once,
the indexes to the new intersections once they are moved to the permanent
``intPts`` list will be indexes 10, 11, and 12 (indexes start at 0). So, we
append to the first polygon listed in the tempIntersectList index 10, the second
polygon in the list index 11, and the third index 12. 

11.	If there are new triple intersection points, they are now appended to the
    permanent ``triplePoints`` list. The temporary triple intersection points
    are held in a list of ``TrieplePtTempData`` structures. This structure
    contains the triple intersection point, and the index for each of the
    intersections it belongs to (three total). One of the intersections will be
    a new intersection just created by the new polygon, and the other two will
    be a triple intersection point on previously accepted intersections. 

The new triple intersection point is added to the permanent ``triplePoints``
array, and then its index in that permanent array is appended to the
intersection structure variable ``triplePointsIdx`` for the intersection that it
belongs to. 

12.	 The last thing that is done is a call to the function ``updateGroups()``
     (details below). 


Function ``assignGroup()``: assign polygon to cluster group
*********************************************************************

The function ``assignGroup()``, defined in clusterGroups.cpp,  is used to assign
a new polygon to a new cluster group. This function is for polygons that do not
intersect with any other polygons; otherwise a cluster group will be inherited
from the intersected polygon. 

Arguments to this function: 
1.	Poly structure reference. A reference to the new
polygon being assigned a new group. 
2.	Stats structure reference. The program
statistics object (variable name pstats throughout the code). The Stats
structure contains two structures within it that contain all the cluster group
information. These structures are ``FractureGroups`` and ``GroupData`` (details
below). 
3.	Index (integer) of the new polygons place in the permanent polygon
list ``acceptedPoly``. 

Code Overview (See sections on GroupData and FractureGroups structures for their details)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

1.	The new polygon is assigned the next available group number. This comes from
   the Stats variable ``nextGroupNum``.

2.	A ``GroupData`` structure is created.

3.	Inside the ``GroupData`` structure, there is a boolean array of six
   elements. This array, faces, contains connectivity information for the
   cluster. There is an element for each of the six faces, or walls, of the
   domain. False meaning it is not touching that face, true meaning it is
   touching the face (see GroupData section for more details). Likewise, there
   is another faces array in the polygon Poly structure. 

The polygon’s faces array and the ``GroupData’s`` faces array are bitwise ORed
together so that anywhere there is a true in the polygons faces array, there
will be a true in the ``GroupData’s`` faces array. After many polygons go
through this process for a single cluster group, by looking at the GroupData’s
faces array we are able to see which domain faces the cluster connects.

4.	Next, the variable size inside of the structure ``GroupData`` is
   incremented. This contains the number of fractures contained in the fracture
   cluster group.  5.	The ``GroupData`` structure is now saved to a permanent
   location within the ``Stats`` structure.  6.	A ``FractureGroups`` structure
   is now created.  7.	The new ``FractureGroups`` structure is assigned the
   same group number from step 1 using the same ``nextGroupNum`` variable.  8.
   ``nextGroupNum`` is incremented.  9.	Inside the ``FractrueGroups`` structure
   is the list (polyList) of polygons belonging to the group. The index for the
   location in the permanent polygon list, ``acceptedPoly``, for the new polygon
   is added to this list.  10.	The ``FractureGroup`` structure is then saved to
   a permanent location within the ``Stats`` structure. 

Function  ``updateGroups()`` : update fracture cluster group information
*************************************************************************

The function ``updateGroups()``, defined in clusterGroups.cpp,  is used to
update the fracture cluster group information for new polygons that have
intersected other polygons. When updating the cluster group information, there
are two cases: A.	The new polygon only intersected with polygons of a single
group.  B.	The new polygon intersected and connected more than one group. The
groups now need to be merged together into a single group. 

Arguments to this function: 1.	``Poly`` structure reference. A reference to the
new polygon being added to fracture cluster groups.  2.	Permanent list of
accepted polygons already in the DFN (variable ``acceptedPoly``).  3.	List of
cluster groups which the new polygon has intersected with, if more than one
group (see example in part c on page 1).  4.	``Stats`` structure reference.
The program statistics object (variable name ``pstats`` throughout the code).
The ``Stats`` structure contains two structures within it that contain all the
cluster group information. These structures are ``FractureGroups`` and
``GroupData`` (details below).  5.	Index (integer) of the new polygons place in
the permanent polygon list ``acceptedPoly``. 


Case A
++++++++
1.	The new polygons faces data is ORed into its corresponding
``GroupData`` structure. 

The ``GroupData`` array, (in variable pstats) is always aligned with cluster
group numbers. Group numbers start at 1, the indexes to the array start at 0.
E.g. to access the ``GroupData`` structure for cluster group 12, it is the
variable ``pstats.groupData[12 – 1]``. 

2.	The corresponding ``GroupData`` structure’s variable size is incremented
   (number of polygons in the group). 

3.	Next, the corresponding ``FractureGroup`` structure must be found. This has
   to be done by searching through the array (``pstats.fractGroup``) and
   comparing the new polygons ``groupNum`` and the group number in the
   ``FractureGroup`` structure. 

See below for an explanation as to why we have to search for the group number,
and why the ``GroupData`` and ``FractureGroup`` structures are not combined a
single structure.

4.	Once the correct FractureGroup structure is found, the index to the new
   polygon in the permanent polygon list acceptedPoly is appended to the list
   polyList in the ``FractureGroups`` structure. 

Case B
+++++++
1.	The new polygon’s corresponding ``FractureGroup`` structure
is searched and found. The poly is added to the ``FractureGroup`` structure (see
3 and 4 in Case A).

2.	The new polygon’s faces data is ORed into the new polygons corresponding
   ``GroupData`` structure (see 1 in Case A).

3.	The new polygon’s corresponding ``GroupData`` structure has it’s size
   incremented (see 2 in case A). 

Merge Cluster Groups
++++++++++++++++++++++
4.	For all groups in the
``encounteredGroups`` list (see part c under Algorithm Overview at the beginning
of this document), the ``GroupData’s`` size variable, is added to and the
``GroupData`` structure corresponding to the new polygons group number. 

5.	The ``GroupData’s`` faces array for each of the groups in
   ``encounteredGroups`` is ORed together with the ``GroupData`` structure
   corresponding to the new polygons group. 

6.	While doing steps 4 and 5, the ``GroupData’s`` valid variable for each group
   in ``encounteredGroups`` is set to false. This means that that
   ``GroupData’s`` data is no longer valid and it should be disregarded (see
   next section of this document for more details).

7.	Search for the corresponding ``FractureGroup`` for the group numbers listed
   in ``encounteredGroups``. 

8.	For each of the corresponding ``FractureGroups`` for the group numbers
   listed in ``encounteredGroups``, change the ``groupNum`` variable in
   ``FractureGroups`` to the new polygon’s group number. 

9.	Inside the ``FractureGroups`` structure, go through all the polygons listed
   there and change their groupNum group number variables to match the new
   polygon’s group number.


Group data structures:  ``GroupData`` and ``FractureGroups``
************************************************************************

Structure Definitions:

NOTE: Both structures use a constructor to initialize their variables (see code
in ``structures.cpp``).

.. code-block:: c

    struct GroupData { unsigned int size; bool valid; bool faces[6]; /* Domain
    boundary sides/faces that this cluster connects to..  Index Key: [0]: -x
    face, [1]: +x face [2]: -y face, [3]: +y face [4]: -z face, [5]: +z face */
    };

    struct FractureGroups { unsigned long long int groupNum;
    std::vector<unsigned int> polyList; };

The reason we do not combine the ``GroupData`` and ``FractureGroups`` into a
single structure is for performance reasons. 

If the two structures were combined, a problem arises when two different
fracture groups merge together. The structures could no longer be aligned with
the group numbers in an array because the group numbers will be changing
whenever groups merge together. This would cause constant searching every time
you needed to access any of the data. We still need to search when dealing with
the ``FractureGroups`` array, but save some performance costs by being able to
access everything in the GroupData array for any group number without any
searching. 

If you tried to force the alignment by having empty structures where groups were
merged to another group, it would require constantly deleting and reallocating
the arrays, and copying polygons to the new group every time groups merged to
make everything fit as it should. This would be a huge performance hit and
probably the worst solution. 
 
The solution implemented was to keep the two structures separate. When clusters
merge together, we simply have to set the old cluster’s ``GroupData`` valid bit
false (no search required), add its size and OR the faces to the ``GroupData``
structure that it is being merged into. We then need to find (search required)
the group number that is about to go away in the ``FractureGroups`` list and
change it to the new group number, and change the polygons in that group to the
same group number. Nothing is ever re-allocated.

NOTE: When the group number changes in ``FractureGroups`` after clusters merge
together, there will be two ``FractureGroups`` with the same group number but
with different polygons listed. To get all the polygons from a single group, the
two lists (or more if clusters continued to merge) need to be concatenated.


Funciton  ``getCluster()`` : get a cluster of fractures
********************************************************************

The ``getCluster()`` function is responsible for returning a list of  indexes to
the polygons which match the user’s connectivity option. 

Arguments to this function: 1. The program statistics Stats object (named pstats
throughout the code).  There are three user options that deal with fracture
connectivity: 1.	``boundaryFaces`` a.	This option provides a way to select
which faces or walls of the domain the user wants the fractures to connect with.
It is an array of 6 elements. A zero means not to enforce a connection, a 1
means fractures must have a connection to that face.  i.	Array elements match
to each boundary wall as follows: [0]: -x face, [1]: +x face [2]: -y face, [3]:
+y face [4]: -z face, [5]: +z face

2.	``ignoreBoundaryFaces`` a.	This option ignores the ``boundaryFaces``
   connectivity option completely and causes ``getCluster()`` to return a list
   of all polygons containing at least one intersection.  3.
   ``keepOnlyLargestCluster`` a.	This option keeps causes getCluster() to
   return the largest cluster using the above two options as well. If
   ``ignoreBoundaryFaces`` is being used, ``getCluster()`` will return the
   largest cluster of fractures in the DFN, even if they do not connect to any
   of the domain walls. If the ``boundaryFaces`` option is being used,
   ``getCluster()`` will return the largest cluster which connects the user’s
   required domain walls. 

Code Overview
+++++++++++++++

Part 1: Find cluster groups that match the user’s
connectivity option 1.	If the user is using the ``boundaryFaces`` option,
search through the GroupData and compare the ``GroupData’s`` faces array to the
users ``boundaryFaces`` array. If the groups faces connectivity array connects
the required user defined domain walls, add that group number to a list
(``matchingGroups`` in the code). 

2.	If the user is using the ``ignoreBoundaryFaces`` option, go through the
   ``GroupData`` array and add all the valid groups to the ``matchingGroups``
   array. 

3.	If the user is using the ``keepOnlyLargestCluster`` option, go through the
   ``matchingGroups`` array and compare each group’s ``GroupData.size``
   variable. Keep group with the largest size.


4.	Search for each group in the ``FractureGroups`` array and concatenate their
   polygon lists in a list to be returned by the function.


Exponential Distribution Class Implementation
---------------------------------------------

Introduction
************
This document is intended for new developers working
on dfnGen. It covers the implementation of the ``Distributions`` class, and its
composed exponential distribution class ``ExpDist`` in dfnGen V2.0. 

During dfnGen 2.0 development, new functionality was needed to allow for the
control of the range of numbers produced by the exponential distribution.
Previously, dfnGen V2.0 was developed using the C++ standard library,
``random``. 

Need for a Customized Exponential Distribution
*************************************************
There was need to control the
minimum fracture size for exponential distributed fracture families for research
purposes. Also, all fracture radii must always be greater than the minimum
feature size ``h``. 

The exponential distribution favors small numbers that caused a lot of
re-sampling when the distribution generated fracture radii of less than h or
smaller than the user’s defined minimum radius. Re-sampling the standard
library’s exponential distribution when the distribution produced numbers
outside of the user’s defined ranged was found to be very inefficient and could
halt program execution when the exponential mean did not match the range which
the user had chosen. The program could re-sample the distribution thousands of
times before an acceptable radius was generated.

With the standard library’s implementation, complete randomness is forced from
the distribution. There was no way to control the range of numbers produced by
the distribution. A way of limiting the output of the distribution was needed
that did not involve re-sampling.

Implementation Overview *********************** Our implementation uses the CDF
determine the random variable range from which we need to sample. When the
inverse CDF is sampled uniformly between 0 and 1, an exponential distribution
will be produced that matches that of the standard library’s exponential
distribution output. By limiting the random variable range, we can sample
between the users desired minimum and maximum without generating numbers outside
of that range.

To limit the range of output, we use the exponential CDF formula: ``rv = 1 – e
(-lambda * output)``, where rv is the random variable needed to produce output
when plugged into the inverse CDF function: ``output = -log(1-rv)/lambda``. 

When the user’s defined minimum and maximum are plugged in to output, we get the
range which the distribution should be sample from in order to get a exponential
distribution bounded by the users defined minimum and maximum.

These variables, the range to sample the exponential distribution, are saved to
minDistInput and maxDistInput in the family’s corresponding Shape structure.  


Implementation Details
***********************

Our implementation uses
composition for increased modularity and to increase the ease of adding
additional distribution types in the future. 

The ``ExpDist`` class is a sub-class of the ``Distributions`` class. This allows
the programmer to only create one instance of the ``Distributions`` class, and
the ``ExpDist`` class and any other distribution classes added in the future
will be automatically set up and initialized by ``Distributions`` constructor.

``Distributions`` Class ************************ The ``Distributions`` class
contains functions and variables that are needed to initialize the ``ExpDist``
class, and likely other distribution classes added in the future. It also
contains the ``ExpDist`` class within it. 

When the ``Distributions`` class is created, its constructor function is called.
This function creates and initializes the ``ExpDist`` class within the
``Distributions`` class. 

One of the issues with the exponential distribution is that if given 1.0 as a
random variable, the distribution returns inf. To maximize the range of numbers
which can be produced, we need to know the largest value less than 1.0 that the
computer is able to produce. 

The ``Distributions`` class has a function called ``getMaxDecimalDouble()``.
During ``Distributions`` creation, ``getMaxDecimalDouble()`` returns the largest
number less than 1, e.g. 0.999….9, to its maximum precision. This variable is
saved to variable ``maxInput`` in the ``Distributions`` class. It is also passed
to the ``ExpDist`` class during its creation. 

Also in the ``Distributions`` class constructor, the function
``checkDistributionUserInput()`` is called. This function error checks user
exponential input options and finishes initializing the exponential
distribution. The function is written with the expectation for other
distributions to be added and will be easy to modify. 

In ``checkDistributionUserInput()``, ``minDistInput`` and ``maxDistInput`` are
initialized for each family using exponential distribution (see Implementation
Overview). Error checks are performed to ensure ``minDistInput`` and
``maxDistInput`` are within the machines capabilities to produce. If they are
set very high, plugging in ``maxInput`` (see above) into the distribution can
produce a number smaller than the requested maximum, and possibly minimum. If
the user defined maximum cannot be produced stochastically, the user is warned
and the user defined maximum is set to the largest possible number that the
machine can produce. The minimum is then checked to ensure it is still less than
the maximum. If it is not, the error is reported to the user and the program
terminates. Otherwise, everything is okay and the ``ExpDist`` class is ready to
use. 

``ExpDist`` Class
*******************

After the ``ExpDist`` class has been
initialized, the ``getValue()`` function can be used to return random numbers
from the exponential distribution. The function has been overloaded to either be
given the random input variable (random variable between 0 and 1) as an
argument, or be given a range between 0 and 1 to generate random input variables
from. 

Other Details
****************
The C++ standard random library is still used for
generating uniform random reals. The 64-bit Mersenne twister engine random
generator is the random generator used for all dfnGen’s random variables. It is
created in main() and passed as a reference to the Distributions class during
its creation. 

Hotkey ``~``
--------------

If the dfnGen takes too long, one can use ``~`` to
abort fracture generation process and contine to the next step of outputting the
data related the fractures generated until that point in time.

Developer notes: Variables that might need adjusting
**********************************************************************

Due to the recent changes in the LaGriT meshing script, there are a couple parts
of the code that might need adjusting.

Distance between intersections
+++++++++++++++++++++++++++++++++

After updates to
the meshing script, there are cases where intersections can have only one
triangular element between them. If the distance between intersections needs to
be increased, adjust the last argument in ``checkDistDistToOldIntersections()``
and ``checkDistToNewIntersections()``, lines 645 and 653 in
computationalGeometry.cpp

Allowed Intersection Angles
+++++++++++++++++++++++++++

The changes to the
LaGriT meshing script might allow for smaller angles without causing problems in
the mesh. This is for intersection angles crossing the edge of a polygon, not
for triple intersections.
 
To change the angle, adjust the variable ``const static double minDist2`` found
on line 1260 in ``computationalGeometry.cpp``. 

``minDist2`` is the minimum distance allowed to the edge of a polygon from the
first discretized intersection point, not including the end points (the first
node in from the end point). 

Adding new user input variables to dfnGen 2.0
*********************************************
1.	Add option/variable to an
existing input file. Tag the option’s name with ``:`` at the end.  There must be
at least 1 space or a new line in between the ``:`` and the data.  E.g.
``newUserOption: 12``

2.	Add ``extern varType varName`` to ``input.h``. Most user input variables are
   stored globally. ``input.h`` must be included in any files that need access
   to them.

3.	Update ``readInput.cpp``. Declare the new global variable (the same variable
   as in step 1 but without the ``extern`` keyword) at the top of this file. 

This file contains the function ``getInput()``.  This function is responsible
for reading in user input files.  ``getInput()`` needs to be updated to read in
the new variable. I suggest looking for a similar variable, whether it be an
array, a flag, or a number, and use that as an example to read in the new input
option. 

The function ``searchVar()`` is very helpful in reading variables from the user
input file. The first argument is the file object (C++ ifstream object), the
second argument is a string of the variable/option name in the input file
including the ``:`` at the end.  After this function runs, the file pointer will
be pointing to the data directly after the input options name (e.g. in step 1,
the file pointer will be pointing to the white space directly after the colon.)
All that is left is to read the input variable in to a C++ variable e.g. ``file
>> var``. NOTE: C++ is smart and will skip multiple spaces and/or new line
characters. 

If the option requires a list or array as the options parameters, see similar
options in readInput.cpp. Instead of reading in directly to a variable (``file
>> var``), a function will be required to parse the list. See
``readInputFunctions.cpp`` and ``readInputFunctions.h`` for some examples on how
to do this.

4.  The last thing to do is to write/edit the code that will use the new option.
    Include ``input.h`` in any new file to access the global variable. If the
    new variable is an array, don’t forget to use ``delete[]`` to free its
    memory after the variable is no longer needed. If a new file was created, be
    sure to edit the makefile to include it in the built. 






