#ifndef _clusterGroups_h_
#define _clusterGroups_h_
#include "structures.h"
#include <vector>

std::vector<unsigned int> getCluster(Stats &pstats);
bool facesMatch(bool *facesOption, bool *faces);
void assignGroup(Poly &newPoly, Stats &pstats, int newPolyIndex);
void updateGroups(Poly &newPoly, std::vector<Poly> &acceptedPoly, std::vector<unsigned int> &encounteredGroups, Stats &pstats, int newPolyIndex);

#endif
