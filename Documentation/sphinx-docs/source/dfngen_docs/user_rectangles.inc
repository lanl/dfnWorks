
User Defined Rectangles
====================================

Deterministic Rectangles can be included using two different formats: general or coordinates. 

userRectanglesOnOff
------------------------
Description: Selection if general user defined rectangles are going to be used. If this option is activated, then the file :ref:`UserRect_Input_File_Path` is read. The path to that file must be valid. 

Type: boolean (0/1)

| 0: Do not include general user defined rectangles
| 1: Do include general user defined rectangles


    
----


UserRect_Input_File_Path
--------------------------------------
Description: Filepath for general user defined rectangles

Type: string

Example:

.. code-block:: c

    UserRect_Input_File_Path: /dfnWorks/examples/4_user_rects/define_4_user_rects.dat     


    
----


General user defined rectangles parameters
------------------------------------------------
Below are the required parameters for the general user defined rectangles

    
----


nUserRect
^^^^^^^^^^^^^^^^
Description: Number of user defined rectangles

Type: Int

Example:

.. code-block:: c

    nUserRect: 2 // There will be 2 rectangles expected.

----

Additional parameters have the same definitions as for user defined ellipses:

* :ref:`Radii`
* :ref:`Aspect_Ratio`
* :ref:`AngleOption`
* :ref:`Beta`
* :ref:`Translation`
* :ref:`userOrientationOption`
* :ref:`Normal`
* :ref:`Trend_Plunge`
* :ref:`Dip_Strike`

    
----


General Rectangle Input Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: c

    /************************* USER DEFINED rectangles ***************************/
    /*****************************************************************************/

    /*****************************************************************************/
    //Number of User Defined rectangles
    /*****************************************************************************/
    nUserRect: 4


    /*****************************************************************************/
    //Radius for each rectangle (one per line)
    /*****************************************************************************/
    Radii:
    0.5
    0.5
    0.4
    0.4


    /*****************************************************************************/
    //Aspect Ratio for each rectangle (one per line)
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
    //Rotation around center for each rectangle (one per line)
    /*****************************************************************************/
    Beta:
    0
    0
    0
    0

    /*****************************************************************************/
    //Translation of each rectangle according to its center {x,y,z} (one per line)
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
    //Normal Vector for each rectangle (one per line)
    /*****************************************************************************/
    Normal:
    {0,0,1}
    {1,0,0}
    {0,0,1}
    {0,0,1}


userRecByCoord
------------------------
Description: Selection if user defined rectangles by coordinate are going to be used. If this option is activated, then the file :ref:`RectByCoord_Input_File_Path` is read. The path to that file must be valid. 

Type: boolean (0/1)

| 0: Do not include user defined rectangles by coordinate 
| 1: include user defined rectangles by coordinate
  
..  warning:: The same number of vertices must be used for all fractures.

    
----


RectByCoord_Input_File_Path
------------------------------
Description: File path name for user defined rectangles by coordinate

Type: string

Example:

.. code-block:: c

    RectByCoord_Input_File_Path: /dfnWorks/example/4_user_rect/rectCoords.dat


    
----


User defined rectangles by coordinate parameters
------------------------------------------------
Below are the required parameters for the user defined rectangles by coordinate

    
----


nRectangles
^^^^^^^^^^^^^^^^
Description: Number of user defined rectangles

Type: Integer

Example:

.. code-block:: c

    nRectangles: 2


----

Fracture coordinates are defined using the same method as for ellipses. See :ref:`coordinates`.


Rectangle By Coordinate Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: c

    /************************************************************************/
    /*                 rectangles SPECIFIED BY COORDINATES                  */
    /************************************************************************/
    // NOTE: Coordinates must be listed in clockwise, or counterclockwise order
    //       Coordinates must be co-planar

    /************************************************************************/
    // Number of rectangles Defined
    /************************************************************************/

    nRectangles: 2

    /************************************************************************/
    // Coordinates (4 vertices coordinates per line/One rectangle per line)
    /************************************************************************/
    // One rectangle per line (White space and new lines should not matter)
    // Format: {x1,y1,z1} {x2,y2,z2} {x3,y3,z3} {x4,y4,z4} ... {xn, yn, zn}

    Coordinates:

    {-2,-1,0} {1,-2,0} {2,0,0} {0,2,0} {-2,1,0}
    {0,-0.3,-1} {0,.5,-.7} {0,.7,1} {0,-.7,1} {0,-1,0} 

