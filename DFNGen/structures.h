/*!
    \file polyStruct.h
    \brief Contains definitions of data structures for polygons, points, intersections, and related statistics in DFNGen.
*/

#ifndef _polyStruct_h_
#define _polyStruct_h_

#include <vector>
#include <cmath>
#include <string>


/**************************************************************************************/
/**************************************************************************************/
/*!
    The Poly structure is used to create and store fractures/polygons.
*/
struct Poly {
    /*! Number of nodes/vertices in the polygon. */
    int numberOfNodes;
    
    /*! Contains the index of the 'shapeFamilies' array in main() from which the fracture was
        created. If the polygon was created from user defined input, it will be marked
        (-2 for user-rect, and -1 for user-ell).
        The stochastic shape family numbers start at 0 for the first family, and increase by
        1 for each additional family. Families are in the same order in which they are defined in the
        'famProb' variable in the input file, starting with ellipse families, then rectangular families. */
    int familyNum;
    
    /*! Fracture cluster number which the fracture belongs to. This variable is used to keep
        track of fracture connectivity. When a fracture first intersects another fracture,
        it inherits its cluster group number (groupNum). If a fracture does not intersect
        any other fractures, it is given a new and unique cluster group number. When a
        fracture bridges two different clusters, all clusters are merged to have the
        cluster group number of the first intersecting fracture. */
    unsigned int groupNum;
    
    /*! Polygon area (Not calculated until after DFN generation has completed). */
    float area;
    
    /*! X-radius before fracture-domain truncation. In the case of rectangles, radius is
        1/2 the width of the polygon. */
    double xradius;
    
    /*! Y-radius before fracture-domain truncation. In the case of rectangles, radius is
        1/2 the height of the polygon. */
    double yradius;
    
    /*! Aspect ratio of polygon before fracture-domain truncation. Must be value greater than zero. */
    float aspectRatio;
    
    /*! Translation of polygon. This variable is set while building the polygon. */
    double translation[3];
    
    /*! Polygon normal. This variable is set while building the polygon. */
    double normal[3];
    
    /*! The bounding box of the polygon. Set with createBoundingBox().
        Index Key:
        [0]: x minimum, [1]: x maximum
        [2]: y minimum, [3]: y maximum
        [4]: z minimum, [5]: z maximum */
    double boundingBox[6];
    
    /*! Double array which holds the polygon's vertices. Vertices are stored in a 1-D array.
        For n number of vertices, array will be: {x1, y1, z1, x2, y2, z2, ... , xn, yn, zn} */
    double *vertices;
    
    /*! The faces array contains flags which denote which sides, if any, the polygon is touching.
        True  - Polygon is touching a domain boundary.
        False - Polygon is not touching a domain boundary.
        Index Key:
        [0]: -x face, [1]: +x face
        [2]: -y face, [3]: +y face
        [4]: -z face, [5]: +z face */
    bool faces[6];
    
    /*! Used to prevent multiple rotations to the XY plane. */
    bool XYPlane;
    
    /*! True if the polygon has been truncated, false otherwise. */
    bool truncated;
    
    /*! List of indices to the permanent intersection array ('intPts' in main()) which belong to this polygon. */
    std::vector<unsigned int> intersectionIndex;
    
    /*! Constructor. */
    Poly();
};



/**************************************************************************************/
/**************************************************************************************/
/*! 
    Structure for 3D points/vertices. Constructor is overloaded for either creating
    a point with uninitialized variables, or variables x, y, and z during object
    creation.
*/
struct Point {
    double x;
    double y;
    double z;
    
    Point();
    Point(double _x, double _y, double _z);
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Holds rejection information for user-defined fractures.
*/
struct RejectedUserFracture {
    int id;                 /*!< Fracture identifier. */
    int userFractureType;   /*!< Type code of user-defined fracture. */
    RejectedUserFracture();
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Intersections structure.
    Contains all data pertaining to one intersection, including the IDs of both
    intersecting fractures, the intersection end points, any triple intersection
    points on the intersection, and a flag indicating whether the intersection
    has been shortened by shrinkIntersection().
*/
struct IntPoints {
    long int fract1;        /*!< ID of first intersecting fracture. */
    long int fract2;        /*!< ID of second intersecting fracture. */
    double x1, y1, z1;      /*!< Coordinates of intersection endpoint 1. */
    double x2, y2, z2;      /*!< Coordinates of intersection endpoint 2. */
    std::vector<unsigned int> triplePointsIdx; /*!< Indices of triple intersection points. */
    bool intersectionShortened; /*!< True if intersection was shortened. */

    IntPoints(); /*!< Constructor. Initializes fract1 and fract2 to -1. */
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Holds temporary triple point data while FRAM checks intersections for a new polygon.
*/
struct TriplePtTempData {
    Point triplePoint;                  /*!< The candidate triple intersection point. */
    std::vector<int> intIndex;          /*!< Indices into permanent intersection array if accepted. */
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    FractureGroups holds lists of polygons for each cluster group number.
*/
struct FractureGroups {
    unsigned long long int groupNum;            /*!< Cluster group number. */
    std::vector<unsigned int> polyList;         /*!< Indices of polygons in this group. */
    FractureGroups();
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    GroupData tracks validity and boundary connections of fracture clusters.
*/
struct GroupData {
    unsigned int size;         /*!< Number of polygons in the group. */
    bool valid;                /*!< True if this group's data remains valid. */
    bool faces[6];             /*!< Boundary faces connected by this cluster. */
    GroupData();               /*!< Constructor sets defaults. */
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Rejection reason counters for DFN generation.
*/
struct RejectionReasons {
    unsigned long long int shortIntersection;   /*!< Too-short intersection. */
    unsigned long long int closeToNode;         /*!< Intersection too close to a node. */
    unsigned long long int closeToEdge;         /*!< Intersection too close to an edge. */
    unsigned long long int closePointToEdge;    /*!< (Unused) */
    unsigned long long int outside;             /*!< Fracture landing outside domain. */
    unsigned long long int triple;              /*!< Triple intersection error. */
    unsigned long long int interCloseToInter;   /*!< Intersection too close to another. */
    RejectionReasons();                          /*!< Constructor initializes counters. */
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Program and DFN statistics collected during generation.
*/
struct Stats {
    int *acceptedFromFam;     /*!< Accepted count per stochastic family. */
    int *rejectedFromFam;     /*!< Rejected count per stochastic family. */
    int *expectedFromFam;     /*!< Estimated count per stochastic family. */
    unsigned int acceptedPolyCount;          /*!< Total accepted fractures. */
    unsigned long long int rejectedPolyCount;/*!< Total rejected fractures. */
    unsigned int retranslatedPolyCount;      /*!< Number of re-translations performed. */
    unsigned int truncated;                  /*!< Number of truncated fractures. */
    double areaBeforeRemoval;                /*!< Total area before isolation removal. */
    double areaAfterRemoval;                 /*!< Total area after isolation removal. */
    double volBeforeRemoval;                 /*!< Total volume before isolation removal. */
    double volAfterRemoval;                  /*!< Total volume after isolation removal. */
    unsigned long long int nextGroupNum;     /*!< Next available cluster group number. */
    RejectionReasons rejectionReasons;       /*!< Counters for rejection reasons. */
    unsigned int intersectionsShortened;     /*!< Count of shortened intersections. */
    double originalLength;                   /*!< Original total intersection length. */
    double discardedLength;                  /*!< Discarded intersection length. */
    unsigned int intersectionNodeCount;      /*!< Node count after isolation removal. */
    unsigned int tripleNodeCount;            /*!< Triple node count after isolation removal. */
    std::vector<unsigned int> rejectsPerAttempt; /*!< Attempts per fracture acceptance. */
    std::vector<FractureGroups> fractGroup;      /*!< Cluster group listings. */
    std::vector<GroupData> groupData;            /*!< Group data for clusters. */
    std::vector<RejectedUserFracture> rejectedUserFracture; /*!< User rejections. */
    Stats(); /*!< Constructor initializes all fields. */
};



/**************************************************************************************/
/**************************************************************************************/
/*!
    Shape holds parameters for stochastic fracture families (ellipses and rectangles).
*/
struct Shape {
    short shapeFamily;        /*!< 0 = ellipse, 1 = rectangle. */
    short distributionType;   /*!< 1=Lognormal, 2=Power-law, 3=Exponential, 4=Constant. */
    short numPoints;          /*!< Number of vertices (ellipse families only). */
    float *thetaList;         /*!< Array of angle positions for ellipse vertices. */
    unsigned int radiiIdx;    /*!< Current index into radiiList. */
    std::vector<double> radiiList; /*!< Pre-generated radii. */
    short layer;              /*!< Layer index (0 = whole domain). */
    short region;             /*!< Region index (0 = whole domain). */
    float aspectRatio;        /*!< Aspect ratio for shapes. */
    float p32Target;          /*!< P32 target for stopping condition. */
    float currentP32;         /*!< Current P32 value. */
    bool angleOption;         /*!< True = degrees, False = radians. */
    bool betaDistribution;    /*!< True = constant beta, False = uniform. */
    float beta;               /*!< Rotation about normal vector. */
    double angleOne;          /*!< First orientation angle (theta/trend/dip). */
    double angleTwo;          /*!< Second orientation angle (phi/plunge/strike). */
    std::string orientation_distribution; /*!< "fisher" or "bingham". */
    double kappa;             /*!< Fisher distribution concentration. */
    double kappa2;            /*!< Bingham distribution second concentration. */

    /* Exponential distribution parameters */
    double minDistInput;      
    double maxDistInput;      
    float expMean;            
    float expLambda;          
    float expMin;             
    float expMax;             

    /* Log-normal distribution parameters */
    float mean;               
    float sd;                 
    float logMin;             
    float logMax;             

    /* Constant distribution parameter */
    float constRadi;          

    /* Truncated power-law parameters */
    float min;                
    float max;                
    float alpha;              

    Shape(); /*!< Constructor initializes defaults. */
};

/*!
  \brief Prints the data of a Poly object for debugging.
  \param poly Reference to the Poly object to print.
*/
void printPolyData(struct Poly &poly);

/*!
  \brief Prints the contents of a Stats object for debugging.
  \param obj Pointer to the Stats object to print.
*/
void printStats(struct Stats *obj);

#endif // _polyStruct_h_