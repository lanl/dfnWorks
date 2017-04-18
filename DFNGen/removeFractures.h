#ifndef _REMOVEFRACTURES_H
#define _REMOVEFRACTURES_H

#include "structures.h"
#include <vector>

void removeFractures(double minSize, std::vector<Poly> &acceptedPolys, std::vector<IntPoints> &intPts, std::vector<Point> triplePoints, Stats  &pstats);
#endif
