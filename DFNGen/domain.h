#ifndef _domain_h_
#define _domain_h_
#include "structures.h"

bool domainTruncation(Poly &newPoly, double *domainSize, std::vector<IntPoints> &boundaryPts, int newPolyIndx);
void printPoints(std::vector<double> &point);

#endif
