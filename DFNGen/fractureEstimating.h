#ifndef _fractureEstimating_h_
#define _fractureEstimating_h_

#include <random>
#include <vector>
#include "structures.h"
#include "distributions.h"

void printShapeFams(std::vector<Shape> &shapeFamilies);
void dryRun(std::vector<Shape> &shapeFamilies, float *shapeProb, std::mt19937_64 &generator, Distributions &distributions);
void addRadiiToLists(float percent, std::vector<Shape> &shapeFamilies, std::mt19937_64 &generator, Distributions &distributions);
void printGeneratingFracturesLessThanHWarning(int famIndex, Shape &shapeFam);
void generateRadiiLists_nPolyOption(std::vector<Shape> &shapeFamilies, float *famProb, std::mt19937_64 &generator, Distributions &distributions);
void addRadii(int amountToadd,int famIdx, Shape &shapeFam, std::mt19937_64 &generator, Distributions &distributions);
void sortRadii(std::vector<Shape> &shapeFam);


#endif
