#ifndef _polyStruct_h_
#define _polyStruct_h_
#include <vector>
#include <cmath>


/**************************************************************************************/
/**************************************************************************************/
/*!
    The Poly structre is used to create and store fracrures/polygons.
*/
struct Poly {
    /*! Number of nodes/vertices in the polygon.*/
    int numberOfNodes;
    
    /*! Contains the index of the 'shapeFamilies' array in main() from which the fracture was
        created from. If the polygon was created from user defined input, it will be marked
        (-2 for user-rect, and -1 for user ell.
        The stochastic shape family numbers start at 0 for the first family, and increase by
        1 for each addition family. Families are in the same order which they are defined in the
        'famProb' variable in the input file, starting with ellipse families, then rectangular families. */
    int familyNum;
    
    /*! Fracture cluster number which the fracture belongs to. This variable is used to keep
        track of fracture connectivity. When a fracture first intersects another fracture,
        it inherits its cluster group number (groupNum). If a fracture does not intersect
        any other fractures, it is given a new and unique cluster group number. When a
        fracture bridges two different clusters, all clusters are merged to be have the
        cluster group number of the first intersecting fracture. */
    unsigned int groupNum;
    
    /*! Polygon area (Not calculated until after DFN generation has completed).*/
    float area;
    
    /*! X-radius before fracture-domain truncation. In the case of rectangles, radius is
        1/2 the width of the polygon.
    
        X-radius is equal to the value generated from randum distributions or given by the user
        in the case of constant distributions and user-defined fractures.*/
    double xradius;
    
    /*! Y-radius before fracture-domain truncation. In the case of rectangles, radius is 1/2
        the width of the polygon.
    
        Y-radius is equal to x-radius * aspect ratio (yradius = aspectRatio * xradius). */
    double yradius;
    
    /*! Aspect ratio of polygon before fracture-domain truncation. Must be value greater than zero.*/
    float aspectRatio;
    
    /*! Translation of polygon. This variable is set while building the polygon. */
    double translation[3];
    
    /*! Polygon normal. This variable is set while building the polygon.*/
    double normal[3];
    
    /*! The bounding box of the polygon. Set with createBoundingBox().
        Index Key:
        [0]: x minimum, [1]: x maximum
        [2]: y minimum, [3]: y maximum
        [4]: z minimum, [5]: z maximum */
    double boundingBox[6];
    
    /*! Aperture for the polygon/fracture. The aperture is set after DFN generation has
        completed (see assignAperture()).*/
    double aperture;
    
    /*! Double array for which hold the polygon's vertices. Vertices are stored in a 1-D array.
        e.g For n number of vertices, array will be: {x1, y1, z1, x2, y2, z2, ... , xn, yn, zn} */
    double *vertices;
    
    /*! Permiability for the polygon/fracture. Permeability is set after DFN generation has
        completed (see assignPermeability()). */
    double permeability;
    
    /*! The faces array contains flags (true/false) which denote which sides, if any, the polygon is touching.
        True (not zero) - Polygon is touching a domain boundary.
        False (0) - Polygon is not touching a domain boundary.
        Index Key:
        [0]: -x face, [1]: +x face
        [2]: -y face, [3]: +y face
        [4]: -z face, [5]: +z face
    */
    bool faces[6]; // Touching boundary faces of the fractures group, not neccesarily the faces of the fracture
    
    /*! When writing intersection points and poly vertices to output, we need them to be entirely on the x-y plane.
        XYPlane is used for error checking. During intersection rotations, the polygon is rotated to
        the x-y plane and it's vertices are changed within the Poly structure. Errors will occur if
        the same polygon was to be rotated again because although the vertices are now on the x-y plane, the
        normal is still the normal of the polygon in its 3D space. This variable prevents this from happening. */
    bool XYPlane;
    
    /*! True if the polygon has been truncated, false otherwise. This variable is used for re-translating polygons.
        If the polygon has been truncated, it must be re-built. Otherwise, it can simply be given a new translation. */
    bool truncated;
    
    /*! List of indices to the permanent intersection array ('intPts' in main()) which belong to this polygon. */
    std::vector<unsigned int> intersectionIndex;
    
    // Constructor
    Poly();
};



/**************************************************************************************/
/**************************************************************************************/
/*! Structure for 3D points/vertices. Constructor is overloaded for either creating
    a poing with uninitialized variables, or variables x, y, and z during object
    creation. */
struct Point {
    double x;
    double y;
    double z;
    
    Point();
    Point(double _x, double _y, double _z);
};



/**************************************************************************************/
/**************************************************************************************/
/*! Intersections structure.
    This structure contains all data pertaining to
    one intersection. This includes the IDs for both
    intersecting fractures, the intersection end points,
    a list of references to any triple intersection points existing
    on the intersection, and a flag denotting whether or not
    the intersection has been shortened by shrinkIntersection()
    during FRAM. */
struct IntPoints {
    /*! Fracture 1, index of fracture in the accpeted polygons list that this
        intersection belongs to ('fract1' and 'fract2' are in no particular order).*/
    long int fract1;
    
    /*! Fracture 2, index of fracture in the accpeted polygons list that this
        intersection belongs to ('fract1' and 'fract2' are in no particular order).*/
    long int fract2;
    
    /*! Intersection endpoint 1, x position.*/
    double x1;
    /*! Intersection endpoint 1, y position.*/
    double y1;
    /*! Intersection endpoint 1, z position.*/
    double z1;
    /*! Intersection endpoint 2, x position.*/
    double x2;
    /*! Intersection endpoint 2, y position.*/
    double y2;
    /*! Intersection endpoint 2, z position.*/
    double z2;
    /*! Triple intersection points/nodes on intersection. */
    std::vector<unsigned int> triplePointsIdx;
    
    /*! Used to update book keeping for keeping track of overal intersection length
        that has been shortened from shrinkIntersection(). Used in intersectionChecking(). */
    bool intersectionShortened;
    
    IntPoints(); // Constructor. initializes fract1, fract2 = -1
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Holds temporary triple point data while FRAM is checking
    all intersections for a new polygon/fracture.

    Once a fracture is accepted, the temporary triple point
    'triplePoint' is moved to its permanent location.

    'intIdx' is used to update intersection point structures' (IntPoints)
    rejerences to the new triple intersection points. 'intIdx' contains
    the index of the triple point in the permanent triple points array
    IF the fracture is accepted.

    If the fracture is rejected, this data is discraded.
*/
struct TriplePtTempData {
    /*! Triple intersection point. */
    Point triplePoint;
    /*! Index to 'triplePoints' array in main() to where this point would be stored
        if the FRAM checks pass. */
    std::vector<int> intIndex;
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    FractureGroups is a structure used to keep track of which fractures are in
    each cluster. FractureGroups works in conjunction with GroupData.

    FractGroups holds pointers/index numbers to the polygons belonging to  group number 'groupNum'. Unlike
    GroupData, fractGroups does not stay aligned to cluster group numbers. To keep from copying, deleteing, and
    re-allocating memory when groups merge together, we simply change the variable 'groupNum' to the new group
    number and leave the polygon pointer/index list as is.

    Because of this, there will be multiple FractureGroups objects with the same group number when
    fracture clusters merge together, but with differnt polygons listed. To get all the
    polygons from a group we must search the fractGroups array for all matching groups and look at each of their
    polgon lists.

*/
struct FractureGroups {
    /*! Fracture cluster group number. */
    unsigned long long int groupNum;
    /*! List of polygon indices in the 'acceptedPoly' array in main() which belong to this group. */
    std::vector<unsigned int> polyList;
    FractureGroups();
};



/**************************************************************************************/
/**************************************************************************************/
// GroupData works in conjunction with 'FractureGroups'
// GroupData keeps track of which group numbers ('groupNum' in above struct)
// Connect to which boundaries. When a cluster of fractures bridges two
// groups/clusters, One of the groups 'valid' bool is set to 0 (not valid).
// The fractures whos valid bool becomes 0 are moved to the other group
// In the 'GroupData' structure array, FractureGroups.groupNum-1 is the index
// to the corresponding GroupData struct in the GroupData array.
struct GroupData {
    /*! Number of polygons in group. */
    unsigned int size;
    /*! Valid bit, True if group this structures data is still valid, false otherwise.
        Data can become invalid when fracture cluster groups merge together. */
    bool valid;
    /*! Domain boundary sides/faces that this cluster connects to..
        Index Key:
        [0]: -x face, [1]: +x face
        [2]: -y face, [3]: +y face
        [4]: -z face, [5]: +z face */
    bool faces[6];
    
    // Constructor sets size to zero an sets 'valid' bit and 'faces' elements
    //    to false.
    GroupData();
};



/**************************************************************************************/
/**************************************************************************************/
/*! Rejection reason counters. */
struct RejectionReasons {
    /*! Rejections due to intersection of length less than h.*/
    unsigned long long int shortIntersection;
    /*! Rejections due to intersections being too close to close to
        polygon verties. */
    unsigned long long int closeToNode;
    /*! Rejections due to intersections being too close to polygon
        edges. */
    unsigned long long int closeToEdge;
    /* Counter no longer in use. */
    unsigned long long int closePointToEdge;
    /*! Rejections due to fractures landing outside of the domain.*/
    unsigned long long int outside;
    /*! Rejections due to triple intersection problem. */
    unsigned long long int triple;
    /*! Rejections due to an intersection landing too close to another
        intersection.*/
    unsigned long long int interCloseToInter;
    RejectionReasons();
};


/**************************************************************************************/
/**************************************************************************************/
// TODO: Make singleton
/*! Program and DFN statisistics structure. Keeps various statistics, including
    fracture cluster information, about the DFN being generated. */
struct Stats {

    /*! Counters for the number of polygons/fractures accepted by each stochastic
        family. Elements in this array are in the same order as the stochastic shape
        families array 'shapeFamilies' in main(). e.g. The counter for the second family
        in the shapeFamilies array is the second element in this array. */
    int *acceptedFromFam;
    
    /*! Counters for the number of polygons/fractures rejected by each stochastic
        family. Elements in this array are in the same order as the stochastic shape
        families array 'shapeFamilies' in main(). e.g. The counter for the second family
        in the shapeFamilies array is the second element in this array. */
    int *rejectedFromFam;
    
    /*! Number of fractures estimated for each stochastic family (see dryRun()).
        Elements in this array are in the same order as the stochastic shape
        families array 'shapeFamilies' in main(). e.g. The estimated number of
        fractures for the second family in the shapeFamilies array is the second
        element in this array. */
    int *expectedFromFam;
    
    /*! Total number of accepted polygons/fractures for the DFN. This variable is
        updated as the DFN is generated. */
    unsigned int acceptedPolyCount;
    
    /*! Total number of rejected polygons/fractures for the DFN. This variable is
        updated as the DFN is generated. */
    unsigned long long int rejectedPolyCount;
    
    /*! Total number of polygon/fracture re-translations. This variable is updated
        as the DFN is generated. */
    unsigned int retranslatedPolyCount;
    
    /*! Total number of fractures that have been truncated against the domain. */
    unsigned int truncated;
    
    /*! Total number of intersection points. This variable is used as a
        counter in writeIntersections() when generating output files. It is used
        to determine the number of nodes lagrit will see as duplicates and remove. */
//   unsigned int numIntPoints;

    /*! Total area of fractures before isolated fracture removal. Variable is set in main() after
        DFN generation has completed. */
    double areaBeforeRemoval;
    
    /*! Total area of fractures after isolated fracture removal. Variable is set in main() after
       DFN generation has completed. */
    double areaAfterRemoval;
    
    /*! Total volume of fractures before isolated fracture removal. Variable is set in
        main() after DFN generation has completed. */
    double volBeforeRemoval;
    
    /*! Total volume of fractures after isolated fracture removal. Variable is set in
        main() after DFN generation has completed. */
    double volAfterRemoval;
    
    /*!  Used to assign group/cluster numbers. 'nextGroupNum initializes to 1, and is used to
        assign a fracture a group number, and is then incremented. */
    unsigned long long int nextGroupNum;
    
    /*! RejectionReasons structure holds counters for all rejection reasons.*/
    struct RejectionReasons rejectionReasons;
    
    /*! Counter for number of intersections that have been shortened by FRAM's
        shrinkIntersection() function. Only counts intersections of fractures that have been
        accepted into the domain. */
    unsigned int intersectionsShortened;
    
    /*! Total length of original intersections in the DFN before intersections were shortened.*/
    double originalLength; // Length of all intersections if none were shortened
    
    /*! Total length of intersections in DFN which were discarded by shrinkIntersection()
        inside FRAM.
        Final intersection length = originalLength - discardedLength  */
    double discardedLength;
    
    /*! Total number of intersection points in DFN after isolated fracture removal.
        This variable is used as a counter in writeIntersections() when generating
        output files. It is used to determine the number of nodes lagrit will see
        as duplicates and remove. Used in error checking. */
    unsigned int intersectionNodeCount;
    
    /*! Total number of triple intersection points in DFN after isolated fracture removal.
       This variable is used as a counter in writeIntersections() when generating
       output files. It is used to determine the number of nodes lagrit will see
       as duplicates and remove. Used in error checking. */
    unsigned int tripleNodeCount;
    
    /*! Rejects per insertion attempt counter. Each element represents the number of tries
        it took to fit a fracture into the DFN. e.g. The number stored in the 10th element
        is the number of tries it took before the 10th fracture was accepted. This count
        inclues re-translating the same fracture to different locations as well as generating
        new fractures.  */
    std::vector<unsigned int> rejectsPerAttempt;
    
    /*! Fracture cluster data. See struct FractureGroup. */
    std::vector<struct FractureGroups> fractGroup;
    /*! Fracture cluster data. See struct GroupData. */
    std::vector<struct GroupData> groupData;
    // Constructor
    Stats();
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Shape is used to hold varibales for all types of stochastic shapes. During getInput(),
    all stochastic families for both recaangles and ellipses are parsed from the user input
    and are placed in a Shape structure array.
*/
struct Shape {

    /*! 0 = ellipse, 1 = rectangle */
    short shapeFamily;
    
    /*! 1: Lognormal, 2: truncated power-law, 3: exponential, 4: constant */
    short distributionType;
    
    /*! Number of vertices used to create the polygon. Ellipse families only.*/
    short numPoints;
    
    /*! Array of thetas to build poly from, initialized while reading input and building shape structures */
    float *thetaList;
    
    /*! Current index to the radii list 'radiiList'.  */
    unsigned int radiiIdx;
    
    /*! Initial list of fracture/polygon radii, sorted largest to smallest. */
    std::vector<double> radiiList;
    
    /*! Layer the family belongs to. 0 is entire domain, greater than 0 is a layer.
        e.g. 2 would be the second layer listed in the input file under "layers:".  */
    short layer;
    
    /*! Region the family belongs to. 0 is entire domain, greater than 0 is a region.
        e.g. 2 would be the second region listed in the input file under "regions:".  */
    short region;
    
    /*! Aspect ratio for family. */
    float aspectRatio;
    
    /*! Target p32 (fracture intensity) for the family when using p32 program-stopping option. */
    float p32Target;
    
    /*! Current P32 value for this family.  */
    float currentP32;
    
    /*! True = degrees, False = radians. This variable is set while readin the user's input file.
        After reading in the users input file, any input in degrees
        will be  changed to radians. */
    bool angleOption;
    
    /*! 'betaOption' is the rotation about the polygon's  normal vector
        True - User Specified Rotation
        False - Uniform Distribution */
    bool betaDistribution;
    
    /*! 'beta' is the rotation, or twist, around z normal before 3d rotation in radians
        or degrees depending on 'angleOption'. */
    float beta;
    
    /*!   If orientationOption = 0 (Spherical coordinates)
        This is the angle the normal vector makes with the z-axis (theta)
        If  orientationOption = 1
        This is the trend of Rectangle fracture orientation.
        */
    double angleOne;
    
    /*! If orientationOption = 0 (Spherical coordinates)
        This is the angle the normal vector makes with the z-axis (phi)
        If  orientationOption = 1
        This is the trend of Rectangle fracture orientation. */
    double angleTwo;
    
    /*! Parameter for fisher distributions. The
        bigger, the more similar (less diverging) are the
        rectangular familiy's normal vectors. */
    double kappa;
    
    
    /**************** Distribution Variables *********************/
    /*************************************************************/
    /*! Value between 0 and 1. Input to distrubution which will generate the user's defined
        minimum value from the distribution. Currently used only for exponential
        distrubution in the Distributions class. Value is set during Distributions
        constructor. */
    double minDistInput;
    
    /*! Value between 0 and 1. Input to distrubution which will generate the user's defined
        maximum value from the distribution. Currently used only for exponential
        distrubution in the Distributions class. Value is set during Distributions
        constructor. */
    double maxDistInput;
    
    /*! Exponential distribution option. Mean value for exponential distribution. */
    float expMean;
    
    /*! Exponential distribution option. Lambda value for exponential distibution. This
        value is set by using 1/'expMean' while reading the user's input file. */
    float expLambda;
    
    /*! Exponential distribution option. User's chosen minimum value for the distribution.
        The distribution will never return a value smaller than this. */
    float expMin;
    
    /*! Exponential distribution option. User's chosen minimum value for the distribution.
        The distribution will never return a value larger than this. */
    float expMax;
    
    /*! Log-normal distribution option. Mean of underlying normal distribution from which
        the log-normal distribution is created. */
    float mean;
    
    /*! Log-normal distribution option. Standard deviation of the underlying
        normal distribution from which the log-normal distribution is created.  */
    float sd;
    
    /*! Log-normal distribution option. User's chosen minimum value for the distribution.
        The distribution will never return a value smaller than this. */
    float logMin;
    /*! Log-normal distribution option. User's chosen maximum value for the distribution.
        The distribution will never return a value smaller than this. */
    float logMax;
    
    /*! Constant distribution. Constant radii size for all fractures in the family.  */
    float constRadi;
    
    /*! Truncated power-law option. Minimum radius for power-law distribution. */
    float min;
    
    /*! Truncated power-law option. Maximum radius for power-law distribution. */
    float max;
    
    /*! Alpha. Used in truncated power-law distribution calculations. */
    float alpha;
    
    Shape(); // Constructor
};

void printPolyData(struct Poly &Poly);
void printStats(struct stats *obj);

#endif


