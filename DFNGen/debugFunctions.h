#ifndef _DEBUGFUNCTIONS_H_
#define _DEBUGFUNCTIONS_H_

#include <vector>
#include "structures.h"

void printAllPolys(std::vector<Poly> &acceptedPoly);
void printAllTriplePts(std::vector<Point> &triplePois);
void printIntersectionData(std::vector<IntPoints> &intPts);
void printGroupData(Stats &pstats, std::vector<Poly> &acceptedPoly);
void printPolyData(struct Poly &poly);
void printShapeFams(std::vector<Shape> &shapeFamilies);
#endif

