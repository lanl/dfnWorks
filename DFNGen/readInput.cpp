#include <iostream>
#include <fstream>
#include <vector>
#include <math.h>
#include <cstdlib>
#include <string>
#include "input.h"
#include "readInputFunctions.h"
#include "generatingPoints.h"

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
bool ecpmOutput;

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
    If orientationOption = 2
    This is the mean strike of Rectangle fracture orientation. */
float *rAngleTwo;

/*! Rotation around the normal vector.*/
float *rbeta;

/*! Parameter for the fisher distribnShaprutions. The
    bigger, the more similar (less diverging) are the
    rectangle family's normal vectors.*/
float *rkappa;

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

/*! False - Permeability of each fracture is a function of fracture aperture,
            given by k=(b^2)/12, where b is an aperture and k is permeability
    True  - Constant permeabilty for all fractures*/
bool permOption;

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
float meanAperture;

/*! Log-normal aperture option.
    Standard deviation of underlying normal distribution. */
float stdAperture;

/*! 1 - Log-normal distribution
    2 - Aperture from transmissivity, first transmissivity is defined,
        and then, using a cubic law, the aperture is calculated.
    3 - Constant aperture (same aperture for all fractures)
    4 - Length Correlated Aperture
        Apertures are defined as a function of fracture size.*/
int aperture;

/*! Transmissivity is calculated as transmissivity = F*R^k,
    where F is a first element in aperturefromTransmissivity,
    k is a second element and R is a mean radius of a polygon.
    Aperture is calculated according to cubic law as
    b = (transmissivity*12)^(1/3)*/
float apertureFromTransmissivity[2];

/*! Sets all fracture apertures to constantAperture.*/
double constantAperture;

/*! Length Correlated Aperture Option:
    Aperture is calculated by: b=F*R^k,
    where F is a first element in lengthCorrelatedAperture,
    k is a second element and R is a mean radius of a polygon.*/
double lengthCorrelatedAperture[2];

/*! Permeability for all fractures*/
double constantPermeability;

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

    Arg 1: Path to input file
    Arg 2: OUTPUT, Shape array to store stochastic families*/
void getInput(char* input, std::vector<Shape> &shapeFamily) {
    std::string tempstring;
    char ch;
    std::ifstream inputFile;
    std::cout << "DFN Generator Input File: " << input << "\n\n";
    // Open input file and initialize variables
    inputFile.open(input, std::ifstream::in);
    checkIfOpen(inputFile, tempstring.c_str());
    searchVar(inputFile, "stopCondition:");
    inputFile >> stopCondition;
    searchVar(inputFile, "printRejectReasons:");
    inputFile >> printRejectReasons;
    searchVar(inputFile, "domainSize:");
    inputFile >> ch >> domainSize[0] >> ch >> domainSize[1] >> ch >> domainSize[2];
    searchVar(inputFile, "numOfLayers:");
    inputFile >> numOfLayers;
    
    if (numOfLayers > 0 ) {
        layers = new float[numOfLayers * 2]; // Multiply by 2 for +z and -z for each layer
        layerVol = new float[numOfLayers];
        searchVar(inputFile, "layers:");
        std::cout << "Number of Layers: " << numOfLayers << "\n";
        
        for (int i = 0; i < numOfLayers; i++) {
            int idx = i * 2;
            inputFile >> ch >> layers[idx] >> ch >> layers[idx + 1] >> ch;
            std::cout << "    Layer " << i + 1 << "{-z,+z}: {" << layers[idx] << "," << layers[idx + 1] << "}, Volume: ";
            layerVol[i] = domainSize[0] * domainSize[1] * (std::abs(layers[idx + 1] - layers[idx]));
            std::cout << layerVol[i] << "m^3\n";
        }
        
        std::cout << "\n";
    }
    
    searchVar(inputFile, "numOfRegions:");
    inputFile >> numOfRegions;
    
    if (numOfRegions > 0 ) {
        regions = new float[numOfRegions * 6]; // Multiply by 6 xmin, xmax, ymin, ymax, zmin, zmax
        regionVol = new float[numOfRegions];
        searchVar(inputFile, "regions:");
        std::cout << "Number of Regions: " << numOfRegions << "\n";
        
        for (int i = 0; i < numOfRegions; i++) {
            int idx = i * 6;
            inputFile >> ch >> regions[idx] >> ch >> regions[idx + 1] >> ch >> regions[idx + 2] >> ch >> regions[idx + 3] >> ch >> regions[idx + 4] >> ch >> regions[idx + 5] >> ch;
            std::cout << " Region " << i + 1 << ": {-x,+x,-y,+y,-z,+z}: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
            regionVol[i] = (std::abs(regions[idx + 1] - regions[idx])) * (std::abs(regions[idx + 3] - regions[idx + 2])) * (std::abs(regions[idx + 5] - regions[idx + 4])) ;
            std::cout << " Volume: " << regionVol[i] << "m^3\n";
        }
        
        std::cout << "\n";
    }
    
    searchVar(inputFile, "h:");
    inputFile >> h;
    searchVar(inputFile, "disableFram:");
    inputFile >> disableFram;
    
    if (disableFram == true) {
        std::cout << "\nFRAM IS DISABLED\n";
    }
    
    searchVar(inputFile, "tripleIntersections:");
    inputFile >> tripleIntersections;
    searchVar(inputFile, "forceLargeFractures:");
    inputFile >> forceLargeFractures;
    searchVar(inputFile, "visualizationMode:");
    inputFile >> visualizationMode;
    
    if (disableFram == true) {
        visualizationMode = 1;
    }
    
    searchVar(inputFile, "outputAllRadii:");
    inputFile >> outputAllRadii;
    searchVar(inputFile, "outputFinalRadiiPerFamily:");
    inputFile >> outputFinalRadiiPerFamily;
    searchVar(inputFile, "outputAcceptedRadiiPerFamily:");
    inputFile >> outputAcceptedRadiiPerFamily;
    searchVar(inputFile, "ecpmOutput:");
    inputFile >> ecpmOutput;
    searchVar(inputFile, "seed:");
    inputFile >> seed;
    searchVar(inputFile, "domainSizeIncrease:");
    inputFile >> ch >> domainSizeIncrease[0] >> ch >> domainSizeIncrease[1] >> ch >> domainSizeIncrease[2];
    searchVar(inputFile, "keepOnlyLargestCluster:");
    inputFile >> keepOnlyLargestCluster;
    searchVar(inputFile, "keepIsolatedFractures:");
    inputFile >> keepIsolatedFractures;
    searchVar(inputFile, "ignoreBoundaryFaces:");
    inputFile >> ignoreBoundaryFaces;
    searchVar(inputFile, "boundaryFaces:");
    inputFile >> ch >> boundaryFaces[0] >> ch >> boundaryFaces[1] >> ch >> boundaryFaces[2] >> ch >> boundaryFaces[3] >> ch >> boundaryFaces[4] >> ch >> boundaryFaces[5];
    searchVar(inputFile, "rejectsPerFracture:");
    inputFile >> rejectsPerFracture;
    searchVar(inputFile, "nFamRect:");
    inputFile >> nFamRect;
    searchVar(inputFile, "nFamEll:");
    inputFile >> nFamEll;
    searchVar(inputFile, "removeFracturesLessThan:");
    inputFile >> removeFracturesLessThan;
    searchVar(inputFile, "orientationOption:");
    inputFile >> orientationOption;
    
    if (orientationOption == 0) {
        std::cout << "Expecting Theta and phi for orientations\n";
    } else if  (orientationOption == 1) {
        std::cout << "Expecting Trend and Plunge for orientations\n";
    } else if (orientationOption == 2) {
        std::cout << "Expecting Dip and Strike (RHR) for orientations\n";
    }
    
    if (nFamEll > 0 || nFamRect > 0) {
        searchVar(inputFile, "famProb:");
        famProb = new float[(nFamEll + nFamRect)];
        getInputAry(inputFile, famProb, (nFamEll + nFamRect));
        searchVar(inputFile, "famProb:");
        famProbOriginal = new float[(nFamEll + nFamRect)];
        getInputAry(inputFile, famProbOriginal, (nFamEll + nFamRect));
        searchVar(inputFile, "radiiListIncrease:");
        inputFile >> radiiListIncrease;
    }
    
    if (nFamEll > 0) {
        searchVar(inputFile, "ebetaDistribution:");
        ebetaDistribution = new bool[nFamEll];
        getInputAry(inputFile, ebetaDistribution, nFamEll);
        searchVar(inputFile, "eLayer:");
        eLayer = new int[nFamEll];
        getInputAry(inputFile, eLayer, nFamEll);
        searchVar(inputFile, "eRegion:");
        eRegion = new int[nFamEll];
        getInputAry(inputFile, eRegion, nFamEll);
        searchVar(inputFile, "edistr:");
        edistr = new int[nFamEll];
        getInputAry(inputFile, edistr, nFamEll);
        searchVar(inputFile, "easpect:");
        easpect = new float[nFamEll];
        getInputAry(inputFile, easpect, nFamEll);
        searchVar(inputFile, "enumPoints:");
        enumPoints = new unsigned int[nFamEll];
        getInputAry(inputFile, enumPoints, nFamEll);
        searchVar(inputFile, "eAngleOption:");
        inputFile >> eAngleOption;
        
        if (orientationOption == 0) {
            searchVar(inputFile, "etheta:");
            eAngleOne = new float[nFamEll];
            getInputAry(inputFile, eAngleOne, nFamEll);
            searchVar(inputFile, "ephi:");
            eAngleTwo = new float[nFamEll];
            getInputAry(inputFile, eAngleTwo, nFamEll);
        } else if (orientationOption == 1) {
            searchVar(inputFile, "etrend:");
            eAngleOne = new float[nFamEll];
            getInputAry(inputFile, eAngleOne, nFamEll);
            searchVar(inputFile, "eplunge:");
            eAngleTwo = new float[nFamEll];
            getInputAry(inputFile, eAngleTwo, nFamEll);
        } else if (orientationOption == 2) {
            searchVar(inputFile, "edip:");
            eAngleOne = new float[nFamEll];
            getInputAry(inputFile, eAngleOne, nFamEll);
            searchVar(inputFile, "estrike:");
            eAngleTwo = new float[nFamEll];
            getInputAry(inputFile, eAngleTwo, nFamEll);
        }
        
        searchVar(inputFile, "ebeta:");
        ebeta = new float[nFamEll];
        getInputAry(inputFile, ebeta, nFamEll);
        searchVar(inputFile, "ekappa:");
        ekappa = new float[nFamEll];
        getInputAry(inputFile, ekappa, nFamEll);
        searchVar(inputFile, "eLogMean:");
        eLogMean = new float[nFamEll];
        getInputAry(inputFile, eLogMean, nFamEll);
        searchVar(inputFile, "esd:");
        esd = new float[nFamEll];
        getInputAry(inputFile, esd, nFamEll);
        searchVar(inputFile, "eExpMean:");
        eExpMean = new float[nFamEll];
        getInputAry(inputFile, eExpMean, nFamEll);
        searchVar(inputFile, "emin:");
        emin = new float[nFamEll];
        getInputAry(inputFile, emin, nFamEll);
        searchVar(inputFile, "emax:");
        emax = new float[nFamEll];
        getInputAry(inputFile, emax, nFamEll);
        searchVar(inputFile, "ealpha:");
        ealpha = new float[nFamEll];
        getInputAry(inputFile, ealpha, nFamEll);
        searchVar(inputFile, "econst:");
        econst = new float[nFamEll];
        getInputAry(inputFile, econst, nFamEll);
        searchVar(inputFile, "eLogMin:");
        eLogMin = new float[nFamEll];
        getInputAry(inputFile, eLogMin, nFamEll);
        searchVar(inputFile, "eLogMax:");
        eLogMax = new float[nFamEll];
        getInputAry(inputFile, eLogMax, nFamEll);
        searchVar(inputFile, "eExpMin:");
        eExpMin = new float[nFamEll];
        getInputAry(inputFile, eExpMin, nFamEll);
        searchVar(inputFile, "eExpMax:");
        eExpMax = new float[nFamEll];
        getInputAry(inputFile, eExpMax, nFamEll);
        
        if (stopCondition == 1) {
            // Get temp array for ellipse p32 targets
            // Used to simplify initialization of shape family structures below
            searchVar(inputFile, "e_p32Targets:");
            e_p32Targets = new float[nFamEll];
            getInputAry(inputFile, e_p32Targets, nFamEll);
        }
    }
    
    // Distribution counters
    int shape1 = 0; //longnormal dist counter
    int shape2 = 0; //truncated power-law dist counter
    int shape3 = 0; //exponential dist counter
    int shape4 = 0; //constant dist counter
    int betaCount = 0;
    
    // Create shape structures from data gathered above
    for (int i = 0; i < nFamEll; i++) {
        struct Shape newShapeFam;
        newShapeFam.shapeFamily = 0; // shapFam = 0 = ellipse, 1 = rect
        newShapeFam.distributionType = edistr[i];
        newShapeFam.numPoints = enumPoints[i];
        newShapeFam.aspectRatio = easpect[i];
        newShapeFam.angleOne = eAngleOne[i];
        newShapeFam.angleTwo = eAngleTwo[i];
        newShapeFam.kappa = ekappa[i];
        newShapeFam.angleOption = eAngleOption;
        newShapeFam.layer = eLayer[i];
        newShapeFam.region = eRegion[i];
        generateTheta(newShapeFam.thetaList, newShapeFam.aspectRatio, newShapeFam.numPoints);
        
        if (ebetaDistribution[i] == 1 ) { // If constant user defined beta option
            newShapeFam.betaDistribution = 1;
            newShapeFam.beta = ebeta[betaCount];
            betaCount++;
        } else {
            newShapeFam.betaDistribution = 0;
        }
        
        // dist options:1 = lognormal, 2= truncated power-law, 3= exponential, 4=constant
        switch (edistr[i]) {
        case 1: // Lognormal
            newShapeFam.mean = eLogMean[shape1];
            newShapeFam.sd = esd[shape1];
            newShapeFam.logMin = eLogMin[shape1];
            newShapeFam.logMax = eLogMax[shape1];
            shape1++;
            break;
            
        case 2: // Truncated power-law
            newShapeFam.min = emin[shape2];
            newShapeFam.max = emax[shape2];
            newShapeFam.alpha = ealpha[shape2];
            shape2++;
            break;
            
        case 3:
            newShapeFam.expMean = eExpMean[shape3];
            newShapeFam.expLambda = 1 / eExpMean[shape3];
            newShapeFam.expMin = eExpMin[shape3];
            newShapeFam.expMax = eExpMax[shape3];
            shape3++;
            break;
            
        case 4:
            newShapeFam.constRadi = econst[shape4];
            shape4++;
            break;
        }
        
        if (stopCondition == 1) {
            newShapeFam.p32Target = e_p32Targets[i];
        }
        
        // Save shape family to perminant array
        shapeFamily.push_back(newShapeFam);
    }
    
    if (nFamEll > 0 ) {
        // Can now delete/free the memory for these arrays
        delete[] ebetaDistribution;
        delete[] edistr;
        delete[] easpect;
        delete[] enumPoints;
        delete[] eAngleOne;
        delete[] eAngleTwo;
        delete[] ebeta;
        delete[] ekappa;
        delete[] eLogMean;
        delete[] esd;
        delete[] eExpMean;
        delete[] emin;
        delete[] emax;
        delete[] ealpha;
        delete[] econst;
        delete[] eLayer;
        delete[] eRegion;
        delete[] eLogMin;
        delete[] eLogMax;
        delete[] eExpMin;
        delete[] eExpMax;
        
        if (stopCondition == 1) {
            delete[] e_p32Targets;
        }
    }
    
    if (nFamRect > 0) {
        searchVar(inputFile, "rbetaDistribution:");
        rbetaDistribution = new bool[nFamRect];
        getInputAry(inputFile, rbetaDistribution, nFamRect);
        searchVar(inputFile, "rdistr:");
        rdistr = new unsigned int[nFamRect];
        getInputAry(inputFile, rdistr, nFamRect);
        searchVar(inputFile, "rLayer:");
        rLayer = new int[nFamRect];
        getInputAry(inputFile, rLayer, nFamRect);
        searchVar(inputFile, "rRegion:");
        rRegion = new int[nFamRect];
        getInputAry(inputFile, rRegion, nFamRect);
        searchVar(inputFile, "raspect:");
        raspect = new float[nFamRect];
        getInputAry(inputFile, raspect, nFamRect);
        searchVar(inputFile, "rAngleOption:");
        inputFile >> rAngleOption;
        
        if (orientationOption == 0) {
            searchVar(inputFile, "rtheta:");
            rAngleOne = new float[nFamRect];
            getInputAry(inputFile, rAngleOne, nFamRect);
            searchVar(inputFile, "rphi:");
            rAngleTwo = new float[nFamRect];
            getInputAry(inputFile, rAngleTwo, nFamRect);
        } else if (orientationOption == 1) {
            searchVar(inputFile, "rtrend:");
            rAngleOne = new float[nFamRect];
            getInputAry(inputFile, rAngleOne, nFamRect);
            searchVar(inputFile, "rplunge:");
            rAngleTwo = new float[nFamRect];
            getInputAry(inputFile, rAngleTwo, nFamRect);
        } else if (orientationOption == 2) {
            searchVar(inputFile, "rdip:");
            rAngleOne = new float[nFamRect];
            getInputAry(inputFile, rAngleOne, nFamRect);
            searchVar(inputFile, "rstrike:");
            rAngleTwo = new float[nFamRect];
            getInputAry(inputFile, rAngleTwo, nFamRect);
        }
        
        searchVar(inputFile, "rbeta:");
        rbeta = new float[nFamRect];
        getInputAry(inputFile, rbeta, nFamRect);
        searchVar(inputFile, "rkappa:");
        rkappa = new float[nFamRect];
        getInputAry(inputFile, rkappa, nFamRect);
        searchVar(inputFile, "rLogMean:");
        rLogMean = new float[nFamRect];
        getInputAry(inputFile, rLogMean, nFamRect);
        searchVar(inputFile, "rsd:");
        rsd = new float[nFamRect];
        getInputAry(inputFile, rsd, nFamRect);
        searchVar(inputFile, "rmin:");
        rmin = new float[nFamRect];
        getInputAry(inputFile, rmin, nFamRect);
        searchVar(inputFile, "rmax:");
        rmax = new float[nFamRect];
        getInputAry(inputFile, rmax, nFamRect);
        searchVar(inputFile, "ralpha:");
        ralpha = new float[nFamRect];
        getInputAry(inputFile, ralpha, nFamRect);
        searchVar(inputFile, "rExpMean:");
        rExpMean = new float[nFamRect];
        getInputAry(inputFile, rExpMean, nFamRect);
        searchVar(inputFile, "rconst:");
        rconst = new float[nFamRect];
        getInputAry(inputFile, rconst, nFamRect);
        searchVar(inputFile, "rLogMin:");
        rLogMin = new float[nFamRect];
        getInputAry(inputFile, rLogMin, nFamRect);
        searchVar(inputFile, "rLogMax:");
        rLogMax = new float[nFamRect];
        getInputAry(inputFile, rLogMax, nFamRect);
        searchVar(inputFile, "rExpMin:");
        rExpMin = new float[nFamRect];
        getInputAry(inputFile, rExpMin, nFamRect);
        searchVar(inputFile, "rExpMax:");
        rExpMax = new float[nFamRect];
        getInputAry(inputFile, rExpMax, nFamRect);
        
        if (stopCondition == 1) {
            // Get temp array for rectangle p32 targets,
            // Used to simplify initialization of shape family structures below
            searchVar(inputFile, "r_p32Targets:");
            r_p32Targets = new float[nFamRect];
            getInputAry(inputFile, r_p32Targets, nFamRect);
        }
    }
    
    // Set stop condition variables
    if (nFamRect > 0 || nFamEll > 0) {
        if (stopCondition == 0) { // npoly option
            searchVar(inputFile, "nPoly:");
            inputFile >> nPoly;
        } else if (stopCondition == 1) { // Stop program when p32 conditions per fracture family are met
            p32Status = new bool [nFamRect + nFamEll]; // Staus array for whether or not the family has reached its p32 requirement
            
            for (int i = 0; i < (nFamRect + nFamEll); i++) {
                // Zero the status flags
                p32Status[i] = 0;
            }
        }
    }
    
    // Counters, used to place variable into correct array index
    // distribution counters
    shape1 = 0; // Longnormal dist counter
    shape2 = 0; // Truncated power-law dist counter
    shape3 = 0; // Exponential dist counter
    shape4 = 0; // Constant dist counter
    betaCount = 0;
    
    // Create shape strucutres from data gathered above
    for (int i = 0; i < nFamRect; i++) {
        struct Shape newShapeFam;
        newShapeFam.shapeFamily = 1; // shapFam = 0 = ellipse, 1 = rect
        newShapeFam.distributionType = rdistr[i];
        newShapeFam.numPoints = 4; // Rectangle
        newShapeFam.aspectRatio = raspect[i];
        newShapeFam.angleOne = rAngleOne[i];
        newShapeFam.angleTwo = rAngleTwo[i];
        newShapeFam.kappa = rkappa[i];
        newShapeFam.angleOption = rAngleOption;
        newShapeFam.layer = rLayer[i];
        newShapeFam.region = rRegion[i];
        
        if (rbetaDistribution[i] == 1 ) { // If constant beta option
            newShapeFam.betaDistribution = 1;
            newShapeFam.beta = rbeta[betaCount];
            betaCount++;
        } else {
            newShapeFam.betaDistribution = 0;
        }
        
        // dist options:1 = lognormal, 2= truncated power-law, 3= exponential, 4=constant
        switch (rdistr[i]) {
        case 1: // Lognormal
            newShapeFam.mean = rLogMean[shape1];
            newShapeFam.sd = rsd[shape1];
            newShapeFam.logMin = rLogMin[shape1];
            newShapeFam.logMax = rLogMax[shape1];
            shape1++;
            break;
            
        case 2: // Truncated power-law
            newShapeFam.min = rmin[shape2];
            newShapeFam.max = rmax[shape2];
            newShapeFam.alpha = ralpha[shape2];
            shape2++;
            break;
            
        case 3:
            newShapeFam.expMean = rExpMean[shape3];
            newShapeFam.expLambda = 1 / rExpMean[shape3];
            newShapeFam.expMin = rExpMin[shape3];
            newShapeFam.expMax = rExpMax[shape3];
            shape3++;
            break;
            
        case 4:
            newShapeFam.constRadi = rconst[shape4];
            shape4++;
            break;
        }
        
        if (stopCondition == 1) {
            newShapeFam.p32Target = r_p32Targets[i];
        }
        
        // Save family to perminant array
        shapeFamily.push_back(newShapeFam);
    }
    
    if (nFamRect > 0 ) {
        // Can now delete/free the memory for these arrays
        delete[] rbetaDistribution;
        delete[] rdistr;
        delete[] raspect;
        delete[] rAngleOne;
        delete[] rAngleTwo;
        delete[] rbeta;
        delete[] rkappa;
        delete[] rLogMean;
        delete[] rsd;
        delete[] rExpMean;
        delete[] rmin;
        delete[] rmax;
        delete[] ralpha;
        delete[] rconst;
        delete[] rLayer;
        delete[] rRegion;
        delete[] rLogMin;
        delete[] rLogMax;
        delete[] rExpMin;
        delete[] rExpMax;
        
        if (stopCondition == 1) {
            delete[] r_p32Targets;
        }
    }
    
    searchVar(inputFile, "userEllipsesOnOff:");
    inputFile >> userEllipsesOnOff;
    
    if (userEllipsesOnOff != 0) {
        searchVar(inputFile, "UserEll_Input_File_Path:");
        inputFile >> tempstring;
        std::ifstream uEllFile;
        uEllFile.open(tempstring.c_str(), std::ifstream::in);
        checkIfOpen(uEllFile, tempstring);
        std::cout << "User Defined Ellipses File: " << tempstring << std::endl;
        searchVar(uEllFile, "nUserEll:");
        uEllFile >> nUserEll;
        searchVar(uEllFile, "Radii:");
        ueRadii = new float[nUserEll];
        getElements(uEllFile, ueRadii, nUserEll);
        searchVar(uEllFile, "Aspect_Ratio:");
        ueaspect = new float[nUserEll];
        getElements(uEllFile, ueaspect, nUserEll);
        searchVar(uEllFile, "AngleOption:");
        uEllFile >> ueAngleOption;
        searchVar(uEllFile, "Beta:");
        ueBeta = new float[nUserEll];
        getElements(uEllFile, ueBeta, nUserEll);
        searchVar(uEllFile, "Translation:");
        uetranslation = new double[3 * nUserEll];
        get2dAry(uEllFile, uetranslation, nUserEll);
        //
        searchVar(uEllFile, "userOrientationOption:");
        uEllFile >> userEllOrientationOption;
        std::cout << "userOrientationOption" << " " <<  userEllOrientationOption << std::endl;
        
        if (userEllOrientationOption == 0) {
            searchVar(uEllFile, "Normal:");
            uenormal = new double[3 * nUserEll];
            get2dAry(uEllFile, uenormal, nUserEll);
        } else if (userEllOrientationOption == 1) {
            searchVar(uEllFile, "Trend_Plunge:");
            ueTrendPlunge = new double[2 * nUserEll];
            get2dAry2(uEllFile, ueTrendPlunge, nUserEll);
            uenormal = new double[3 * nUserEll];
            // Convert Trend and Plunge into Dip and Strike
            double temp = M_PI / 180;
            
            for (int i = 0; i < nUserEll; i++) {
                int index1 = i * 2;
                int index2 = i * 3;
                // Trend and Plunge
                // ueTrendPlunge[index1] = Trend
                // ueTrendPlunge[index1+1] = Plunge
                double trend = ueTrendPlunge[index1] * temp;
                double plunge = ueTrendPlunge[index1 + 1] * temp;
                //std::cout << "trend & plunge: " << trend/temp << " " << plunge/temp << "\n";
                uenormal[index2] = cos(trend) * cos(plunge);
                uenormal[index2 + 1] = sin(trend) * cos(plunge);
                uenormal[index2 + 2] = sin(plunge);
            }
        } else if (userEllOrientationOption == 2) {
            searchVar(uEllFile, "Dip_Strike:");
            ueDipStrike = new double[2 * nUserEll];
            get2dAry2(uEllFile, ueDipStrike, nUserEll);
            uenormal = new double[3 * nUserEll];
            // Convert Trend and Plunge into Dip and Strike
            double temp = M_PI / 180;
            
            for (int i = 0; i < nUserEll; i++) {
                int index1 = i * 2;
                int index2 = i * 3;
                // Trend and Plunge
                // angleOne = Trend
                // angleTwo = Plunge
                double dip = ueDipStrike[index1] * temp;
                double strike = ueDipStrike[index1 + 1] * temp;
                //std::cout << "dip & strike: " << dip/temp << " " << strike/temp << "\n";
                uenormal[index2] = sin(dip) * sin(strike);
                uenormal[index2 + 1] = -sin(dip) * cos(strike);
                uenormal[index2 + 2] = cos(dip);
            }
        }
        
        searchVar(uEllFile, "Number_of_Vertices:");
        uenumPoints = new unsigned int[nUserEll];
        getElements(uEllFile, uenumPoints, nUserEll);
        uEllFile.close();
    }
    
    searchVar(inputFile, "userRectanglesOnOff:");
    inputFile >> userRectanglesOnOff;
    
    if (userRectanglesOnOff != 0) {
        searchVar(inputFile, "UserRect_Input_File_Path:");
        inputFile >> tempstring;
        std::ifstream uRectFile;
        uRectFile.open(tempstring.c_str(), std::ifstream::in);
        checkIfOpen(uRectFile, tempstring);
        std::cout << "User Defined Rectangles File: " << tempstring << std::endl;
        searchVar(uRectFile, "nUserRect:");
        uRectFile >> nUserRect;
        searchVar(uRectFile, "Radii:");
        urRadii = new float[nUserRect];
        getElements(uRectFile, urRadii, nUserRect);
        searchVar(uRectFile, "AngleOption:");
        uRectFile >> urAngleOption;
        searchVar(uRectFile, "Beta:");
        urBeta = new float[nUserRect];
        getElements(uRectFile, urBeta, nUserRect);
        searchVar(uRectFile, "Aspect_Ratio:");
        uraspect = new float[nUserRect];
        getElements(uRectFile, uraspect, nUserRect);
        searchVar(uRectFile, "Translation:");
        urtranslation = new double[3 * nUserRect];
        get2dAry(uRectFile, urtranslation, nUserRect);
        searchVar(uRectFile, "userOrientationOption:");
        uRectFile >> userRectOrientationOption;
        
        // std::cout << "userRectOrientationOption: " << userRectOrientationOption << " \n";
        if (userRectOrientationOption == 0) {
            searchVar(uRectFile, "Normal:");
            urnormal = new double[3 * nUserRect];
            get2dAry(uRectFile, urnormal, nUserRect);
        } else if (userRectOrientationOption == 1) {
            searchVar(uRectFile, "Trend_Plunge:");
            urTrendPlunge = new double[2 * nUserRect];
            get2dAry2(uRectFile, urTrendPlunge, nUserRect);
            urnormal = new double[3 * nUserRect];
            double temp = M_PI / 180;
            
            // Convert Trend and Plunge into Dip and Strike
            for (int i = 0; i < nUserRect; i++) {
                int index1 = i * 2;
                int index2 = i * 3;
                // Trend and Plunge
                // urTrendPlunge[index1] = Trend
                // urTrendPlunge[index1+1] = Plunge
                // convert to radians
                double trend = urTrendPlunge[index1] * temp;
                double plunge = urTrendPlunge[index1 + 1] * temp;
                //std::cout << "normal: " << urnormal[index2] << " " << urnormal[index2+1] << " " << urnormal[index2+2] << "\n";
                //std::cout << "trend & plunge: " << trend/temp << " " << plunge/temp << "\n";
                urnormal[index2] = cos(trend) * cos(plunge);
                urnormal[index2 + 1] = sin(trend) * cos(plunge);
                urnormal[index2 + 2] = sin(plunge);
                //std::cout << "normal: " << urnormal[index2] << " " << urnormal[index2+1] << " " << urnormal[index2+2] << "\n";
            }
        } else if (userRectOrientationOption == 2) {
            searchVar(uRectFile, "Dip_Strike:");
            urDipStrike = new double[2 * nUserRect];
            get2dAry2(uRectFile, urDipStrike, nUserRect);
            urnormal = new double[3 * nUserRect];
            // Convert Dip and Strike into normal vectors
            double temp = M_PI / 180;
            
            for (int i = 0; i < nUserRect; i++) {
                int index1 = i * 2;
                int index2 = i * 3;
                // dip and strike
                // urDipStrike[index1] = dip
                // urDipStrike[index1+1] = strike
                // convert to radians
                double dip = urDipStrike[index1] * temp;
                double strike = urDipStrike[index1 + 1] * temp;
                //std::cout << "dip & strike: " << dip/temp << " " << strike/temp << "\n";
                urnormal[index2] = sin(dip) * sin(strike);
                urnormal[index2 + 1] = -sin(dip) * cos(strike);
                urnormal[index2 + 2] = cos(dip);
            }
        }
        
        uRectFile.close();
    }
    
    searchVar(inputFile, "userEllByCoord:");
    inputFile >> userEllByCoord;
    searchVar(inputFile, "userRecByCoord:");
    inputFile >> userRecByCoord;
    searchVar(inputFile, "userPolygonByCoord:");
    inputFile >> userPolygonByCoord;
    
    if ((userRectanglesOnOff == 1 || userRecByCoord == 1) && (userEllipsesOnOff == 1 || userEllByCoord == 1)) {
        searchVar(inputFile, "insertUserRectanglesFirst:");
        inputFile >> insertUserRectanglesFirst;
    } else {
        insertUserRectanglesFirst = 0;
    }
    
    if (userPolygonByCoord != 0) {
        searchVar(inputFile, "PolygonByCoord_Input_File_Path:");
        inputFile >> polygonFile;
    }
    
    if (userEllByCoord != 0) {
        searchVar(inputFile, "EllByCoord_Input_File_Path:");
        inputFile >> tempstring;
        std::ifstream file;
        file.open(tempstring.c_str(), std::ifstream::in);
        checkIfOpen(file, tempstring);
        std::cout << "User Defined Ellipses by Coordinates File: " << tempstring << std::endl;
        searchVar(file, "nEllipses:");
        file >> nEllByCoord;
        searchVar(file, "nNodes:");
        file >> nEllNodes;
        userEllCoordVertices = new double[3 * nEllNodes * nEllByCoord];
        searchVar(file, "Coordinates:");
        getCords(file, userEllCoordVertices, nEllByCoord, nEllNodes);
        file.close();
    }
    
    if (userRecByCoord != 0) {
        searchVar(inputFile, "RectByCoord_Input_File_Path:");
        inputFile >> tempstring;
        std::ifstream uCoordFile;
        uCoordFile.open(tempstring.c_str(), std::ifstream::in);
        checkIfOpen(uCoordFile, tempstring);
        std::cout << "User Defined Rectangles by Coordinates File: " << tempstring << std::endl;
        searchVar(uCoordFile, "nRectangles:");
        uCoordFile >> nRectByCoord;
        searchVar(uCoordFile, "Coordinates:");
        //4 vertices, 12 elements x,y,z per rectangle:
        userRectCoordVertices = new double[12 * nRectByCoord];
        getRectCoords(uCoordFile, userRectCoordVertices, nRectByCoord);
        uCoordFile.close();
    }
    
    searchVar(inputFile, "aperture:");
    inputFile >> aperture;
    
    if (aperture == 1) {
        searchVar(inputFile, "meanAperture:");
        inputFile >> meanAperture;
        searchVar(inputFile, "stdAperture:");
        inputFile >> stdAperture;
    } else if (aperture == 2) {
        searchVar(inputFile, "apertureFromTransmissivity:");
        getInputAry(inputFile, apertureFromTransmissivity, 2);
    } else if (aperture == 3) {
        searchVar(inputFile, "constantAperture:");
        inputFile >> constantAperture;
    } else if (aperture == 4) {
        searchVar(inputFile, "lengthCorrelatedAperture:");
        getInputAry(inputFile, lengthCorrelatedAperture, 2);
    } else {
        std::cerr << "\nERROR: Aperture option not recognised\n";
        exit(1);
    }
    
    searchVar(inputFile, "permOption:");
    inputFile >> permOption;
    
    if (permOption != 0) {
        searchVar(inputFile, "constantPermeability:");
        inputFile >> constantPermeability;
    }
    
    // Error check on stopping parameter
    if (nFamEll + nFamRect == 0 && stopCondition != 0) { // If no stochastic shapes, use nPoly option with npoly = number of user polygons
        std::cout << "\nWARNING: You have defined stopCondition = 1 (P32 program stopping condition) but have no stochastic shape families defined. Automatically setting stopCondition to 0 for use with user defined polygons and nPoly.\n\n";
        stopCondition = 0;
        
        if (userEllipsesOnOff == 0 && userRectanglesOnOff == 0 && userRecByCoord == 0 ) {
            std::cout << "ERROR: All polygon generating options are off or undefined, please check input file for errors.\n\n";
            exit(1);
        }
        
        int count = 0; // Count of user defined polygons
        
        if (userEllipsesOnOff == 1) {
            count += nUserEll;
        }
        
        if (userRectanglesOnOff == 1) {
            count += nUserRect;
        }
        
        if (userRecByCoord == 1) {
            count += nRectByCoord;
        }
        
        // Set nPoly to the amount of user defined polygons
        nPoly = count;
    }
    
    inputFile.close();
    
    // Convert angles to rad if necessary, all functions and code require radians
    for (unsigned int i = 0; i < shapeFamily.size(); i ++) {
        if (shapeFamily[i].angleOption == 1 ) { // Convert deg to rad
            double temp = M_PI / 180;
            shapeFamily[i].beta *= temp;
            shapeFamily[i].angleOne *= temp;
            shapeFamily[i].angleTwo *= temp;
            shapeFamily[i].angleOption = 0; // Angles now in radians
        }
    }
}

/****************************************************************************************/
// Depreciated Function
// Prints all input variables, useful for debugging.
// NOTE: Needs to be updated. There bave been changes to input variables
void printInputVars() {
    std::cout << "npoly = " << nPoly << std::endl;
    std::cout << "tripleIntersections = " << tripleIntersections << std::endl;
    std::cout << "domainsize = {" << domainSize[0] << ", " << domainSize[1] << ", " << domainSize[2] << "}\n";
    std::cout << "h = " << h << std::endl;
    std::cout << "visualizationMode = " << visualizationMode << std::endl;
    std::cout << "seed = " << seed << std::endl;
    std::cout << "keepOnlyLargestCluster = " << keepOnlyLargestCluster << std::endl;
    std::cout << "domainSizeIncrease = {" << domainSizeIncrease[0] << "," << domainSizeIncrease[1] << "," << domainSizeIncrease[2] << "}\n";
    std::cout << "boundaryFaces = {" << boundaryFaces[0] << "," << boundaryFaces[1] << "," << boundaryFaces[2] << "," << boundaryFaces[3] << "," << boundaryFaces[4] << "," << boundaryFaces[5] << "}\n";
    std::cout << "nFamRect = " << nFamRect << std::endl;
    std::cout << "nFamEll = " << nFamEll << std::endl;
    printAry(famProb, "famProb", (nFamEll + nFamRect));
    printAry(edistr, "edistr", nFamEll);
    printAry(enumPoints, "enumPoints", nFamEll);
    std::cout << "eAngleOption = " << eAngleOption << std::endl;
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
    printAry(eLogMean, "eLogMean", nFamEll);
    printAry(esd, "esd", nFamEll);
    printAry(eExpMean, "eExpMean", nFamEll);
    printAry(econst, "econst", nFamEll);
    printAry(emin, "emin", nFamEll);
    printAry(emax, "emax", nFamEll);
    printAry(ealpha, "ealpha", nFamEll);
    printAry(rdistr, "rdistr", nFamRect);
    printAry(raspect, "raspect", nFamRect);
    std::cout << "rAngleOption = " << rAngleOption << std::endl;
    
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
    printAry(rExpMean, "rExpMean", nFamRect);
    printAry(rconst, "rconst", nFamRect);
    std::cout << "userEllipsesOnOff = " << userEllipsesOnOff << std::endl;
    
    if (userEllipsesOnOff != 0) {
        std::cout << "nUserEll = " << nUserEll << "\n";
        printAry(ueRadii, "ueRadii", nUserEll);
        std::cout << "urAngleOption = " << ueAngleOption << std::endl;
        printAry(ueBeta, "ueBeta", nUserEll);
        printAry(ueaspect, "ueaspect", nUserEll);
        print2dAry(uetranslation, "uetranslation", nUserEll);
        print2dAry(uenormal, "uenormal", nUserEll);
        printAry(uenumPoints, "uenumPoints", nUserEll);
    }
    
    std::cout << "userRectanglesOnOff = " << userRectanglesOnOff << std::endl;
    
    if (userRectanglesOnOff != 0) {
        std::cout << "nUserRect = " << nUserRect << "\n";
        printAry(urRadii, "urRadii", nUserRect);
        std::cout << "urAngleOption = " << urAngleOption << std::endl;
        printAry(urBeta, "urBeta", nUserRect);
        printAry(urRadii, "urRadii", nUserRect);
        printAry(uraspect, "uraspect", nUserRect);
        print2dAry(urtranslation, "urtranslation", nUserRect);
        print2dAry(urnormal, "urnormal", nUserRect);
    }
    
    std::cout << "userRecByCoord = " << userRecByCoord << std::endl;
    
    if (userRecByCoord != 0) {
        std::cout << "nRectByCoord = " << nRectByCoord << std::endl;
        printRectCoords(userRectCoordVertices, "userRectCoordVertices", nRectByCoord);
    }
    
    std::cout << "aperture option: " << aperture << std::endl;
    
    if (aperture == 1) {
        std::cout << "meanAperture = " << meanAperture << std::endl;
        std::cout << "stdAperture = " << stdAperture << std::endl;
    } else if (aperture == 2) {
        printAry(apertureFromTransmissivity, "apertureFromTransmissivity", 2);
    } else if (aperture == 3) {
        std::cout <<  "constantAperture = " << constantAperture << std::endl;
    } else if (aperture == 4) {
        printAry(lengthCorrelatedAperture, "lengthCorrelatedAperture", 2);
    }
    
    if (permOption == 0) {
        std::cout << "Permeability: Function of aperture\n";
    } else {
        std::cout << "ConstantPermeability = " << constantPermeability << std::endl;
    }
}





