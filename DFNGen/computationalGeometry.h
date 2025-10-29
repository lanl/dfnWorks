#ifndef _computationalGeometry_h_
#define _computationalGeometry_h_
#include "structures.h"
#include <fstream>

void createBoundingBox(struct Poly &newPoly);
void printBoundingBox(struct Poly &newPoly);
bool checkBoundingBox(struct Poly &poly1, struct Poly &poly2);
struct IntPoints findIntersections(short &flag, struct Poly &poly1, struct Poly &poly2);
int FRAM(struct IntPoints &intPts, unsigned int count, std::vector<IntPoints> &intPtsList, struct Poly &newPoly, struct Poly &poly2, struct Stats &pstats, std::vector<TriplePtTempData> &tempData, std::vector<Point> &triplePoints, std::vector<IntPoints> &tempIntPts);
int intersectionChecking(struct Poly &newPoly, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints);
double pointToLineSeg(const double *point, const double *line);
double pointToLineSeg(const Point &point, const double *line);
bool checkDistanceFromNodes(struct Poly &poly, IntPoints &intPts, double minSize, Stats &pstats);
bool checkCloseEdge(Poly &poly1, IntPoints &intPts, double shrinkLimit, Stats &pstats);
double lineSegToLineSeg(const double *line1, const double *line2, Point &pt);
double lineSegToLineSegSep(const double *line1, const double *line2);
Point lineIntersection3D(const double *p1, double *v1, const double *p2, double *v2);
bool checkDistIntPtsEdge(struct PointList &tmpPoints, struct Poly &newPoly, struct Poly &poly2);
void applyRotation2D(struct Poly &newPoly, float angle);
void applyRotation3D(struct Poly &newPoly, double *normal);
void translate(Poly &newPoly, double *translation);
int checkForTripleIntersections(IntPoints &intPts, unsigned int count, std::vector<IntPoints> &intPtsList, Poly &newPoly, Poly &poly2, std::vector<TriplePtTempData> &tempData, std::vector<Point> &triplePoints);
struct IntPoints polyAndIntersection_RotationToXY(struct IntPoints &intersection, Poly &newPoly, std::vector<Point> &triplePoints, std::vector<Point> &tempTripPts);
double *rotationMatrix(double *normalA, double *normalB);
bool shrinkIntersection(IntPoints &intPts, double *edge, double shrinkLimit, double firstNodeMinDist, double minDist);
bool checkDistToOldIntersections(std::vector<IntPoints> &intPtsList, IntPoints &intPts, Poly &poly2, double minDistance);
bool checkDistToNewIntersections(std::vector<IntPoints> &tempIntPts, IntPoints &intpts,  std::vector<TriplePtTempData> &tempTripPts, double minDistance);
bool PointOnLineSeg(const Point &pt, const double *line);
bool PointOnLineSeg(const double *pt, const double *line);
#endif

