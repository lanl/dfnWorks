#ifndef _output_h_
#define _output_h_
#include <vector>
#include "structures.h"
#include <fstream>
#include <string>

void writeRotationData(std::vector<Poly> &acceptedPoly, std::vector<unsigned int> &finalFractures, std::vector<Shape> &shapeFamilies, std::string output);
void writeNormalVectors(std::vector<Poly> &acceptedPoly, std::vector<unsigned int> &finalFractures, std::vector<Shape> &shapeFamilies, std::string output);
void writeOutput(char* outputFolder, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts,
                 std::vector<Point> &triplePoints, struct Stats &pstats,
                 std::vector<unsigned int> &finalFractures, std::vector<Shape> &shapeFamilies);

void writePoints(std::ostream &output, std::vector<Point> &points, int start, unsigned int &count);

bool DIR_exists(const char *path);

inline void savePoints(std::stringstream &stream, std::vector<Point> &points,
                       int fract1, int fract2, int start);
void adjustIntFractIDs(std::vector<unsigned int> &finalFractures, std::vector<Poly> &allPolys,
                       std::vector<IntPoints> &intPts);

inline void writeVertices(std::ostream &output, Poly &frac);

void rotateFractures(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly);

void debugINP(std::vector<Poly> &allPolys, Stats &pstats, std::string &outputFolder);

void finishWritingIntFile(std::ostream &fractIntFile, int fract1, int numPoints, int numIntersections,
                          std::vector<unsigned int> &intStart, std::vector<unsigned int> &intersectingFractures);

void writeRadiiAcceptedFile();
void writeIntersectionFiles(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly,
                            std::vector<IntPoints> &intPts, std::vector<Point> &triplePoints, std::string intersectionFolder, struct Stats &pstats);
void writePolysInp(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writePolys(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writePolysInp_old(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writeParamsFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<Shape> &shapeFamilies, Stats &pstats, std::vector<Point> &triplePoints, std::string &output);
// void writeApertureFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
// void writePermFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writeFinalPolyRadii(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writeFinalPolyArea(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writeAllAcceptedRadii(std::vector<Poly> &acceptedPoly, std::string &output);
void writeAllAcceptedRadii_OfFamily(int familyNum, std::vector<Poly> &acceptedPoly, std::string &output);
void writeFinalRadii_OfFamily(std::vector<unsigned int> &finalFractures, int familyNum, std::vector<Poly> &acceptedPoly, std::string &output);
void writeTriplePts(std::vector<Point> &triplePoints, std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly,
                    std::vector<IntPoints> &intPts, std::string &output);
void makeDIR(const char *dir);
void writeRadiiFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writeRejectionStats(Stats &pstats, std::string &output);
void writeUserRejectedFractureInformation(Stats &pstats, std::string &output);
void writeShapeFams(std::vector<Shape> &shapeFamilies, std::string &output);
void writeFractureTranslations(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output);
void writeConnectivity(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts, std::string &output);
void writeRejectsPerAttempt(Stats &pstats, std::string &output);

void writeGraphData(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts);
void writeMidPoint(std::ofstream &fp, int fract1, int fract2, double x1, double y1, double z1, double x2, double y2, double z2);
void writeBoundaryFiles(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly);

#endif
