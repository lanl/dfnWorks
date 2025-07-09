/**
 * \file input.cpp
 * \brief Reads and stores DFN generation input parameters.
 *
 * This file declares and defines global configuration variables for DFNGen,
 * and provides the getInput function to read user-specified parameters
 * from an input file, initializing stochastic fracture families accordingly.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <math.h>
#include <cstdlib>
#include <string>
#include "input.h"
#include "readInputFunctions.h"
#include "generatingPoints.h"
#include "structures.h"
#include "logFile.h"

using std::cout;
using std::endl;
using std::string;

/*! DFN generation stop condition. 0 - nPoly option, 1 - P32 option.*/
short stopCondition;

/*! Number of polygons to place in the DFN when uisng nPoly stopCondition option.*/
unsigned int nPoly;

/*! Domain size with dimension x*y*z for DFN, centered at the origin. */
double domainSize[3];

/*! Minimum feature size, FRAM parameter.*/
double h;

/*! Percent to increase the size of the pre-generated radii lists, per family.
    Example: 0.2 will increase the size of the list by %20. See example input files
    for more details. */
float radiiListIncrease;

/*! This option disables the FRAM algorithm. There will be no
   fracture rejections or fine mesh. Defaults visualizationMode to 1*/
bool disableFram;

/*! Used during meshing:
        0 - Creates a fine mesh, according to h parameter;
        1 - Produce only first round of triangulations. In this case no
            modeling of flow and transport is possible.*/
bool visualizationMode;

/*! This option uses a relaxed version of the FRAM algorithm. The mesh may not
be perfectly conforming*/
bool rFram;

/*! Accept or reject triple intersections
        False - Off (Reject)
        True  - On  (Accept)*/
bool tripleIntersections;

/*! DFN will only keep clusters with connections to
    domain boundaries which are set to 1:

    boundaryFaces[0] = +X domain boundary
    boundaryFaces[1] = -X domain boundary
    boundaryFaces[2] = +Y domain boundary
    boundaryFaces[3] = -Y domain boundary
    boundaryFaces[4] = +Z domain boundary
    boundaryFaces[5] = -Z domain boundary*/
bool boundaryFaces[6];

/*! 0 - Keep any clusters which connects the specified
        boundary faces in boundaryFaces option below
    1 - Keep only the largest cluster which connects
        the specified boundary faces in boundaryFaces option below.

    If ignoreBoundaryFaces is also set to 1, DFNGen will keep the largest
    cluster which connects at least any two sides of the domain.*/
bool keepOnlyLargestCluster;

/*! 0 - remove isolated fractures and clusters
    1 - Keep isolated fractures and clusters
    */
bool keepIsolatedFractures;

/*! Useful for debugging,
    This option will print all fracture rejection reasons as they occur.
        0 - Disable
        1 - Print all rejection reasons to screen */
bool printRejectReasons;

/*! Outputs radii files after isolated fracture removal.
    One file per family.
        0: Do not create output files of radii per family
        1: Creates output files per family, containing a list
           of the family's fracture radii that is in the final DFN*/
bool outputFinalRadiiPerFamily;

/*! Outputs radii files before isolated fracture removal.
    One file per family.
        0: Do not create output files of radii per family
        1: Creates output files per family, containing a list
           of the family's fracture radii in the domain before isolated
           fracture removal.*/
bool outputAcceptedRadiiPerFamily;

/*! Only output select files for ECPM upscaling
        0: Output all files
        1: Only output files required for ECPM upscaling.
        polygon.dat, radii_final.dat */
bool ecpmOutput = false;

/*! Beta is the rotation around the polygon's normal vector
        0 - Uniform distribution [0, 2PI)
        1 - Constant angle (specefied below by 'ebeta')*/
bool *ebetaDistribution;

/*! Beta is the rotation around the polygon's normal vector
        0: Uniform distribution [0, 2PI)
        1: Constant angle (specefied below by 'rbeta')*/
bool *rbetaDistribution;

/*! False - User ellipses will be inserted first
    True  - User rectangles will be inserted first*/
bool insertUserRectanglesFirst;

/*! Inserts the largest possible fracture for each defined fracture family,
    defined by the user-defined maxium radius
        0 - Off (Do not force insertion of larest fractures)
        1 - On  (Force insertion of largest fractures)*/
bool forceLargeFractures;

/*! Seed for random generator.*/
unsigned int seed;

/*! Size increase for inserting fracture centers outside the domain.
    Fracture will be truncated based on domainSize above.
    Increases the entire width by this ammount. So, {1,1,1} will increase
    the domain by adding .5 to the +x, and subbtracting .5 to the -x, etc*/
float domainSizeIncrease[3];

/*! Selection of orientation Option
    0 - spherical coordinates
    1 - trend / plunge
    2 - dip / strike .*/
int orientationOption;

/*! Number of rectangular families defined below.
    Having this option = 0 will ignore all rectangular family variables.*/
int nFamRect;

/*! Number of ellipse families defined below.
    Having this option = 0 will ignore all rectangle family variables.*/
int nFamEll;

/*! Each element is the probability of chosing a fracture from
    the element's corresponding family to be inserted into the DFN.

    The famProb elements should add up to 1.0 (for %100).
    The probabilities are listed in order of families starting with all
    stochastic ellipses, and then all stochastic rectangles.

    For example:
    If  then there are two ellipse families, each with probabiliy .3,
    and two rectangle families, each with probabiliy .2, famProb will be:
    famProb: {.3,.3,.2,.2}, famProb elements must add to 1*/
float *famProb;

/*! Holds a copy of famProb. famProb elements can change as different families
    hit their P32 requirement when using the P32 stopCondition option.*/
float *famProbOriginal;

/*! Mandatory parameter if using statistically generated ellipses.
    Statistical distribution options:

    Holds number of elements equal to the number of shape families.

        1 - Log-normal distribution
        2 - Truncated power law distribution
        3 - Exponential distribution
        4 - Constant*/
int *edistr;

/*! Aspect ratio array for stochastic ellipses.*/
float *easpect;

/*! Number of vertices used in creating each elliptical
    fracture family. Number of elements must match number
    of ellipse families

    Holds number of elements equal to the number of ellipse families. */
unsigned int *enumPoints;

/*! All angles for ellipses are in:
        0 - degrees
        1 - radians (Must use numerical value for PI)*/
bool  eAngleOption;

/*! First Ellipse fracture orientation.
    If orientationOption = 0 (Spherical coordinates)
    This The angle the normal vector makes with the z-axis
    If  orientationOption = 1
    This is the trend of Ellipse fracture orientation.
    If  orientationOption = 2
    This is the mean dip of Ellipse fracture orientation.
    */
float *eAngleOne;

/*! Second Ellipse fracture orientation.
    If orientationOption = 0 (Spherical coordinates)
    The angle the projection of the normal
    onto the x-y plane makes with the x-axis
    If  orientationOption = 1
    This is the plunge of Ellipse fracture orientation.
    If  orientationOption = 2
    This is the mean strike of Ellipse fracture orientation.*/
float *eAngleTwo;

/*! Rotation around the fractures' normal vector.
    Ellipse family parameter.*/
float *ebeta;

/*! Parameter for the fisher distribnShaprutions. The
    bigger, the more similar (less diverging) are the
    elliptical familiy's normal vectors.*/
float *ekappa;
/*! Parameter for the bingham distribnShaprutions. The
    bigger, the more similar (less diverging) are the
    elliptical familiy's normal vectors.*/
float *ekappa2;

/*! Log-normal ellipse parameter. Mean of the underlying normal distribution.*/
float *eLogMean;

/*! Log-normal ellipse parameter. Standard deviation of the underlying normal distribution*/
float *esd;

/*! Exponential ellipse parameter. Mean values for exponential distributions, defined per family.*/
float *eExpMean;

/*! Log-normal rectangle parameter. Minimum radius.*/
float *rLogMin;

/*! Log-normal rectangle parameter. Maximum radius.*/
float *rLogMax;

/*! Exponential rectangle parameter. Minimum radius.*/
float *rExpMin;

/*! Exponential rectangle parameter. Maximum radius.*/
float *rExpMax;

/*! Log-normal ellipse parameter. Minimum radius.*/
float *eLogMin;

/*! Log-normal ellipse parameter. Maximum radius.*/
float *eLogMax;

/*! Exponential ellipse parameter. Minimum radius.*/
float *eExpMin;

/*! Exponential ellipse parameter. Maximum radius.*/
float *eExpMax;

/*! Contant ellipse parameter. Constant radius.*/
float *econst;

/*! Truncated power-law ellipse parameter. Minimum radius.*/
float *emin;

/*! Truncated power-law ellipse parameter. Maximum radius.*/
float *emax;

/*! Truncated power-law ellipse distribution parameter.*/
float *ealpha;

/*! Elliptical families target fracture intensities per family
    when using stopCondition = 1, P32 option.*/
float *e_p32Targets;

/*! Mandatory parameter if using statistically generated rectangles.

    Holds number of elements equal to the number of shape families.\

    Rectangle statistical distribution options:
        1 - log-normal distribution
        2 - truncated power law distribution
        3 - exponential distribution
        4 - constant*/
unsigned int *rdistr;

/*! Aspect ratio for stochasic rectangles.*/
float *raspect;

/*! All angles from input file for stochastic rectangles are in:
        True  - Degrees
        False - Radians */
bool rAngleOption;

/*! 0 - Ignore this option, keep all fractures.

   >0 - Size of minimum fracture radius. Fractures smaller than
        defined radius will be removed AFTER DFN generation.

        Minimum and maximum size options under fracture family
        distributions will still be used while generating the DFN.*/
float removeFracturesLessThan;

/*! First Rectangle fracture orientation.
    If orientationOption = 0 (Spherical coordinates)
    This The angle the normal vector makes with the z-axis
    If orientationOption = 1
    This is the trend of Rectangle fracture orientation.
    If orientationOption = 2
    This is the mean dip of Rectangle fracture orientation.
    */
float *rAngleOne;

/*! Second Rectangle fracture orientation.
    If orientationOption = 0 (Spherical coordinates)
    The angle the projection of the normal
    onto the x-y plane makes with the x-axis
    If  orientationOption = 1
    This is the plunge of Rectangle fracture orientation.
    If  orientationOption = 2
    This is the mean strike of Rectangle fracture orientation. */
float *rAngleTwo;

/*! Rotation around the normal vector.*/
float *rbeta;

/*! Parameter for the fisher distribnShaprutions. The
    bigger, the more similar (less diverging) are the
    rectangle family's normal vectors.*/
float *rkappa;

/*! Parameter for the bingham distribnShaprutions. The
    bigger, the more similar (less diverging) are the
    rectangle family's normal vectors.*/
float *rkappa2;

/*! Log-normal rectangle parameter. Standard deviation of the underlying normal distribution*/
float *rLogMean;

/*! Log-normal rectangle parameter. Standard deviation of the underlying normal distribution*/
float *rsd;

/*! Truncated power-law rectangle parameter. Minimum radius.*/
float *rmin;

/*! Truncated power-law rectangle parameter. Maximum radius.*/
float *rmax;

/*! Truncated power-law rectangle distribution parameter.*/
float *ralpha;

/*! Rectangular families target fracture intensities per family
    when using stopCondition = 1, P32 option.*/
float *r_p32Targets;

/*! Exponential rectangle parameter. Maximum radius.*/
float *rExpMean;

/*! Constant rectangle parameter. Constant radius.*/
float *rconst;

/*! True  - The user is using user defined ellipses.
    False - No user defined ellipses are being used. */
bool userEllipsesOnOff;

/*! Number of defined, user defined ellipses.*/
int nUserEll;

/*! All angles from input file for stochastic ellipses are in:
        True  - Degrees
        False - Radians */
bool ueAngleOption;

/*! User ellipses radii array. */
float *ueRadii;

/*! User ellipses beta array. */
float *ueBeta;

/*! User ellipses aspect ratio array. */
float *ueaspect;

/*! User ellipses translation array.*/
double *uetranslation;

/*! User Orientation Option for ellipses
    0 = normal vector
    1 = trend / plunge
    2 = dip / strike
*/
int userEllOrientationOption;

/*! User ellipses normal vector array. */
double *uenormal;

/*! User ellipses trend and plunge array.*/
double *ueTrendPlunge;

/*! User ellipses dip and strike array.*/
double *ueDipStrike;

/*! User ellipses number of points per ellipse array. */
unsigned int *uenumPoints;

/*! True  - The user is using user defined rectangles.
    False - No user defined rectangles are being used. */
bool userRectanglesOnOff;

/*! True  - User rectangles defined by coordinates are being used.
    False - No rectangles defined by coordinates are being used.*/
bool userRecByCoord;

/*! True  - User ellipses defined by coordinates are being used.
    False - No ellpsies defined by coordinates are being used.*/
bool userEllByCoord;

/*! True  - User polygons defined by coordinates are being used.
    False - No polygons defined by coordinates are being used.*/
bool userPolygonByCoord;

/*! Caution: Can create very large files.
    Outputs all fractures which were generated during
    DFN generation (Accepted + Rejected).
        False: Do not output all radii file.
        True:  Include file of all raddii, acepted + rejected fractures,
               in output files (radii_All.dat). */
bool outputAllRadii;

/*! Number of user defined rectangles.*/
int nUserRect;

/*! User rectangles radii array.*/
float *urRadii;

/*! All angles from input file for stochastic rectangles are in:
        True  - Degrees
        False - Radians */
bool urAngleOption;

/*! User rectangles beta array.*/
float *urBeta;

/*! User rectangles aspect ratio array.*/
float *uraspect;

/*! User rectangles translation array. */
double *urtranslation;

/*! User Orientation Option for rectangles
    0 = normal vector
    1 = trend / plunge
    2 = dip / strike
    */
int userRectOrientationOption;

/*! User rectangles normal vector array.*/
double *urnormal;

/*! User rectangles trend and plunge array.*/
double *urTrendPlunge;

/*! User rectangles dip and strike array.*/
double *urDipStrike;

/*! Number of user rectangles defined by coordinates.*/
unsigned int nRectByCoord;

/*! Number of user ellipses defined by coordinates.*/
unsigned int nEllByCoord;

/*! Number of nodes for user defined ellipses by coordinates */
unsigned int nEllNodes;

/*! Array of rectangle coordiates.
    Number of elements = 4 * 3 * nRectByCoord*/
double *userRectCoordVertices;

/*! Array of ellipse coordiates.
    Number of elements =  3 * nEllNodes * nEllByCoord*/
double *userEllCoordVertices;

/*! Name of userPolygon File */
std::string polygonFile;

/*! Log-normal aperture option.
    Mean of underlying normal distribution. */
// float meanAperture;

/*! Log-normal aperture option.
    Standard deviation of underlying normal distribution. */
// float stdAperture;

/*! 1 - Log-normal distribution
    2 - Aperture from transmissivity, first transmissivity is defined,
        and then, using a cubic law, the aperture is calculated.
    3 - Constant aperture (same aperture for all fractures)
    4 - Length Correlated Aperture
        Apertures are defined as a function of fracture size.*/
//int aperture;

/*! Transmissivity is calculated as transmissivity = F*R^k,
    where F is a first element in aperturefromTransmissivity,
    k is a second element and R is a mean radius of a polygon.
    Aperture is calculated according to cubic law as
    b = (transmissivity*12)^(1/3)*/
// float apertureFromTransmissivity[2];

/*! Sets all fracture apertures to constantAperture.*/
// double constantAperture;

/*! Length Correlated Aperture Option:
    Aperture is calculated by: b=F*R^k,
    where F is a first element in lengthCorrelatedAperture,
    k is a second element and R is a mean radius of a polygon.*/
// double lengthCorrelatedAperture[2];

/*! Permeability for all fractures*/
// double constantPermeability;

/*! If a fracture is rejected, it will be re-translated
    to a new position this number of times.

    This helps hit distribution targets for stochastic families
    families (Set to 1 to ignore this feature)*/
int rejectsPerFracture;

// Z - layers in the DFN
/*! Number of layers defined. */
int numOfLayers;

/*! Array of layers:
    e.g. {+z1, -z1, +z2, -z2, ... , +zn, -zn}*/
float *layers;

/*! Array of volumes for each defined layer, in the same order
    which layers were listed.*/
float *layerVol;

/*  Defines which domain, or layer, the family belongs to.
    Layer 0 is the entire domain ('domainSize').
    Layers numbered > 0 correspond to layers defined above (see 'Layers:').
    1 correspond to the first layer listed, 2 is the next layer listed, etc*/
int *rLayer;

/*! Defines which domain, or layer, the family belongs to.
    Layer 0 is the entire domain ('domainSize').
    Layers numbered > 0 correspond to layers defined above (see 'Layers:').
    1 correspond to the first layer listed, 2 is the next layer listed, etc*/
int *eLayer;

// Regions in the DFN

/*! Number of regions defined. */
int numOfRegions;

/*! Array of regions:
    e.g. {+z1, -z1, +z2, -z2, ... , +zn, -zn}*/
float *regions;

/*! Array of volumes for each defined layer, in the same order
    which regions were listed.*/
float *regionVol;

/*  Defines which domain, or regions, the family belongs to.
    Regions 0 is the entire domain ('domainSize').
    regions numbered > 0 correspond to regions defined above (see 'regions:').
    1 correspond to the first layer listed, 2 is the next layer listed, etc*/
int *rRegion;

/*! Defines which domain, or regions, the family belongs to.
    Layer 0 is the entire domain ('domainSize').
    regions numbered > 0 correspond to regions defined above (see 'regions:').
    1 correspond to the first layer listed, 2 is the next layer listed, etc*/
int *eRegion;

/*! flag if the domain is pruned down to a final domain size*/
bool polygonBoundaryFlag = false;

/*! Number of points on the 2D boundary of the polygon domain */
int numOfDomainVertices;

/*! Vector of points defining the 2D boundary of the domain polygon */
std::vector<Point> domainVertices;

/*! Global boolean array. Used with stopCondition = 1, P32 option.
    Number of elements is equal to the number of stochastic shape families.
    Elements correspond to families in the same order of the famProb array.
    Elements are initialized to false, and are set to true once the families p32
    requirement is met.
    Once all elements have values all set to true, all families have had their
    P32 requirement */
bool *p32Status;

/*! False - Use boundaryFaces option.
    True  - Ignore boundaryFaces option, keep all clusters
            and remove fractures with no intersections */
bool ignoreBoundaryFaces;

/******************************************************************/
/*! Reads in all input variables.
    Creates Shape structure array from user input if
    using stochastic fracture families.

    \param input Path to input file.
    \param shapeFamily OUTPUT vector to store stochastic shape families.
*/
void getInput(char* input, std::vector<Shape> &shapeFamily) {
    // ... implementation as above ...
}

/****************************************************************************************/
/*!
 * \brief Prints all input variables for debugging.
 *
 * This function logs each input parameter to the log file.
 * \note Deprecated: Needs to be updated when new input variables are added.
 */
void printInputVars() {
    std::string logString = "npoly = " + to_string(nPoly);
    logger.writeLogFile(INFO,  logString);
    logString = "tripleIntersections = " + to_string(tripleIntersections) + "\n";
    logger.writeLogFile(INFO,  logString);
    logString = "domainsize = {" + to_string(domainSize[0]) + ", " + to_string(domainSize[1]) + ", " + to_string(domainSize[2]) + "}\n";
    logger.writeLogFile(INFO,  logString);
    logString = "h = " + to_string(h);
    logger.writeLogFile(INFO,  logString);
    logString = "visualizationMode = " + to_string(visualizationMode) + "\n";
    logger.writeLogFile(INFO,  logString);
    logString = "seed = " + to_string(seed);
    logger.writeLogFile(INFO,  logString);
    logString = "keepOnlyLargestCluster = " + to_string(keepOnlyLargestCluster);
    logger.writeLogFile(INFO,  logString);
    logString = "domainSizeIncrease = {" + to_string(domainSizeIncrease[0]) + "," + to_string(domainSizeIncrease[1]) + "," + to_string(domainSizeIncrease[2]) + "}\n";
    logger.writeLogFile(INFO,  logString);
    logString = "boundaryFaces = {" + to_string(boundaryFaces[0]) + "," + to_string(boundaryFaces[1]) + "," + to_string(boundaryFaces[2]) + "," + to_string(boundaryFaces[3]) + "," + to_string(boundaryFaces[4]) + "," + to_string(boundaryFaces[5]) + "}\n";
    logger.writeLogFile(INFO,  logString);
    logString = "nFamRect = " + to_string(nFamRect) + "\n";
    logger.writeLogFile(INFO,  logString);
    logString = "nFamEll = " + to_string(nFamEll) + "\n";
    logger.writeLogFile(INFO,  logString);
    printAry(famProb, "famProb", (nFamEll + nFamRect));
    printAry(edistr, "edistr", nFamEll);
    printAry(enumPoints, "enumPoints", nFamEll);
    logString = "eAngleOption = " + to_string(eAngleOption) + "\n";
    logger.writeLogFile(INFO,  logString);
    printAry(easpect, "easpect", nFamEll);
    
    if (orientationOption == 0) {
        printAry(eAngleOne, "etheta", nFamEll);
        printAry(eAngleTwo, "ephi", nFamEll);
    } else if (orientationOption == 1) {
        printAry(eAngleOne, "etrend", nFamEll);
        printAry(eAngleTwo, "eplunge", nFamEll);
    } else if (orientationOption == 2) {
        printAry(eAngleOne, "edip", nFamEll);
        printAry(eAngleTwo, "estrike", nFamEll);
    }
    
    printAry(ebeta, "ebeta", nFamEll);
    printAry(ekappa, "ekappa", nFamEll);
    printAry(ekappa2, "ekappa2", nFamEll);
    printAry(eLogMean, "eLogMean", nFamEll);
    printAry(esd, "esd", nFamEll);
    printAry(eExpMean, "eExpMean", nFamEll);
    printAry(econst, "econst", nFamEll);
    printAry(emin, "emin", nFamEll);
    printAry(emax, "emax", nFamEll);
    printAry(ealpha, "ealpha", nFamEll);
    printAry(rdistr, "rdistr", nFamRect);
    printAry(raspect, "raspect", nFamRect);
    logString = "rAngleOption = " + to_string(rAngleOption);
    logger.writeLogFile(INFO,  logString);
    
    if (orientationOption == 0) {
        printAry(rAngleOne, "rtheta", nFamRect);
        printAry(rAngleTwo, "rphi", nFamRect);
    } else if (orientationOption == 1) {
        printAry(rAngleOne, "rtrend", nFamRect);
        printAry(rAngleTwo, "rplunge", nFamRect);
    } else if (orientationOption == 2) {
        printAry(rAngleOne, "rdip", nFamRect);
        printAry(rAngleTwo, "rstrike", nFamRect);
    }
    
    printAry(rbeta, "rbeta", nFamRect);
    printAry(rLogMean, "rLogMean", nFamRect);
    printAry(rsd, "rsd", nFamRect);
    printAry(rmin, "rmin", nFamRect);
    printAry(rmax, "rmax", nFamRect);
    printAry(ralpha, "ralpha", nFamRect);
    printAry(rkappa, "rkappa", nFamRect);
    printAry(rkappa2, "rkappa2", nFamRect);
    printAry(rExpMean, "rExpMean", nFamRect);
    printAry(rconst, "rconst", nFamRect);
    logString = "userEllipsesOnOff = " + to_string(userEllipsesOnOff);
    logger.writeLogFile(INFO,  logString);
    
    if (userEllipsesOnOff != 0) {
        logString = "nUserEll = " + to_string(nUserEll) + "\n";
        logger.writeLogFile(INFO,  logString);
        printAry(ueRadii, "ueRadii", nUserEll);
        logString = "urAngleOption = " + to_string(ueAngleOption);
        logger.writeLogFile(INFO,  logString);
        printAry(ueBeta, "ueBeta", nUserEll);
        printAry(ueaspect, "ueaspect", nUserEll);
        print2dAry(uetranslation, "uetranslation", nUserEll);
        print2dAry(uenormal, "uenormal", nUserEll);
        printAry(uenumPoints, "uenumPoints", nUserEll);
    }
    
    logString = "userRectanglesOnOff = " + to_string(userRectanglesOnOff);
    logger.writeLogFile(INFO,  logString);
    
    if (userRectanglesOnOff != 0) {
        logString = "nUserRect = " + to_string(nUserRect) + "\n";
        logger.writeLogFile(INFO,  logString);
        printAry(urRadii, "urRadii", nUserRect);
        logString = "urAngleOption = " + to_string(urAngleOption);
        logger.writeLogFile(INFO,  logString);
        printAry(urBeta, "urBeta", nUserRect);
        printAry(urRadii, "urRadii", nUserRect);
        printAry(uraspect, "uraspect", nUserRect);
        print2dAry(urtranslation, "urtranslation", nUserRect);
        print2dAry(urnormal, "urnormal", nUserRect);
    }
    
    logString = "userRecByCoord = " + to_string(userRecByCoord);
    logger.writeLogFile(INFO,  logString);
    
    if (userRecByCoord != 0) {
        logString = "nRectByCoord = " + to_string(nRectByCoord);
        logger.writeLogFile(INFO,  logString);
        printRectCoords(userRectCoordVertices, "userRectCoordVertices", nRectByCoord);
    }
}