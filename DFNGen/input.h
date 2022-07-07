#ifndef _input_h_
#define _input_h_
#include <string>
#include <fstream>
// Variable prototypes for user input variables

extern short stopCondition;
extern unsigned int nPoly;
extern double domainSize[3];
extern double h;
extern float radiiListIncrease;
extern double eps;
extern bool disableFram;
extern bool visualizationMode;
extern bool tripleIntersections;
extern bool boundaryFaces[6];
extern bool keepOnlyLargestCluster;
extern bool keepIsolatedFractures;
extern bool printRejectReasons;
extern bool outputFinalRadiiPerFamily;
extern bool outputAcceptedRadiiPerFamily;
extern bool ecpmOutput;
extern int orientationOption;
extern bool *ebetaDistribution;
extern bool *rbetaDistribution;
extern bool insertUserRectanglesFirst;
extern bool forceLargeFractures;
extern unsigned int seed;
extern float domainSizeIncrease[3];
extern float removeFracturesSmallerThan;
extern int nFamRect;
extern int nUserRect;
extern int nFamEll;
extern int nUserEll;
extern float *famProb;
extern float *famProbOriginal;
extern int *edistr;
extern float *easpect;
extern unsigned int *enumPoints;
extern bool  eAngleOption;
extern float *eAngleOne;
extern float *eAngleTwo;
extern float *ebeta;
extern float *ekappa;
extern float *eLogMean;
extern float *eLogMin;
extern float *eLogMax;
extern float *eExpMin;
extern float *eExpMax;
extern float *esd;
extern float *eExpMean;
extern float *econst;
extern float *emin;
extern float *emax;
extern float *ealpha;
extern unsigned int *rdistr;
extern float *raspect;
extern bool rAngleOption;
extern float *rAngleOne;
extern float *rAngleTwo;
extern float *rbeta;
extern float *rkappa;
extern float *rLogMean;
extern float *rLogMin;
extern float *rLogMax;
extern float *rExpMin;
extern float *rExpMax;
extern float *rsd;
extern float *rmin;
extern float *rmax;
extern float *ralpha;
extern float *rExpMean;
extern float *rconst;
extern bool ueAngleOption;
extern float *ueRadii;
extern float *ueBeta;
extern float *ueaspect;
extern double *uetranslation;
extern double *uenormal;
extern unsigned int *uenumPoints;
extern bool userRectanglesOnOff;
extern bool userEllipsesOnOff;
extern bool outputAllRadii;
extern float *urRadii;
extern bool urAngleOption;
extern float *urBeta;
extern float *uraspect;
extern double *urtranslation;
extern double *urnormal;
extern bool userRecByCoord;
extern bool userEllByCoord;
extern bool userPolygonByCoord;
extern unsigned int nRectByCoord;
extern double *userRectCoordVertices;
extern double *userEllCoordVertices;
extern unsigned int nEllByCoord;
extern unsigned int nEllNodes;
extern int aperture;
extern float meanAperture;
extern float stdAperture;
extern float apertureFromTransmissivity[2];
extern double constantAperture;
extern double lengthCorrelatedAperture[2];
extern bool permOption;
extern double constantPermeability;
extern float *econst;
extern float *rconst;
extern float *layers;
extern float *layerVol;
extern int *rLayer;
extern int *eLayer;
extern float *regions;
extern float *regionVol;
extern int *rRegion;
extern int *eRegion;
extern bool *p32Status;
extern bool ignoreBoundaryFaces;
extern int numOfLayers;
extern int rejectsPerFracture;
extern float *e_p32Targets;
extern float *r_p32Targets;
extern float removeFracturesLessThan;
extern std::string polygonFile;

#endif







