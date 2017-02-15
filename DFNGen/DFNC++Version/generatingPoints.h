#ifndef _generatingPoints_h_
#define _generatingPoints_h_
#include "structures.h"
#include <vector>
#include <random>
#include "distributions.h"

std::vector<Point> discretizeLineOfIntersection(double *pt1, double *pt2, double dist);
struct Point lineFunction3D(double *v, double *point, double t);
double *fisherDistribution(double theta, double phi, double kappa, std::mt19937_64 &generator);
double *randomTranslation(std::mt19937_64 &generator, float xMin, float xMax, float yMin, float yMax, float zMin, float zMax);
float truncatedPowerLaw(float randomNum, float emin, float emax, float alpha);
void generateTheta(float * &thetaArray, float aspectRatio, int nPoints);
bool greaterThan(float i, float j);

/*****************************/
/* Returns max value from array */
/*template <typename T>
T max(T *ary, int size){
    T max = ary[0];
    for (int i = 1; i < size; i++){
        if (max < ary[i]){
            max = ary[i];
        }
    }
    return max;
}*/

#endif
