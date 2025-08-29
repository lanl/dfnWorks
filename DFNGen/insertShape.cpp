#include <iostream>
#include <random>
#include "structures.h"
#include "insertShape.h"
#include "generatingPoints.h"
#include "computationalGeometry.h"
#include "input.h"
#include "vectorFunctions.h"
#include <string>
#include "logFile.h"


/**************************************************************************/
/*****************  Generate Polygon/Fracture  ****************************/
/*!
 * \brief Generates a polygon based on a stochastic fracture shape family.
 *
 * \param shapeFam Shape family to generate fracture from.
 * \param generator Random generator, see std::mt19937_64.
 * \param distributions Distributions class, currently used only for exponential distribution.
 * \param familyIndex Index of \p shapeFam in the shapeFamilies array.
 * \param useList If true, use pre-calculated fracture radii list; if false, generate random radii each time.
 * \return A \c Poly struct representing the generated polygon/fracture.
 */
struct Poly generatePoly(struct Shape &shapeFam,
                         std::mt19937_64 &generator,
                         Distributions &distributions,
                         int familyIndex,
                         bool useList) {
    // New polygon to build
    struct Poly newPoly;
    // Initialize normal to {0,0,1}. ( All polys start on x-y plane )
    newPoly.normal[0] = 0; // x
    newPoly.normal[1] = 0; // y
    newPoly.normal[2] = 1; // z
    // Assign number of nodes
    newPoly.numberOfNodes = shapeFam.numPoints;
    newPoly.vertices = new double[3 * newPoly.numberOfNodes]; // numPoints * {x,y,z}
    // Assign family number (index of array)
    newPoly.familyNum = familyIndex;
    
    // Switch based on distribution type
    switch (shapeFam.distributionType) {
    case 1: { // Lognormal
        double radius;
        int count = 1;
        
        if (shapeFam.radiiIdx >= shapeFam.radiiList.size() || !useList) {
            // If out of radii from list, insert random radius
            std::lognormal_distribution<double> logDistribution(shapeFam.mean, shapeFam.sd);
            
            do {
                radius = logDistribution(generator);
                
                if (count % 1000 == 0) {
                    std::string logString = "Warning: Lognormal distribution for " 
                        + shapeType(shapeFam) 
                        + " family " 
                        + to_string(getFamilyNumber(familyIndex, shapeFam.shapeFamily)) 
                        + " unable to generate fracture radius within parameters after " 
                        + to_string(count) + " tries.\n";
                    logger.writeLogFile(WARNING, logString);
                    logString = "Consider adjusting the lognormal parameters for this family in the input file.\n";
                    logger.writeLogFile(WARNING, logString);
                    break;
                }
                
                count++;
            } while (radius < h || radius < shapeFam.logMin || radius > shapeFam.logMax);
        } else {
            // Insert radius from list
            radius = shapeFam.radiiList[shapeFam.radiiIdx++];
        }
        
        if (shapeFam.shapeFamily == 1) { // Rectangle
            initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
        } else { // Ellipse
            initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        break;
    }
    
    case 2: { // Truncated power-law
        double radius;
        
        if (shapeFam.radiiIdx >= shapeFam.radiiList.size() || !useList) {
            std::uniform_real_distribution<double> uniformDist(0.0, 1.0);
            radius = truncatedPowerLaw(uniformDist(generator),
                                       shapeFam.min,
                                       shapeFam.max,
                                       shapeFam.alpha);
        } else {
            radius = shapeFam.radiiList[shapeFam.radiiIdx++];
        }
        
        if (shapeFam.shapeFamily == 1) {
            initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
        } else {
            initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        break;
    }
    
    case 3: { // Exponential
        double radius;
        int count = 1;
        
        if (shapeFam.radiiIdx >= shapeFam.radiiList.size() || !useList) {
            do {
                radius = distributions.expDist->getValue(shapeFam.expLambda,
                                                         shapeFam.minDistInput,
                                                         shapeFam.maxDistInput);
                
                if (count % 1000 == 0) {
                    std::string logString = "WARNING: Exponential distribution for " 
                        + shapeType(shapeFam) 
                        + " family " 
                        + to_string(getFamilyNumber(familyIndex, shapeFam.shapeFamily)) 
                        + " unable to generate fracture radius within parameters after " 
                        + to_string(count) + " tries.\n";
                    logger.writeLogFile(WARNING, logString);
                    logString = "Consider adjusting the exponential parameters for this family in the input file.\n";
                    logger.writeLogFile(WARNING, logString);
                    break;
                }
                
                count++;
            } while (radius < h || radius < shapeFam.expMin || radius > shapeFam.expMax);
        } else {
            radius = shapeFam.radiiList[shapeFam.radiiIdx++];
        }
        
        if (shapeFam.shapeFamily == 1) {
            initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
        } else {
            initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        break;
    }
    
    case 4: { // Constant
        if (shapeFam.shapeFamily == 1) {
            initializeRectVertices(newPoly, shapeFam.constRadi, shapeFam.aspectRatio);
        } else {
            initializeEllVertices(newPoly, shapeFam.constRadi, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        break;
    }
    }
    
    double beta;
    if (shapeFam.betaDistribution == 0) {
        std::uniform_real_distribution<double> uniformDist(0, 2 * M_PI);
        beta = uniformDist(generator);
    } else {
        beta = shapeFam.beta;
    }
    
    applyRotation2D(newPoly, beta);
    
    double *norm = nullptr;
    double mag = 0.0;

    if (shapeFam.orientation_distribution == "bingham") {
        norm = binghamDistribution(shapeFam.angleOne,
                                   shapeFam.angleTwo,
                                   shapeFam.kappa,
                                   shapeFam.kappa2,
                                   generator);
    } else {
        norm = fisherDistribution(shapeFam.angleOne,
                                  shapeFam.angleTwo,
                                  shapeFam.kappa,
                                  generator);
    }

    mag = magnitude(norm[0], norm[1], norm[2]);
    if (mag < 1 - eps || mag > 1 + eps) {
        normalize(norm);
    }

    applyRotation3D(newPoly, norm);
    newPoly.normal[0] = norm[0];
    newPoly.normal[1] = norm[1];
    newPoly.normal[2] = norm[2];
    delete[] norm;

    double *t;
    if (shapeFam.layer == 0 && shapeFam.region == 0) {
        t = randomTranslation(generator,
                              (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2,
                              (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2,
                              (-domainSize[2] - domainSizeIncrease[2]) / 2,
                              (domainSize[2] + domainSizeIncrease[2]) / 2);
    } else if (shapeFam.layer > 0 && shapeFam.region == 0) {
        int layerIdx = (shapeFam.layer - 1) * 2;
        t = randomTranslation(generator,
                              (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2,
                              (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2,
                              layers[layerIdx],
                              layers[layerIdx + 1]);
    } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
        int regionIdx = (shapeFam.region - 1) * 6;
        t = randomTranslation(generator,
                              regions[regionIdx],
                              regions[regionIdx + 1],
                              regions[regionIdx + 2],
                              regions[regionIdx + 3],
                              regions[regionIdx + 4],
                              regions[regionIdx + 5]);
    } else {
        t = randomTranslation(generator, -1, 1, -1, 1, -1, 1);
        std::string logString = "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
        logger.writeLogFile(ERROR, logString);
        exit(1);
    }

    translate(newPoly, t);
    delete[] t;
    return newPoly;
}


/**************************************************************************/
/*************  Generate Polygon/Fracture With Given Radius  **************/
/*!
 * \brief Similar to generatePoly(), but uses a provided radius.
 *
 * \param radius Radius for the polygon.
 * \param shapeFam Shape family to generate fracture from.
 * \param generator Random generator, see std::mt19937_64.
 * \param distributions Distributions class, currently used only for exponential distribution.
 * \param familyIndex Index of \p shapeFam in the shapeFamilies array.
 * \return A \c Poly struct representing the generated polygon/fracture with the given radius.
 */
struct Poly generatePoly_withRadius(double radius,
                                    struct Shape &shapeFam,
                                    std::mt19937_64 &generator,
                                    Distributions &distributions,
                                    int familyIndex) {
    // New polygon to build
    struct Poly newPoly;
    newPoly.normal[0] = 0;
    newPoly.normal[1] = 0;
    newPoly.normal[2] = 1;
    newPoly.numberOfNodes = shapeFam.numPoints;
    newPoly.vertices = new double[3 * newPoly.numberOfNodes];
    newPoly.familyNum = familyIndex;
    
    if (shapeFam.shapeFamily == 1) {
        initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
    } else {
        initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
    }
    
    double beta;
    if (shapeFam.betaDistribution == 0) {
        std::uniform_real_distribution<double> uniformDist(0, 2 * M_PI);
        beta = uniformDist(generator);
    } else {
        beta = shapeFam.beta;
    }
    applyRotation2D(newPoly, beta);

    double *norm = fisherDistribution(shapeFam.angleOne,
                                      shapeFam.angleTwo,
                                      shapeFam.kappa,
                                      generator);
    double mag = magnitude(norm[0], norm[1], norm[2]);
    if (mag < 1 - eps || mag > 1 + eps) {
        normalize(norm);
    }
    applyRotation3D(newPoly, norm);
    newPoly.normal[0] = norm[0];
    newPoly.normal[1] = norm[1];
    newPoly.normal[2] = norm[2];
    delete[] norm;

    double *t;
    if (shapeFam.layer == 0 && shapeFam.region == 0) {
        t = randomTranslation(generator,
                              (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2,
                              (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2,
                              (-domainSize[2] - domainSizeIncrease[2]) / 2,
                              (domainSize[2] + domainSizeIncrease[2]) / 2);
    } else if (shapeFam.layer > 0 && shapeFam.region == 0) {
        int layerIdx = (shapeFam.layer - 1) * 2;
        t = randomTranslation(generator,
                              (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2,
                              (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2,
                              layers[layerIdx],
                              layers[layerIdx + 1]);
    } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
        int regionIdx = (shapeFam.region - 1) * 6;
        t = randomTranslation(generator,
                              regions[regionIdx],
                              regions[regionIdx + 1],
                              regions[regionIdx + 2],
                              regions[regionIdx + 3],
                              regions[regionIdx + 4],
                              regions[regionIdx + 5]);
    } else {
        std::string logString = "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
        logger.writeLogFile(ERROR, logString);
        exit(1);
    }
    translate(newPoly, t);
    delete[] t;
    return newPoly;
}


/**************************************************************************/
/**************  Initialize Rectangular Vertices  *****************/
/*!
 * \brief Initializes vertices for a rectangular polygon using radius and aspect ratio.
 *
 * \param newPoly Polygon to initialize vertices for.
 * \param radius Half the rectangle's length.
 * \param aspectRatio Ratio of y-radius to x-radius.
 */
void initializeRectVertices(struct Poly &newPoly, float radius, float aspectRatio) {
    double x = radius;
    double y = radius * aspectRatio;
    newPoly.xradius = x;
    newPoly.yradius = y;
    newPoly.aspectRatio = aspectRatio;
    newPoly.vertices[0] = x;
    newPoly.vertices[1] = y;
    newPoly.vertices[2] = 0;
    newPoly.vertices[3] = -x;
    newPoly.vertices[4] = y;
    newPoly.vertices[5] = 0;
    newPoly.vertices[6] = -x;
    newPoly.vertices[7] = -y;
    newPoly.vertices[8] = 0;
    newPoly.vertices[9] = x;
    newPoly.vertices[10] = -y;
    newPoly.vertices[11] = 0;
}


/**************************************************************************/
/************* Initialize Ellipse Vertices **********************/
/*!
 * \brief Initializes vertices for an elliptical polygon on the x-y plane.
 *
 * \param newPoly Polygon to initialize vertices for.
 * \param radius x-radius of the ellipse.
 * \param aspectRatio y-radius factor relative to x-radius.
 * \param thetaList Array of theta values for each vertex.
 * \param numPoints Number of points (vertices) in the ellipse.
 */
void initializeEllVertices(struct Poly &newPoly,
                           float radius,
                           float aspectRatio,
                           float *thetaList,
                           int numPoints) {
    newPoly.xradius = radius;
    newPoly.yradius = radius * aspectRatio;
    newPoly.aspectRatio = aspectRatio;
    
    for (int i = 0; i < numPoints; i++) {
        int idx = i * 3;
        newPoly.vertices[idx]     = radius * std::cos(thetaList[i]);
        newPoly.vertices[idx + 1] = radius * aspectRatio * std::sin(thetaList[i]);
        newPoly.vertices[idx + 2] = 0;
    }
}


/**************************************************************************/
/********************  Retranslate Polygon  ***************************/
/*!
 * \brief Re-translates a polygon: either moves it randomly or rebuilds if truncated.
 *
 * \param newPoly Polygon to re-translate.
 * \param shapeFam Shape family struct which \p newPoly belongs to.
 * \param generator Random number generator for translation.
 */
void reTranslatePoly(struct Poly &newPoly,
                     struct Shape &shapeFam,
                     std::mt19937_64 &generator) {
    if (newPoly.truncated == 0) {
        newPoly.groupNum = 0;
        newPoly.intersectionIndex.clear();
        for (int i = 0; i < newPoly.numberOfNodes; i++) {
            int idx = 3 * i;
            newPoly.vertices[idx]     -= newPoly.translation[0];
            newPoly.vertices[idx + 1] -= newPoly.translation[1];
            newPoly.vertices[idx + 2] -= newPoly.translation[2];
        }
        
        double *t;
        if (shapeFam.layer == 0 && shapeFam.region == 0) {
            t = randomTranslation(generator,
                                  (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2,
                                  (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2,
                                  (-domainSize[2] - domainSizeIncrease[2]) / 2,
                                  (domainSize[2] + domainSizeIncrease[2]) / 2);
        } else if (shapeFam.layer > 0 && shapeFam.region == 0) {
            int layerIdx = (shapeFam.layer - 1) * 2;
            t = randomTranslation(generator,
                                  (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2,
                                  (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2,
                                  layers[layerIdx],
                                  layers[layerIdx + 1]);
        } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
            int regionIdx = (shapeFam.region - 1) * 6;
            t = randomTranslation(generator,
                                  regions[regionIdx],
                                  regions[regionIdx + 1],
                                  regions[regionIdx + 2],
                                  regions[regionIdx + 3],
                                  regions[regionIdx + 4],
                                  regions[regionIdx + 5]);
        } else {
            t = randomTranslation(generator, -1, 1, -1, 1, -1, 1);
            std::string logString = "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
            logger.writeLogFile(ERROR, logString);
            exit(1);
        }
        translate(newPoly, t);
        delete[] t;
    } else {
        delete[] newPoly.vertices;
        newPoly.vertices = new double[shapeFam.numPoints * 3];
        for (int f = 0; f < 6; f++) newPoly.faces[f] = 0;
        newPoly.truncated = 0;
        newPoly.groupNum = 0;
        newPoly.intersectionIndex.clear();
        newPoly.numberOfNodes = shapeFam.numPoints;
        
        if (shapeFam.shapeFamily == 1) {
            newPoly.vertices[0]  = newPoly.xradius;
            newPoly.vertices[1]  = newPoly.yradius;
            newPoly.vertices[2]  = 0;
            newPoly.vertices[3]  = -newPoly.xradius;
            newPoly.vertices[4]  = newPoly.yradius;
            newPoly.vertices[5]  = 0;
            newPoly.vertices[6]  = -newPoly.xradius;
            newPoly.vertices[7]  = -newPoly.yradius;
            newPoly.vertices[8]  = 0;
            newPoly.vertices[9]  = newPoly.xradius;
            newPoly.vertices[10] = -newPoly.yradius;
            newPoly.vertices[11] = 0;
        } else {
            initializeEllVertices(newPoly, newPoly.xradius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        
        double normalB[3] = {newPoly.normal[0], newPoly.normal[1], newPoly.normal[2]};
        newPoly.normal[0] = 0;
        newPoly.normal[1] = 0;
        newPoly.normal[2] = 1;
        double beta;
        if (shapeFam.betaDistribution == 0) {
            std::uniform_real_distribution<double> uniformDist(0, 2 * M_PI);
            beta = uniformDist(generator);
        } else {
            beta = shapeFam.beta;
        }
        applyRotation2D(newPoly, beta);
        applyRotation3D(newPoly, normalB);
        newPoly.normal[0] = normalB[0];
        newPoly.normal[1] = normalB[1];
        newPoly.normal[2] = normalB[2];
        
        double *t;
        if (shapeFam.layer == 0 && shapeFam.region == 0) {
            t = randomTranslation(generator,
                                  (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2,
                                  (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2,
                                  (-domainSize[2] - domainSizeIncrease[2]) / 2,
                                  (domainSize[2] + domainSizeIncrease[2]) / 2);
        } else if (shapeFam.layer > 0 && shapeFam.region == 0) {
            int layerIdx = (shapeFam.layer - 1) * 2;
            t = randomTranslation(generator,
                                  (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2,
                                  (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2,
                                  layers[layerIdx],
                                  layers[layerIdx + 1]);
        } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
            int regionIdx = (shapeFam.region - 1) * 6;
            t = randomTranslation(generator,
                                  regions[regionIdx],
                                  regions[regionIdx + 1],
                                  regions[regionIdx + 2],
                                  regions[regionIdx + 3],
                                  regions[regionIdx + 4],
                                  regions[regionIdx + 5]);
        } else {
            t = randomTranslation(generator, -1, 1, -1, 1, -1, 1);
            std::string logString = "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
            logger.writeLogFile(ERROR, logString);
            exit(1);
        }
        translate(newPoly, t);
        delete[] t;
    }
}


/**************************************************************************/
/*************  Check if Target P32 Has Been Met  *********************/
/*!
 * \brief Checks if P32 intensity targets have been met for all families.
 *
 * \param size Number of families (length of p32Status array).
 * \return \c true if all entries in p32Status are 1; \c false otherwise.
 */
bool p32Complete(int size) {
    for (int i = 0; i < size; i++) {
        if (p32Status[i] == 0) {
            return false;
        }
    }
    return true;
}


/***************************************************************************/
/**********************  Print Rejection Reason  ****************************/
/*!
 * \brief Prints fracture rejection reasons based on reject code.
 *
 * \param rejectCode Integer code indicating the reason for rejection.
 * \param newPoly The \c Poly struct that was rejected.
 */
void printRejectReason(int rejectCode, struct Poly newPoly) {
    std::string logString;
    
    if (newPoly.familyNum >= 0) {
        logString = "Attempted fracture from family " + to_string(newPoly.familyNum) + " was rejected:\n";
        logger.writeLogFile(ERROR, logString);
    }
    
    switch (rejectCode) {
    case -2:
        logString = "rejectCode = -2: Intersection of length < h.\n";
        break;
    case -1:
        logString = "rejectCode = -1: Fracture too close to a node.\n";
        break;
    case -6:
        logString = "rejectCode = -6: Fracture too close to another fracture's edge.\n";
        break;
    case -7:
        logString = "rejectCode = -7: Fractures intersecting on same plane.\n";
        break;
    case -10:
        logString = "rejectCode = -10: Triple intersection turned off in input file.\n";
        break;
    case -11:
        logString = "rejectCode = -11: Intersection too close to previous intersection.\n";
        break;
    case -12:
        logString = "rejectCode = -12: Triple intersection angle too small.\n";
        break;
    case -13:
        logString = "rejectCode = -13: Triple intersection point too close to endpoint.\n";
        break;
    case -14:
        logString = "rejectCode = -14: Triple intersection point too close to another triple intersection point.\n";
        break;
    default:
        logString = "rejectCode = " + to_string(rejectCode) + "\n";
        break;
    }
    logger.writeLogFile(ERROR, logString);
}


/******************************************************************/
/*********************  Get Family Number  *************************/
/*!
 * \brief Converts global family index into a local family number for user.
 *
 * \param familyIndex Index in the shapeFamilies array.
 * \param familyShape Shape identifier: 0 = Ellipse, 1 = Rectangle.
 * \return Local (1-based) family number within its shape category.
 */
int getFamilyNumber(int familyIndex, int familyShape) {
    if (familyShape != 0) {
        return familyIndex - nFamEll + 1;
    } else {
        return familyIndex + 1;
    }
}


/******************************************************************/
/********************  Print Shape Type  **************************/
/*!
 * \brief Returns the shape family type as a string.
 *
 * \param shapeFam Shape family struct.
 * \return "Ellipse" if \p shapeFam.shapeFamily == 0, otherwise "Rectangular".
 */
std::string shapeType(struct Shape &shapeFam) {
    if (shapeFam.shapeFamily == 0) {
        return "Ellipse";
    } else {
        return "Rectangular";
    }
}


/******************************************************************/
/************  Get Max Fracture Radius From Family  ****************/
/*!
 * \brief Returns the largest fracture radius defined by the user for a shape family.
 *
 * \param shapeFam Shape family struct.
 * \return Maximum radius (logMax, max, expMax, or constRadi) based on distributionType.
 */
double getLargestFractureRadius(Shape &shapeFam) {
    switch (shapeFam.distributionType) {
    case 1: // Log-normal
        return shapeFam.logMax;
    case 2: // Power-law
        return shapeFam.max;
    case 3: // Exponential
        return shapeFam.expMax;
    default: // Constant
        return shapeFam.constRadi;
    }
}