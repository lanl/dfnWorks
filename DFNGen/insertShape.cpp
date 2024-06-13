#include <iostream>
#include <random>
#include "structures.h"
#include "insertShape.h"
#include "generatingPoints.h"
#include "computationalGeometry.h"
#include "input.h"
#include "vectorFunctions.h"
#include <string>


/**************************************************************************/
/*****************  Generate Polygon/Fracture  ****************************/
/*! Generates a polygon based on a stochastic fracture shape family
    NOTE: Function does not create bouding box. The bouding box has to be
          created after fracture truncation
    Arg 1: Shape family to generate fracture from
    Arg 2: Random generator, see std <random> c++ library
    Arg 3: Distributions class, currently used only for exponential dist.
    Arg 4: Index of 'shapeFam' (arg 1) in the shapeFamilies array in main()
    Arg 5: True - Use pre-calculated fracture radii list to pull radii from
           False - Generate random radii every time (used in dryRun()
                   which estimates number of fractures needed when using
                   p32 option and generates the radii lists)
    Return: Random polygon/fracture based from 'shapeFam' */
struct Poly generatePoly(struct Shape &shapeFam, std::mt19937_64 &generator, Distributions &distributions, int familyIndex, bool useList) {
    // New polygon to build
    struct Poly newPoly;
    // Initialize normal to {0,0,1}. ( All polys start on x-y plane )
    newPoly.normal[0] = 0; // x
    newPoly.normal[1] = 0; // y
    newPoly.normal[2] =    1; // z
    // Assign number of nodes
    newPoly.numberOfNodes = shapeFam.numPoints;
    newPoly.vertices = new double[3 * newPoly.numberOfNodes]; //numPoints*{x,y,z}
    // Assign family number (index of array)
    newPoly.familyNum = familyIndex;
    
    // Switch based on distribution type
    switch (shapeFam.distributionType) {
    case 1: { // Lognormal
        double radius;
        int count = 1;
        
        if (shapeFam.radiiIdx >= shapeFam.radiiList.size() || useList == false) {
            // If out of radii from list, insert random radius
            std::lognormal_distribution<double> logDistribution(shapeFam.mean, shapeFam.sd);
            
            do {
                radius = logDistribution(generator);
                
                if (count % 1000 == 0) {
                    std::cout << "\nWarning: Lognormal distribution for " << shapeType(shapeFam)
                              << " family " << getFamilyNumber(familyIndex, shapeFam.shapeFamily)
                              << " has been  unable to generate a fracture with radius within set parameters after "
                              << count << " consecutive tries.\n";
                    std::cout << "Consider adjusting the lognormal paramerters for this family in the input file.\n";
                    break;
                }
                
                count++;
            } while (radius < h || radius < shapeFam.logMin || radius > shapeFam.logMax);
        } else { // Insert radius from list
            radius = shapeFam.radiiList[shapeFam.radiiIdx];
            shapeFam.radiiIdx++;
        }
        
        if (shapeFam.shapeFamily == 1) { // Rectangle
            // Initialize rectangles vertices using lognormal dist.
            initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
        } else { // Ellipse
            initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        
        break;
    }
    
    case 2: { // Truncated power-law
        double radius;
        
        if (shapeFam.radiiIdx >= shapeFam.radiiList.size() || useList == false) {
            // If out of radii from list, generate random radius
            std::uniform_real_distribution<double> uniformDist(0.0, 1.0);
            radius = truncatedPowerLaw( uniformDist(generator), shapeFam.min, shapeFam.max, shapeFam.alpha);
        } else { // Pull radius from list
            radius = shapeFam.radiiList[shapeFam.radiiIdx];
            shapeFam.radiiIdx++;
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
        
        if (shapeFam.radiiIdx >= shapeFam.radiiList.size() || useList == false) {
            // If out of radii from list, generate random radius
            do {
                radius = distributions.expDist->getValue(shapeFam.expLambda, shapeFam.minDistInput, shapeFam.maxDistInput);
                
                if (count % 1000 == 0) {
                    std::cout << "\nWARNING: Exponential distribution for " << shapeType(shapeFam)
                              << " family " << getFamilyNumber(familyIndex, shapeFam.shapeFamily)
                              << " has been  unable to generate a fracture with radius within set parameters after "
                              << count << " consecutive tries.\n";
                    std::cout << "Consider adjusting the exponential parameters for this family in the input file.\n";
                    break;
                }
                
                count++;
            } while (radius < h || radius < shapeFam.expMin || radius > shapeFam.expMax);
        } else { // Insert radius from list
            radius = shapeFam.radiiList[shapeFam.radiiIdx];
            shapeFam.radiiIdx++;
        }
        
        if (shapeFam.shapeFamily == 1) { // Rectangle
            // Initialize rectangles vertices using exp. dist.
            initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
        } else { // Ellipse
            initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        
        break;
    }
    
    case 4: { // Constant
        if (shapeFam.shapeFamily == 1) { // Rectangle
            // Initialize rectangles vertices
            initializeRectVertices(newPoly, shapeFam.constRadi, shapeFam.aspectRatio);
        } else { // Ellipse
            initializeEllVertices(newPoly, shapeFam.constRadi, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        
        break;
    }
    }
    
    double beta;
    
    // Initialize beta based on distrubution type: 0 = unifrom on [0,2PI], 1 = constant
    if (shapeFam.betaDistribution == 0) { //uniform distribution
        std::uniform_real_distribution<double> uniformDist (0, 2 * M_PI);
        beta = uniformDist(generator);
    } else {
        beta = shapeFam.beta;
    }
    
    // Apply 2d rotation matrix, twist around origin
    // Assumes polygon on x-y plane
    // Angle must be in rad
    applyRotation2D(newPoly, beta);
    // Fisher distribution / get normal vector
    double *norm = fisherDistribution(shapeFam.angleOne, shapeFam.angleTwo, shapeFam.kappa, generator);
    double mag = magnitude(norm[0], norm[1], norm[2]);
    
    if (mag < 1 - eps || mag > 1 + eps) {
        normalize(norm); // Ensure norm is normalized
    }
    
    applyRotation3D(newPoly, norm); // Rotate vertices to norm (new normal)
    // Save newPoly's new normal vector
    newPoly.normal[0] = norm[0];
    newPoly.normal[1] = norm[1];
    newPoly.normal[2] = norm[2];
    delete[] norm;
    double *t;
    
    // HERE
    if (shapeFam.layer == 0 && shapeFam.region == 0) { // The family layer is the whole domain
        t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2, (-domainSize[2] - domainSizeIncrease[2]) / 2,
                              (domainSize[2] + domainSizeIncrease[2]) / 2);
    } else if (shapeFam.layer > 0 && shapeFam.region == 0) { // Family belongs to a certain layer, shapeFam.layer is > zero
        // Layers start at 1, but the array of layers start at 0, hence
        // the subtraction by 1
        // Layer 0 is reservered to be the entire domain
        int layerIdx = (shapeFam.layer - 1) * 2;
        // Layers only apply to z coordinates
        t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2, layers[layerIdx], layers[layerIdx + 1]);
    } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
        int regionIdx = (shapeFam.region - 1) * 6;
        // Layers only apply to z coordinates
        t = randomTranslation(generator, regions[regionIdx], regions[regionIdx + 1], regions[regionIdx + 2], regions[regionIdx + 3], regions[regionIdx + 4], regions[regionIdx + 5]);
        //std::cout << "Translation "<< t[0] << " " << t[1] << " " << t[2]<<"\n";
    } else {
        t = randomTranslation(generator, -1, 1, -1, 1, -1, 1);
        std::cout << "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
        exit(1);
    }
    
    // Translate - will also set translation vector in poly structure
    translate(newPoly, t);
    delete[] t;
    return newPoly;
}


/**************************************************************************/
/*************  Generate Polygon/Fracture With Given Radius  **************/
/*! Similar to generatePoly() except the radius is passed to the function.
    Generates a polygon
    Shape (ell or rect) still comes from the shapes' familiy
    NOTE: Function does not create bouding box. The bouding box has to be
          created after fracture truncation
    Arg 1: Radius for polygon
    Arg 2: Shape family to generate fracture from
    Arg 3: Random generator, see std <random> c++ library
    Arg 4: Distributions class, currently used only for exponential dist.
    Arg 5: Index of 'shapeFam' (arg 1) in the shapeFamilies array in main()
    Return: Polygond with radius passed in arg 1 and shape based on 'shapeFam' */
struct Poly generatePoly_withRadius(double radius, struct Shape &shapeFam, std::mt19937_64 &generator, Distributions &distributions, int familyIndex) {
    // New polygon to build
    struct Poly newPoly;
    // Initialize normal to {0,0,1}. ( All polys start on x-y plane )
    newPoly.normal[0] = 0; //x
    newPoly.normal[1] = 0; //y
    newPoly.normal[2] = 1; //z
    // Assign number of nodes
    newPoly.numberOfNodes = shapeFam.numPoints;
    newPoly.vertices = new double[3 * newPoly.numberOfNodes]; //numPoints*{x,y,z}
    // Assign family number (index of shapeFam array)
    newPoly.familyNum = familyIndex;
    
    // TODO: Convert any degrees to rad
    // in readInput() to avoid continuous checking
    
    if (shapeFam.shapeFamily == 1) { // If rectangle shape
        // Initialize rectangles vertices
        initializeRectVertices(newPoly, radius, shapeFam.aspectRatio);
    } else { // Ellipse
        initializeEllVertices(newPoly, radius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
    }
    
    double beta;
    
    // Initialize beta based on distrubution type: 0 = unifrom on [0,2PI], 1 = constant
    if (shapeFam.betaDistribution == 0) { // Uniform distribution
        std::uniform_real_distribution<double> uniformDist (0, 2 * M_PI);
        beta = uniformDist(generator);
    } else {
        beta = shapeFam.beta;
    }
    
    // Apply 2d rotation matrix, twist around origin
    // assumes polygon on x-y plane
    // Angle must be in rad
    applyRotation2D(newPoly, beta);
    // Fisher distribution / get normal vector
    double *norm = fisherDistribution(shapeFam.angleOne, shapeFam.angleTwo, shapeFam.kappa, generator);
    double mag = magnitude(norm[0], norm[1], norm[2]);
    
    if (mag < 1 - eps || mag > 1 + eps) {
        normalize(norm); //ensure norm is normalized
    }
    
    applyRotation3D(newPoly, norm); // Rotate vertices to norm (new normal)
    // Save newPoly's new normal vector
    newPoly.normal[0] = norm[0];
    newPoly.normal[1] = norm[1];
    newPoly.normal[2] = norm[2];
    delete[] norm;
    double *t;
    
    if (shapeFam.layer == 0 && shapeFam.region == 0) { // The family layer is the whole domain
        t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2, (-domainSize[2] - domainSizeIncrease[2]) / 2,
                              (domainSize[2] + domainSizeIncrease[2]) / 2);
    } else if (shapeFam.layer > 0 && shapeFam.region == 0) { // Family belongs to a certain layer, shapeFam.layer is > zero
        // Layers start at 1, but the array of layers start at 0, hence
        // the subtraction by 1
        // Layer 0 is reservered to be the entire domain
        int layerIdx = (shapeFam.layer - 1) * 2;
        // Layers only apply to z coordinates
        t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                              (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                              (domainSize[1] + domainSizeIncrease[1]) / 2, layers[layerIdx], layers[layerIdx + 1]);
    } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
        int regionIdx = (shapeFam.region - 1) * 6;
        // Layers only apply to z coordinates
        t = randomTranslation(generator, regions[regionIdx], regions[regionIdx + 1], regions[regionIdx + 2], regions[regionIdx + 3], regions[regionIdx + 4], regions[regionIdx + 5]);
    } else {
        std::cout << "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
        exit(1);
    }
    
    // Translate - will also set translation vector in poly structure
    translate(newPoly, t);
    delete[] t;
    return newPoly;
}


/*******************************************************************************/
/******************** Aperture  assignment function ****************************/
/*! Assigns aperture based in user input option to fractures/polygons
    Function is used at end of fracture insertion in main()

    Arg 1: Polyogon to assign aperture to
    Arg 2: Random generator, see c++ std library: <random>

    Options:
    1) meanAperture and stdAperture for using LogNormal distribution.
    2) apertureFromTransmissivity, first transmissivity is defined, and then,
       using a cubic law, the aperture is calculated;
    3) constantAperture, all fractures, regardless of their size, will have
       the same aperture value;
    4) lengthCorrelatedAperture, aperture is defined as a function of fracture size  */

// water density = 997.7
// gravity = 9.8
// water Visc = 8.9e-4
// constant scalar = waterDesnsity*gravity/waterVisc = 48.3868
#define _CONSTSCALAR 1.1e7
//#define _CONSTSCALAR 48.3868


// void assignAperture(struct Poly &newPoly, std::mt19937_64 &generator) {
//     // Most aperture variables are currently declared globaly
//     switch (aperture) {
//     case 1: { // Lognormal
//         std::lognormal_distribution<double> logDistribution(meanAperture, stdAperture);
//         newPoly.aperture = logDistribution(generator);
//         break;
//     }

//     case 2: {
//         /*  Transmissivity is calculated as transmissivity = F*R^k,
//             where F is a first element in aperturefromTransmissivity,
//             k is a second element and R is a mean radius of a polygon.
//             Aperture is calculated according to cubic law as
//             b=(transmissivity*12)^1/3  */
//         float radiAvg = (newPoly.xradius + newPoly.yradius) * .5;
//         double F = apertureFromTransmissivity[0];
//         double k = apertureFromTransmissivity[1];
//         double transmissivity = F * std::pow(radiAvg, k);
//         newPoly.aperture = std::cbrt((transmissivity * 12 / _CONSTSCALAR)); //cube root
//         break;
//     }

//     case 3: {
//         newPoly.aperture = constantAperture;
//         break;
//     }

//     case 4: {
//         double radiAvg = (newPoly.xradius + newPoly.yradius) * .5;
//         double apertureMeanF = lengthCorrelatedAperture[0];
//         double b = lengthCorrelatedAperture[1];
//         newPoly.aperture = apertureMeanF * std::pow(radiAvg, b);
//         break;
//     }
//     }
// }


/**************************************************************************/
/**************** permiability  assignment function ***********************/
/*! Assigns permiability using user's input option
    Runs once at end of fracture insertion for all accepted fractures
    Options:
       0 - Permeability of each fracture is a function of fracture aperture,
           given by k=(b^2)/12, where b is an aperture and k is permeability
       1 - Constant permeabilty for all fractures
    Arg 1: Polygon/fracture to assign permiability to  */
// void assignPermeability(struct Poly &newPoly) {
//     // Aperture option is declared globaly
//     if (permOption == 0) { // Perm as function of aperture
//         newPoly.permeability = (newPoly.aperture * newPoly.aperture) / 12;
//     } else { // Permoption is equal to 1
//         newPoly.permeability = constantPermeability;
//     }
// }

/**************  Initialize Rectangular Vertices  *****************/
/*! Initializes vertices for rectangular poly using radius (1/2 x length)
    and aspcet ratio. (xradius = radius, yradius = radius * aspectRatio)
    Poly will be on x-y plane
    Arg 1: Polygon to initialize vertices
    Arg 2: Radius (1/2 x dimension length)
    Arg 3: Aspect ratio */
void initializeRectVertices(struct Poly &newPoly, float radius, float aspectRatio) {
    double x = radius;
    double y = radius * aspectRatio;
    newPoly.xradius = x;
    newPoly.yradius = y;
    newPoly.aspectRatio = aspectRatio;
    // Initialize vertices
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


/****************************************************************/
/************* Initialize Ellipse Vertices **********************/
/*! Initializes ellipse vertices on x-y plane
    Arg 1: Poly to initialize
    Arg 2: Radius (xradius = radius. yradius = radius * aspectRatio)
    Arg 3: Aspect ratio */
void initializeEllVertices(struct Poly &newPoly, float radius, float aspectRatio, float *thetaList, int numPoints) {
    newPoly.xradius = radius;
    newPoly.yradius = radius * aspectRatio;
    newPoly.aspectRatio = aspectRatio;
    
    for (int i = 0; i < numPoints; i++ ) {
        int idx = i * 3;
        newPoly.vertices[idx]   = radius * std::cos(thetaList[i]);
        newPoly.vertices[idx + 1] = radius * aspectRatio * std::sin(thetaList[i]);
        newPoly.vertices[idx + 2] = 0;
    }
}


/**********************************************************************/
/********************  Retranslate Polygon  ***************************/
/*! Re-translate poly
    Re-initializes/re-builds (if needed) polygon at origin and translates to
    new position preserving its size, shape, and normal vector
    This helps hit target distributions since we reject less
    Arg 1: Polygon
    Arg 2: Shape family structure which Polygon belongs to
    Arg 3: Random Generator */
void reTranslatePoly(struct Poly &newPoly, struct Shape &shapeFam, std::mt19937_64 &generator) {
    if (newPoly.truncated == 0) {
        // If poly isn't truncated we can skip a lot of steps such
        // as reallocating vertice memory, rotations, etc..
        newPoly.groupNum = 0; // Clear cluster group information
        newPoly.intersectionIndex.clear(); // Clear any saved intersections
        
        // Move poly back to origin
        for (int i = 0; i < newPoly.numberOfNodes; i++) {
            int idx = 3 * i;
            newPoly.vertices[idx]   -= newPoly.translation[0]; // x
            newPoly.vertices[idx + 1] -= newPoly.translation[1]; // y
            newPoly.vertices[idx + 2] -= newPoly.translation[2]; // z
        }
        
        // Translate to new position
        double *t;
        
        if (shapeFam.layer == 0 && shapeFam.region == 0) { // The family layer is the whole domain
            t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2, (-domainSize[2] - domainSizeIncrease[2]) / 2,
                                  (domainSize[2] + domainSizeIncrease[2]) / 2);
        } else if (shapeFam.layer > 0 && shapeFam.region == 0) { // Family belongs to a certain layer, shapeFam.layer is > zero
            // Layers start at 1, but the array of layers start at 0, hence
            // the subtraction by 1
            // Layer 0 is reservered to be the entire domain
            int layerIdx = (shapeFam.layer - 1) * 2;
            // Layers only apply to z coordinates
            t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2, layers[layerIdx], layers[layerIdx + 1]);
        } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
            int regionIdx = (shapeFam.region - 1) * 6;
            // Layers only apply to z coordinates
            t = randomTranslation(generator, regions[regionIdx], regions[regionIdx + 1], regions[regionIdx + 2], regions[regionIdx + 3], regions[regionIdx + 4], regions[regionIdx + 5]);
        } else {
            // you should never get here
            t = randomTranslation(generator, -1, 1, -1, 1, -1, 1);
            std::cout << "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
            exit(1);
        }
        
        // Translate - will also set translation vector in poly structure
        translate(newPoly, t);
        delete[] t;
    } else { // Poly was truncated, need to rebuild the polygon
        delete[] newPoly.vertices; // Delete truncated vertices
        newPoly.vertices = new double[shapeFam.numPoints * 3];
        // Reset boundary faces (0 means poly is no longer touching a boundary)
        newPoly.faces[0] = 0;
        newPoly.faces[1] = 0;
        newPoly.faces[2] = 0;
        newPoly.faces[3] = 0;
        newPoly.faces[4] = 0;
        newPoly.faces[5] = 0;
        newPoly.truncated = 0; // Set to 0 to mean not truncated
        newPoly.groupNum = 0;  // Clear cluster group information
        newPoly.intersectionIndex.clear(); // Clear any saved intersections
        newPoly.numberOfNodes = shapeFam.numPoints;
        
        if (shapeFam.shapeFamily == 1) { // 1 is rectanglular families. rebuild rectangle
            // Rebuild poly at origin using previous size
            newPoly.vertices[0] = newPoly.xradius;
            newPoly.vertices[1] = newPoly.yradius;
            newPoly.vertices[2] = 0;
            newPoly.vertices[3] = -newPoly.xradius;
            newPoly.vertices[4] = newPoly.yradius;
            newPoly.vertices[5] = 0;
            newPoly.vertices[6] = -newPoly.xradius;
            newPoly.vertices[7] = -newPoly.yradius;
            newPoly.vertices[8] = 0;
            newPoly.vertices[9] = newPoly.xradius;
            newPoly.vertices[10] = -newPoly.yradius;
            newPoly.vertices[11] = 0;
        } else { // Rebuild ellipse
            initializeEllVertices(newPoly, newPoly.xradius, shapeFam.aspectRatio, shapeFam.thetaList, shapeFam.numPoints);
        }
        
        // Save newPoly's previous normal vector and then reset poly normal to {0,0,1} for applyRotation3D function
        double normalB[3] = {newPoly.normal[0], newPoly.normal[1], newPoly.normal[2]};
        newPoly.normal[0] = 0; //x
        newPoly.normal[1] = 0; //y
        newPoly.normal[2] = 1; //z
        double beta;
        
        // Initialize beta based on distrubution type: 0 = unifrom on [0,2PI], 1 = constant
        if (shapeFam.betaDistribution == 0) {
            // Uniform distribution
            std::uniform_real_distribution<double> uniformDist (0, 2 * M_PI);
            beta = uniformDist(generator);
        } else { // Constant
            beta = shapeFam.beta;
        }
        
        // Apply 2d rotation matrix, twist around origin
        // Assumes polygon on x-y plane
        // Angle must be in rad
        applyRotation2D(newPoly, beta);
        // Rotates poly from {0,0,1} to normalB, NEED to save normalB to newPoly.normal afterwards
        applyRotation3D(newPoly, normalB);
        newPoly.normal[0] = normalB[0];
        newPoly.normal[1] = normalB[1];
        newPoly.normal[2] = normalB[2];
        // Translate to new position
        // Translate() will also set translation vector in poly structure
        double *t;
        
        if (shapeFam.layer == 0 && shapeFam.region == 0) { // The family layer is the whole domain
            t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2, (-domainSize[2] - domainSizeIncrease[2]) / 2,
                                  (domainSize[2] + domainSizeIncrease[2]) / 2);
        } else if (shapeFam.layer > 0 && shapeFam.region == 0) { // Family belongs to a certain layer, shapeFam.layer is > zero
            // Layers start at 1, but the array of layers start at 0, hence
            // the subtraction by 1
            // Layer 0 is reservered to be the entire domain
            int layerIdx = (shapeFam.layer - 1) * 2;
            // Layers only apply to z coordinates
            t = randomTranslation(generator, (-domainSize[0] - domainSizeIncrease[0]) / 2,
                                  (domainSize[0] + domainSizeIncrease[0]) / 2, (-domainSize[1] - domainSizeIncrease[1]) / 2,
                                  (domainSize[1] + domainSizeIncrease[1]) / 2, layers[layerIdx], layers[layerIdx + 1]);
        } else if (shapeFam.layer == 0 && shapeFam.region > 0) {
            int regionIdx = (shapeFam.region - 1) * 6;
            // Layers only apply to z coordinates
            t = randomTranslation(generator, regions[regionIdx], regions[regionIdx + 1], regions[regionIdx + 2], regions[regionIdx + 3], regions[regionIdx + 4], regions[regionIdx + 5]);
        } else {
            t = randomTranslation(generator, -1, 1, -1, 1, -1, 1);
            std::cout << "ERROR!!!\nLayer and Region both defined for this Family.\nExiting Program\n";
            exit(1);
        }
        
        translate(newPoly, t);
        delete[] t;
    }
}


/**********************************************************************/
/*************  Check if Target P32 Has Been Met  *********************/
/*! For th  P32 stopping option (see input file)
    Function checks the status of the fractures families target P32
    The 'p32Status' array is 1 to 1 with the total number of families
    When a family's P32 requirement has been met, it's corresponding
    element in 'p32Status' is set to '1'
    For example, the status for shapeFamiliy[0] is in p32Status[0].
    If p32Status[0] = 1, shapeFamily[0] has met its p32/fracture intensity target,
    else it has not and will keep inserting more fractures

    Arg 1: Size of 'p32Status' array (same size as the shapeFamilies array)
    Return: True once ALL p32 targets have been met for all families
            False otherwise */
bool p32Complete(int size) {
    // Check if p32Status array is all 1's, if not return 0
    for (int i = 0; i < size; i++) {
        if (p32Status[i] == 0) {
            return 0;
        }
    }
    
    // If function has not returned yet, array is all 1's
    return 1;
}


/***************************************************************************/
/**********************  Print Rejection Reson  ****************************/
/*! Function prints fracture rejection reasons to user based on reject code
    Currtenly only used for user defined fractures.
    Arg 1: Rejection code
    Arg 2: Poly which was rejected */
void printRejectReason(int rejectCode, struct Poly newPoly) {
    if (newPoly.familyNum >= 0 ) {
        std::cout << "\nAttempted fracture from family "
                  <<  newPoly.familyNum << " was rejected:\n";
    }
    
    switch (rejectCode) {
    case -2:
        std::cout << "\trejectCode = -2: Intersection of length < h.\n";
        break;
        
    case -1:
        std::cout << "\trejectCode = -1: Fracture too close to a node.\n";
        break;
        
    case -6:
        std::cout << "\trejectCode = -6: Fracture too close "
                  << "to another fracture's edge.\n";
        break;
        
    case -7:
        std::cout << "\trejectCode = -7: Fractures intersecting on same plane\n";
        break;
        
    case -10:
        std::cout << "\trejectCode = -10: Rejected triple intersection "
                  << "due to triple intersections being turned off in input file.\n";
        break;
        
    case -11:
        std::cout << "\trejectCode = -11: Fracture's intersection "
                  << "landed too close to a previous intersection.\n";
        break;
        
    case -12:
        std::cout << "\trejectCode = -12: Fracture created a triple "
                  << "intersection with an angle too small.\n";
        break;
        
    case -13:
        std::cout << "\trejectCode = -13: Fracture created a triple intersection "
                  << "with the triple intersection point too close to an intersection's endpoint.\n";
        break;
        
    case -14:
        std::cout << "\trejectCode = -14: Fracture created a triple intersection with "
                  << "the triple intersection point too close to another triple intersection point.\n";
        break;
        
    default:
        std::cout << "\trejectCode = " << rejectCode << "\n";
        break;
    }
}


/******************************************************************/
/*********************  Get Family Number *************************/
/*! Turns the global family number into a number the user can more
    easily understand. The shapeFamily array contains both rectangle
    and ellipse families.
    For example: If shapeFamilies array has 3 families of ellipse
    families and 3 families of rectangle families: {ell, ell, ell, rect, rect, rect}
    If we want the local family number for index 3, it will return family 1, meaning
    the first rectangular family. This function is used in conjuntion with shapeType().

    Arg 1: Family index which family belings to
           in main()'s 'shapeFamilies' array
    Arg 2: Rectangle or ellipse family
           0 - Ellipse
           1 - Rectangle */
int getFamilyNumber(int familyIndex, int familyShape) {
    if (familyShape != 0) { // if not ellipse family
        return familyIndex - nFamEll + 1;
    } else {
        return familyIndex + 1;
    }
}


/******************************************************************/
/********************  Print Shape Type  **************************/
/*! Print type of family (ellipse or rectangle)
    Arg 1: Shape family */
std::string shapeType(struct Shape &shapeFam) {
    if (shapeFam.shapeFamily == 0) {
        return "Ellipse";
    } else {
        return "Rectangular";
    }
}

/******************************************************************/
/************  Get Max Fracture Radii From Family  ****************/
/*! Returns the largest fracture radii defined by the user for
    a fracture family.
    This function is used for the 'forceLargeFractures' option
    in the input file
    Arg 1: Shape family
    Return: User's maximum radii for shapeFam (arg 1) */
double getLargestFractureRadius(Shape &shapeFam) {
    switch (shapeFam.distributionType) {
    case 1: // Log-normal
        return shapeFam.logMax;
        break;
        
    case 2: // Power-law
        return shapeFam.max;
        break;
        
    case 3: // Exponential
        return shapeFam.expMax;
        break;
        
    default: // Constant
        return shapeFam.constRadi;
        break;
    }
}


