#ifndef _QUASI2DDOMIAN_H
#define _QUASI2DDOMIAN_H

#include "structures.h"
#include <vector>

void polygonBoundary(std::vector<Poly> &acceptedPolys, std::vector<IntPoints> &intPts, std::vector<Point> triplePoints, Stats  &pstats);
bool inPolygonBoundary(double x, double y);

#endif
