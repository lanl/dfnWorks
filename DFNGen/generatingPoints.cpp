#include "generatingPoints.h"
#include <cmath>
#include <iostream>
#include <vector>
#include "structures.h"
#include "vectorFunctions.h"
#include "computationalGeometry.h"
#include <algorithm>
#include "insertShape.h"


/**************************************************************************/
/********************  Discretize Intersection  ***************************/
/*!
 * \brief Discretizes a line segment by generating points along its intersection.
 *
 * \param pt1 End point 1, array of three doubles {x, y, z}
 * \param pt2 End point 2, array of three doubles {x, y, z}
 * \param dist Distance between endpoints of the line segment.
 * \return List of 3D points of the discretized nodes, including end points.
 */
std::vector<Point> discretizeLineOfIntersection(double *pt1, double *pt2, double dist) {
    std::vector<Point> pointsList;
    
    // If reduced mesh, just save endpoints
    if (visualizationMode == 1) {
        Point pt;
        pt.x = pt1[0];
        pt.y = pt1[1];
        pt.z = pt1[2];
        pointsList.push_back(pt);
        pt.x = pt2[0];
        pt.y = pt2[1];
        pt.z = pt2[2];
        pointsList.push_back(pt);
        return pointsList;
    }
    
    double v[3] = {pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2]}; // {x2-x1, y2-y1, z2-z1};
    double p[3] = {pt1[0], pt1[1], pt1[2]}; // {x1, y1, z1};
//    double dist = magnitude((pt1[0]-pt2[0]), (pt1[1]-pt2[1]), (pt1[2]-pt2[2])); // (x1-x2), (y1-y2), (z1-z2));
    double nprime = std::ceil(2 * dist / h); // I think this could be dist / h rather then 2 * dist / h 
    double hprime = 1 / nprime;
    double *xx = new double[(int)nprime + 1];
    int i;
    double temp = 0;
    
    for (i = 0; i < nprime; i++) { // Array from 0 - 1 with step = hprime
        xx[i] = temp;
        temp += hprime;
    }
    
    xx[i] = 1; // Make sure last element is exactly 1
    pointsList.reserve((int) nprime + 1);
    
    for (i = 0; i < nprime + 1; i++) {
        pointsList.push_back((lineFunction3D(v, p, xx[i])));
    }
    
    delete[] xx;
    return pointsList;
}


/**************************************************************************/
/*********************** Parametric Line Function *************************/
/*!
 * \brief Returns a point on a parametric line at a given parameter t.
 *
 * \param v Array of three doubles {x, y, z}, direction vector of the line segment.
 * \param point Array of three doubles {x, y, z}, start point of the line.
 * \param t Parameter value, 0 <= t <= 1.
 * \return Point on the line corresponding to parameter t.
 */
Point lineFunction3D(double *v, double *point, double t) {
    Point pt;
    pt.x = point[0] + v[0] * t;
    pt.y = point[1] + v[1] * t;
    pt.z = point[2] + v[2] * t;
    return pt;
}



void anglesToNormal(double angleOne, double angleTwo, double v1[3]) {
    /**
    * @brief Converts orientation angles into a unit normal vector.
    *
    * This function maps orientation angles into a 3D Cartesian unit vector
    * depending on the chosen orientation system. The supported options are:
    *   - orientationOption = 0 : Spherical coordinates (theta, phi)
    *       - angleOne = theta (angle from the z-axis)
    *       - angleTwo = phi (azimuth in the x-y plane from the x-axis)
    *   - orientationOption = 1 : Trend and Plunge
    *       - angleOne = trend (azimuth of the vector in the x-y plane)
    *       - angleTwo = plunge (angle below the horizontal plane)
    *   - orientationOption = 2 : Dip and Strike
    *       - angleOne = dip (angle from horizontal plane)
    *       - angleTwo = strike (azimuth of strike direction)
    *
    *
    * @param angleOne First orientation angle (meaning depends on orientationOption).
    * @param angleTwo Second orientation angle (meaning depends on orientationOption).
    * @param[out] v1 Array of size 3 that will contain the resulting unit normal vector {x, y, z}.
    */

    if (orientationOption == 0) {
        // Spherical Coordinates
        // angleOne = Theta
        // angleTwo = Phi
        v1[0] = sin(angleOne) * cos(angleTwo);
        v1[1] = sin(angleOne) * sin(angleTwo);
        v1[2] = cos(angleOne);
    } else if (orientationOption == 1) {
        // Trend and Plunge
        // angleOne = Trend
        // angleTwo = Plunge
        v1[0] = cos(angleOne) * cos(angleTwo);
        v1[1] = sin(angleOne) * cos(angleTwo);
        v1[2] = sin(angleTwo);
    } else if (orientationOption == 2) {
        // Dip and Strike
        // angleOne = Dip
        // angleTwo = Strike
        v1[0] = sin(angleOne) * cos(angleTwo);
        v1[1] = -sin(angleOne) * sin(angleTwo);
        v1[2] = cos(angleOne);
    }

}

/**************************************************************************/
/****** Fisher Distributions for Generating polygons Normal Vectors *******/
/*!
 * \brief Creates and returns an x,y,z array of doubles using the Fisher distribution.
 *
 * \note Uses new[] to return an array. NEED TO USE delete[] TO FREE THE MEMORY AFTER USE.
 *
 * \param angleOne The angle theta that the normal vector makes with the z-axis.
 * \param angleTwo The angle phi that the projection of the normal onto the x-y plane makes with the x-axis.
 * \param kappa Concentration parameter for the Fisher distribution.
 * \param generator Random number generator, see std C++ <random> library.
 * \return A Fisher distribution array {x, y, z}. Used for random generation of polygon normal vectors.
 */
double *fisherDistribution(double angleOne, double angleTwo, double kappa, std::mt19937_64 &generator) {
    double ck = (std::exp(kappa) - std::exp(-kappa)) / kappa;
    double v1[3];

    anglesToNormal(angleOne, angleTwo, v1);

    double u[3] = {0, 0, 1};
    double *xProd = crossProduct(u, v1);
    double R[9];
    
    // Get rotation matrix if normal vectors are not the same (if xProd is not zero vector)
    if (!(std::abs(xProd[0]) <= eps && std::abs(xProd[1]) <= eps && std::abs(xProd[2]) <= eps )) {
        // Since vectors are normalized, sin = magnitude(AxB) and cos = A . B
        double sin = sqrt(xProd[0] * xProd[0] + xProd[1] * xProd[1] + xProd[2] * xProd[2]);
        double cos = dotProduct(u, v1);
        double v[9] = {0, -xProd[2], xProd[1], xProd[2], 0, -xProd[0], -xProd[1], xProd[0], 0};
        double scalar = (1.0f - cos) / (sin * sin);
        double vSquared[9];
        vSquared[0] = (v[0] * v[0] + v[1] * v[3] + v[2] * v[6]) * scalar;
        vSquared[1] = (v[0] * v[1] + v[1] * v[4] + v[2] * v[7]) * scalar;
        vSquared[2] = (v[0] * v[2] + v[1] * v[5] + v[2] * v[8]) * scalar;
        vSquared[3] = (v[3] * v[0] + v[4] * v[3] + v[5] * v[6]) * scalar;
        vSquared[4] = (v[3] * v[1] + v[4] * v[4] + v[5] * v[7]) * scalar;
        vSquared[5] = (v[3] * v[2] + v[4] * v[5] + v[5] * v[8]) * scalar;
        vSquared[6] = (v[6] * v[0] + v[7] * v[3] + v[8] * v[6]) * scalar;
        vSquared[7] = (v[6] * v[1] + v[7] * v[4] + v[8] * v[7]) * scalar;
        vSquared[8] = (v[6] * v[2] + v[7] * v[5] + v[8] * v[8]) * scalar;
        R[0] = 1 + v[0] + vSquared[0];
        R[1] = 0 + v[1] + vSquared[1];
        R[2] = 0 + v[2] + vSquared[2];
        R[3] = 0 + v[3] + vSquared[3];
        R[4] = 1 + v[4] + vSquared[4];
        R[5] = 0 + v[5] + vSquared[5];
        R[6] = 0 + v[6] + vSquared[6];
        R[7] = 0 + v[7] + vSquared[7];
        R[8] = 1 + v[8] + vSquared[8];
    } else {
        // Identity Matrix
        R[0] = 1;
        R[1] = 0;
        R[2] = 0;
        R[3] = 0;
        R[4] = 1;
        R[5] = 0;
        R[6] = 0;
        R[7] = 0;
        R[8] = 1;
    }
    
    delete[] xProd;
    // Random number generator on [0,1]
    std::uniform_real_distribution<double> thetaDist(0.0, 2.0 * M_PI);
    std::uniform_real_distribution<double> distribution(0.0, 1.0);
    double thetaRandom = thetaDist(generator);
    double y = distribution(generator);
    double V[2] = {std::cos(thetaRandom), std::sin(thetaRandom)};
    double w = 1 / kappa * std::log(std::exp(-kappa) + kappa * ck * y);
    double temp = std::sqrt(1 - (w * w));
    V[0] = temp * V[0];
    V[1] = temp * V[1];
    // Matrix multiply with R
    double *vec = new double[3];
    vec[0] = V[0] * R[0] + V[1] * R[1] + w * R[2];
    vec[1] = V[0] * R[3] + V[1] * R[4] + w * R[5];
    vec[2] = V[0] * R[6] + V[1] * R[7] + w * R[8];
    return vec;
}

/**************************************************************************/
/********** Bingham Distribution for Generating polygons Normal Vectors ***********/
/*!
 * \brief Creates and returns an x,y,z array of doubles using the Bingham distribution.
 *
 * \note Uses new[] to return an array. NEED TO USE delete[] TO FREE THE MEMORY AFTER USE.
 *
 * \param angleOne The first angle (theta/trend/dip) depending on orientationOption.
 * \param angleTwo The second angle (phi/plunge/strike) depending on orientationOption.
 * \param kappa1 First concentration parameter for the Bingham distribution.
 * \param kappa2 Second concentration parameter for the Bingham distribution.
 * \param generator Random number generator, see std C++ <random> library.
 * \return A Bingham distribution array {x, y, z}. Used for random generation of polygon normal vectors.
 */
double* binghamDistribution(double angleOne,
                            double angleTwo,
                            double kappa1,
                            double kappa2,
                            std::mt19937_64 &generator)
{
    // 1) Build the “mode” direction v1 exactly like your Fisher code:
    double v1[3];
    anglesToNormal(angleOne, angleTwo, v1);

    // 2) Compute rotation R that takes (0,0,1) → v1 (same as yours):
    double u[3] = {0,0,1};
    double *xProd = crossProduct(u, v1);
    double R[9];
    const double eps = 1e-12;
    if (!(std::abs(xProd[0])<=eps && std::abs(xProd[1])<=eps && std::abs(xProd[2])<=eps)) {
        double sinA = sqrt(xProd[0]*xProd[0] + xProd[1]*xProd[1] + xProd[2]*xProd[2]);
        double cosA = dotProduct(u, v1);
        double v[9] = {
            0,       -xProd[2],  xProd[1],
            xProd[2], 0,        -xProd[0],
           -xProd[1], xProd[0],  0
        };
        double scalar = (1.0 - cosA) / (sinA*sinA);
        // compute v² = v * v:
        double v2[9];
        for (int i=0;i<3;i++) for(int j=0;j<3;j++){
            v2[3*i+j] = v[3*i+0]*v[0*3+j] + v[3*i+1]*v[1*3+j] + v[3*i+2]*v[2*3+j];
            v2[3*i+j] *= scalar;
        }
        // R = I + v + v²
        R[0]=1+v[0]+v2[0]; R[1]=   v[1]+v2[1]; R[2]=   v[2]+v2[2];
        R[3]=   v[3]+v2[3]; R[4]=1+v[4]+v2[4]; R[5]=   v[5]+v2[5];
        R[6]=   v[6]+v2[6]; R[7]=   v[7]+v2[7]; R[8]=1+v[8]+v2[8];
    } else {
        // already aligned
        R[0]=1; R[1]=0; R[2]=0;
        R[3]=0; R[4]=1; R[5]=0;
        R[6]=0; R[7]=0; R[8]=1;
    }
    delete[] xProd;

    // 3) Rejection‐sample in the local frame:
    //    x_local ~ Uniform(S²), accept with prob ∝ exp(k1·x² + k2·y²).
    std::uniform_real_distribution<double> unif01(0.0,1.0);
    std::uniform_real_distribution<double> phiDist(0.0, 2.0*M_PI);
    // const double M = std::exp(std::max(kappa1, kappa2));
    const double M = std::exp(std::max({0.0, kappa1, kappa2}));

    double xL[3];
    while (true) {
        double z   = unif01(generator)*2.0 - 1.0;
        double phi = phiDist(generator);
        double r   = std::sqrt(1.0 - z*z);
        xL[0] = r * std::cos(phi);  // local x
        xL[1] = r * std::sin(phi);  // local y
        xL[2] = z;                  // local z

        // Bingham density up to normalizing constant
        double w = kappa1 * xL[0]*xL[0] + kappa2 * xL[1]*xL[1];

        // Valid acceptance probability in [0,1]
        if (unif01(generator) <= std::exp(w) / M)
            break;
    }

    // 4) Rotate into global frame and return
    double *vec = new double[3];
    vec[0] = R[0]*xL[0] + R[1]*xL[1] + R[2]*xL[2];
    vec[1] = R[3]*xL[0] + R[4]*xL[1] + R[5]*xL[2];
    vec[2] = R[6]*xL[0] + R[7]*xL[1] + R[8]*xL[2];
    return vec;
}

/**************************************************************************/
/******************* Returns random TRANSLATION ***************************/
/*!
 * \brief Returns a random translation vector.
 *
 * \note Uses new[] to return an array. NEED TO USE delete[] TO FREE THE MEMORY AFTER USE.
 *
 * \param generator Random number generator, see std C++ <random> library.
 * \param xMin Minimum x value for random generation.
 * \param xMax Maximum x value for random generation.
 * \param yMin Minimum y value for random generation.
 * \param yMax Maximum y value for random generation.
 * \param zMin Minimum z value for random generation.
 * \param zMax Maximum z value for random generation.
 * \return Pointer to a random translation array of three doubles {x, y, z}.
 */
double *randomTranslation(std::mt19937_64 &generator, float xMin, float xMax, float yMin, float yMax, float zMin, float zMax) {
    double *t = new double[3];
    // Setup for getting random x location
    std::uniform_real_distribution<double> distributionX (xMin, xMax);
    t[0] = distributionX(generator);
    // Setup for getting random y location
    std::uniform_real_distribution<double> distributionY (yMin, yMax);
    t[1] = distributionY(generator);
    // Setup for getting random z location
    std::uniform_real_distribution<double> distributionZ (zMin, zMax);
    t[2] = distributionZ(generator);
    return t;
}


/**************************************************************************/
/*******************  Truncated Power-Law  ********************************/
/*!
 * \brief Computes a random value following a truncated power-law distribution.
 *
 * \param randomNum Random variable between 0 and 1, sampled uniformly.
 * \param min Minimum value that can be returned by the distribution.
 * \param max Maximum value that can be returned by the distribution.
 * \param alpha Power-law exponent.
 * \return Random float adhering to the truncated power-law distribution.
 */
float truncatedPowerLaw(float randomNum, float min, float max, float alpha) {
    float temp = 1 - randomNum + (randomNum * std::pow((min / max), alpha));
    temp = min * std::pow(temp, (-1 / alpha));
    return temp;
}


/**************************************************************************/
/**********  Generates Theta Array for Generating Ellipses  ***************/
/*!
 * \brief Generates an array of theta values by integrating the differential equation as a function of arc length using RK2.
 *
 * \note Allocates memory for thetaArray using new[]; caller must delete[] when done.
 *
 * \param thetaArray [out] Reference to the output theta array used for ellipse generation.
 * \param aspectRatio Aspect ratio of the ellipse family.
 * \param nPoints Number of points for the ellipse family.
 */
void generateTheta(float * &thetaArray, float aspectRatio, int nPoints) {
    // a = x radius
    // b = y radius
    //if (nPoints < 0) {
    //   std::cout << "invalid number of points being used for ellipseFamily (negative number)" << std::endl;
    // exit(0);
    //}
    float a = 1;
    float b = aspectRatio;
    double temp1 = ((a - b) / (a + b));
    temp1 = temp1 * temp1;
    double c = M_PI * (a + b) * (1 + (3 * temp1) / (10 + std::sqrt(4 - 3 * temp1)));
    double del = c / nPoints;
    thetaArray = new float[nPoints];
    thetaArray[0] = 0;
    
    for (int i = 1; i < nPoints; i++) {
        double tmp;
        tmp = std::pow(b * std::cos(thetaArray[i - 1]), 2) + (std::pow((a * std::sin(thetaArray[i - 1])), 2));
        double f_tmp = del / std::sqrt(tmp);
        tmp = thetaArray[i - 1] + f_tmp;
        thetaArray[i] = thetaArray[i - 1] + 0.5 * del * std::pow(std::sqrt(std::pow(b * std::cos(tmp), 2) + std::pow(a * std::sin(tmp), 2)), (-1)) + 0.5 * f_tmp;
    }
}


/**************************************************************************/
/**************************************************************************/
/*!
 * \brief Comparison function for sorting floats in descending order.
 *
 * \param i First float.
 * \param j Second float.
 * \return true if i > j, false otherwise.

    Arg 1: float i
    Arg 2: float j
    Return: True if i > j
            False otherwise */
            
bool greaterThan(float i, float j) {
    return (i > j);
}