#ifndef _insertShape_h_
#define _insertShape_h_
#include <vector>
#include <random>
#include "structures.h"
#include <fstream>
#include <string>
#include "distributions.h"

void insertUserRects(std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints);
void insertUserEll(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints);
void insertUserRectsByCoord(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints);
void insertUserEllByCoord(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints);
struct Poly generatePoly(struct Shape &shapeFam, std::mt19937_64 &generator, Distributions &distributions, int familyIndex, bool useList);
void initializeRectVertices(struct Poly &newPoly, float radius, float aspectRatio);
void assignAperture(struct Poly &newPoly,  std::mt19937_64 &generator);
void assignPermeability(struct Poly &newPoly);
void reTranslatePoly(struct Poly &newPoly, struct Shape &shapeFam, std::mt19937_64 &generator);
bool p32Complete(int size);
void initializeEllVertices(struct Poly &newPoly, float radius, float aspectRatio, float *thetaList, int numPoints);
void printRejectReason(int rejectCode, struct Poly newPoly);
int getFamilyNumber(int familyIndex, int family);
std::string shapeType(struct Shape &shapeFam);
double getLargestFractureRadius(Shape &shapeFam);
struct Poly generatePoly_withRadius(double radius, struct Shape &shapeFam, std::mt19937_64 &generator, Distributions &distributions, int familyIndex);

#endif

