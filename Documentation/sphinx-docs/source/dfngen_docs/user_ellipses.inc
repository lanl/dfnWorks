
User Defined Ellipses
====================================

Ellipses can be included using two different formats: general or coordinates. 

userEllipsesOnOff
------------------------
Description: Selection if general user defined ellipses are going to be used. If this option is activated, then the file :ref:`UserEll_Input_File_Path` is read. The path to that file must be valid. 

Type: boolean (0/1)

| 0: Do not include general user defined ellipses
| 1: Do include general user defined ellipses

----


UserEll_Input_File_Path
------------------------
Description: Filepath for general user defined ellipses

Type: string

Example:

.. code-block:: c

    UserEll_Input_File_Path: /dfnWorks/examples/4_user_ell_uniform/define_4_user_ellipses.dat     

----


General user defined ellipses parameters
------------------------------------------------
Below are the required parameters for the general user defined ellipses

nUserEll
^^^^^^^^^^^^^^^^
Description: Number of User Defined Ellipses

Type: Int

Example:

.. code-block:: c

    nUserEll: 2 // 2 ellipses are expected in the file

    
----


Number_of_Vertices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Number of vertices defining the boundary of each ellipse. One per line per fracture.

Type: Int 

Example:


.. code-block:: c

    Number_of_Vertices:
    12 // fracture 1 has 12 vertices
    8 // fracture 2 has 8 vertices


    
----



Radii
^^^^^^^^^^^^^^^^
Description: Radius of each ellipse

Type: Double, one value per line per fracture

Example:

.. code-block:: c

    Radii:
    0.5 // fracture 1 has a radius of 0.5 m
    1 // fracture 1 has a radius of 1 m

    
----


Aspect_Ratio
^^^^^^^^^^^^^^^^
Description: Aspect Ratio for each ellipse

Type: Double, one value per line per fracture

Example:

.. code-block:: c

    Aspect_Ratio:
    1 // fracture 1 has a radius of 1
    2 // fracture 2 has a radius of 2

    
----


AngleOption
^^^^^^^^^^^^^^^^
Description: Selection of Radius / Degrees

Type: boolean

| 0: All angles in radians
| 1: All angles in degrees

Example:

.. code-block:: c

    AngleOption:
    0 // fracture 1 has angles in radians
    1 // fracture 2 has angles in degrees


    
----


Beta
^^^^^^^^^^^^^^^^
Description: Rotation around center for each ellipse (one per line)

Type: Double, one value per line per fracture

Example:

.. code-block:: c

    AngleOption:
    0 // no rotation for fracture 1
    45 // rotate fracture 2 by 45 degrees

    
----


Translation
^^^^^^^^^^^^^^^^
Description: Translation of each ellipse according to its center {x,y,z} (one per line)

Type: Set of double values {x,y,z}

Example:

.. code-block:: c

    Translation:
    {-0.2,0,0} // Fracture 1 has a center at -0.2, 0, 0
    {0,1,0} // Fracture 2 has a center at 0, 1, 0 

    
----


userOrientationOption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description: Selection of fracture orientation definition. The same orientation option must be used for all fractures.

    | 0 : Normal Vector -> Normal {x,y,z}
    | 1 : Trend / Plunge 
    | 2 : Dip / Strike 

Type: Value of 0,1,2  

Example:


.. code-block:: c

    userOrientationOption: 0 // Fracture orientation will be defined using normal vectors

.. note:: 
    | If option 0 is selected, the keyword normal is required. 
    | If option 1 is selected, the keyword Trend_Plunge is required. 
    | If option 2 is selected, the keyword Dip_Strike is required. 

.. warning:: You cannot mix orientation options


    
----


Normal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Normal vector of each ellipse according {x,y,z} (one per line)

Type: Set of double values {x,y,z}

Example:

.. code-block:: c

    Normal:
    {0,0,1} // Fracture 1 has a normal vector of [0,0,1]
    {1,1,0} // Fracture 1 has a normal vector of [1,1,0]

.. note:: Vectors *do not* need to be normalized

    
----


Trend_Plunge
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Trend and plunge for each fracture

Type: Set of double values {trend,plunge}

Example:

.. code-block:: c

    Trend_Plunge:
    {45, 90} // Fracture 1 has a trend of 45 and plunge of 90
    {0, 37} // Fracture 2 has a trend of 0 and plunge of 37

.. warning:: :ref:`AngleOption` must be set to degrees

    
----


Dip_Strike
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description: Dip and Strike for each fracture

Type: Set of double values {dip,strike}

Example:

.. code-block:: c

    Trend_Plunge:
    {45, 90} // Fracture 1 has a dip of 45 and strike of 90
    {0, 37} // Fracture 2 has a dip of 0 and strike of 37

.. warning:: :ref:`AngleOption` must be set to degrees


    
----


General Ellipse Input Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: c

    /************************* USER DEFINED ELLIPSES ***************************/
    /*****************************************************************************/

    /*****************************************************************************/
    //Number of User Defined Ellipses
    /*****************************************************************************/
    nUserEll: 4


    /*****************************************************************************/
    //Radius for each ellipse (one per line)
    /*****************************************************************************/
    Radii:
    0.5
    0.5
    0.4
    0.4


    /*****************************************************************************/
    //Aspect Ratio for each ellipse (one per line)
    /*****************************************************************************/
    Aspect_Ratio: 
    1
    1
    1
    1


    /*****************************************************************************/
    //Angle Option: 0 - All angles in radians   
    //              1 - All angles in degrees   
    /*****************************************************************************/
    AngleOption: 
    1
    1
    1
    1

    /*****************************************************************************/
    //Rotation around center for each ellipse (one per line)
    /*****************************************************************************/
    Beta:
    0
    0
    0
    0

    /*****************************************************************************/
    //Translation of each ellipse according to its center {x,y,z} (one per line)
    /*****************************************************************************/
    Translation:
    {-0.2,0,0}
    {0,0,0}
    {0.2,0,0.2}
    {0.2,0,-0.2}


    /*****************************************************************************/
    //  userOrientationOption: 
    //  0 - Normal Vector -> Normal {x,y,z}
    //  1 - Trend / Plunge -> Trend_Plunge {trend, plunge} -> Must be degrees
    //  2 - Dip / Strike - > Dip_Strike {dip, strike} -> Must be degrees
    /*****************************************************************************/

    userOrientationOption: 0 


    /*****************************************************************************/
    //Normal Vector for each ellipse (one per line)
    /*****************************************************************************/
    Normal:
    {0,0,1}
    {1,0,0}
    {0,0,1}
    {0,0,1}


    Number_of_Vertices:
    8
    8
    8
    8



    
----


userEllByCoord
------------------------
Description: Selection if user defined ellipses by coordinate are going to be used. If this option is activated, then the file :ref:`EllByCoord_Input_File_Path` is read. The path to that file must be valid. 

Type: boolean (0/1)

| 0: Do not include user defined ellipses by coordinate 
| 1: Include user defined ellipses by coordinate
  
..  warning:: The same number of vertices must be used for all fractures.

    
----


EllByCoord_Input_File_Path
------------------------------
Description: File path name for user defined ellipses by coordinate

Type: string

Example:

.. code-block:: c

    EllByCoord_Input_File_Path: /dfnWorks/example/4_user_ell/ellCoords.dat


    
----


User defined ellipses by coordinate parameters
------------------------------------------------
Below are the required parameters for the user defined ellipses by coordinate

    
----


nEllipses
^^^^^^^^^^^^^^^^
Description: Number of User Defined Ellipses

Type: Integer

Example:

.. code-block:: c

    nEllipses: 2

    
----


nNodes
^^^^^^^^^^^^^^^^
Description: Number of nodes for all ellipses

Type: Integer

.. code-block:: c

    nNodes: 5


    
----


Coordinates
^^^^^^^^^^^^^^^^
Description: Coordinates / Vertices for each ellipse. 

Type: Set of :ref:`nNodes` triples :math:`{x_0, y_0, z_0} {x_1, y_1, z_1} \ldots {x_n, y_n, z_n}`  

.. code-block:: c

    Coordinates:
    {-2,-1,0} {1,-2,0} {2,0,0} {0,2,0} {-2,1,0}
    {0,-0.3,-1} {0,.5,-.7} {0,.7,1} {0,-.7,1} {0,-1,0} 

.. warning:: Coordinates must be listed in clockwise, or counterclockwise order. Coordinates must be co-planar

    
----


Ellipse By Coordinate Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: c

    /************************************************************************/
    /*                 ELLIPSES SPECIFIED BY COORDINATES                  */
    /************************************************************************/
    // NOTE: Coordinates must be listed in clockwise, or counterclockwise order
    //       Coordinates must be co-planar

    /************************************************************************/
    // Number of Ellipses Defined
    /************************************************************************/

    nEllipses: 2


    /************************************************************************/
    // Number of nodes for all ellipses
    /************************************************************************/

    nNodes: 5


    /************************************************************************/
    // Coordinates (4 vertice coordinates per line/One rectangle per line)
    /************************************************************************/
    // One Ellipse per line (White space and new lines should not matter)
    // Format: {x1,y1,z1} {x2,y2,z2} {x3,y3,z3} {x4,y4,z4} ... {xn, yn, zn}

    Coordinates:

    {-2,-1,0} {1,-2,0} {2,0,0} {0,2,0} {-2,1,0}
    {0,-0.3,-1} {0,.5,-.7} {0,.7,1} {0,-.7,1} {0,-1,0} 


