#include <iostream>
#include <algorithm>
#include "generatingPoints.h"
#include "input.h"
#include "fractureEstimating.h"
#include "insertShape.h"
#include "mathFunctions.h"
#include "domain.h"
#include "logFile.h"

/**********************************************************************/
/****************  Sort Families Radii Lists  *************************/
/*! Uses std::sort to sort each family's radii list from largest to smallest.
    This will allow the DFN gereration to start from largest to smallest
    fractures.
    Arg 1: vector<Shape> array of stochastic fracture families */
void sortRadii(std::vector<Shape> &shapeFam) {
    for (unsigned int i = 0; i < shapeFam.size(); i++) {
        std::sort(shapeFam[i].radiiList.begin(),
                  shapeFam[i].radiiList.end(     ), greaterThan);
    }
}

/**********************************************************************/
/***  Create Radii Lists for Shape Families When Using NPoly Option ***/
/*! Estimates the number of fractures needed for each family and
    creates radii lists for each family based on their distribution.
    Arg 1: vector<Shape> array of stochastic fracture families
    Arg 2: Family probablity array ('famProb' in input file)
    Arg 3: Random number generator, see std <random> library
    Arg 4: Reference to Distributions class (used for exponential distribution) */
void generateRadiiLists_nPolyOption(std::vector<Shape> &shapeFamilies, float *famProb, std::mt19937_64 &generator, Distributions &distributions) {
    std::string logString = "Building radii lists for nPoly option...\n";
    logger.writeLogFile(INFO,  logString);
    
    if (forceLargeFractures == true) {
        for (unsigned int i = 0; i < shapeFamilies.size(); i++) {
            double radius = getLargestFractureRadius(shapeFamilies[i]);
            shapeFamilies[i].radiiList.push_back(radius);
        }
    }
    
    for (unsigned int i = 0; i < shapeFamilies.size(); i++) {
        int amountToAdd;
        
        if (forceLargeFractures == true) {
            amountToAdd = std::ceil(famProb[i] * (nPoly - shapeFamilies.size()));
        } else {
            amountToAdd = std::ceil(famProb[i] * nPoly);
        }
        
        addRadii(amountToAdd, i, shapeFamilies[i],
                 generator, distributions);
    }
    
    logString = "Building radii lists for nPoly option Complete";
    logger.writeLogFile(INFO,  logString);
}


/**********************************************************************/
/********************  Print Warining to User  ************************/
/*! This function prints a warning to the user when the random generation
    of fracture radii lenths is continuously smaller than the minimum defined
    radii allowed (defined by user in the input file)
    Arg 1: Index to the family in vecotr<Shape> array the warning is refering to
    Arg 2: Shape structure the warning is refering to */
void printGeneratingFracturesLessThanHWarning(int famIndex, Shape &shapeFam) {
    std::string logString = "WARNING: " + shapeType(shapeFam) + " Family " + to_string(getFamilyNumber(famIndex, shapeFam.shapeFamily)) + " is attepting to populate fracture radii lists, however many fractures are being generated with radii less than 3*h (Minimum radius). Consider adjusting distribution parameters.\n";
    logger.writeLogFile(INFO,  logString);
}


/**********************************************************************/
/*********  Add Percentage More Radii To Radii Lists  *****************/
/*! Function adds a percentage more radii to the fracture families
    radii lists based on each families distribution.
    This helps account for fracture rejections
    Arg 1: Percentage to increase the list by. eg .10 will add %10 more radii
    Arg 2: vector<Shape> array of stochastic fracture families
    Arg 3: Random number generator (see std <random> library)
    Arg 4: Distributions class (currently only used for exponential dist) */
void addRadiiToLists(float percent, std::vector<Shape> &shapeFamilies, std::mt19937_64 &generator, Distributions &distributions) {
    for (unsigned int i = 0; i < shapeFamilies.size(); i++) {
        int amountToAdd = std::ceil(shapeFamilies[i].radiiList.size() * percent);
        addRadii(amountToAdd, i, shapeFamilies[i], generator, distributions);
    }
}


/**********************************************************************/
/************  Add Radii To Shape Families Radii List  ****************/
/*! Adds 'amountToAdd' more radii to 'shapeFam's radii list
    Arg 1: Number of fractures to add to the list
    Arg 2: Family index to the global Shape structure array ('shapeFamilies' in main())
           which the radii are being added to
    Arg 3: The 'Shape' structure which the radii are being added to
    Arg 4: Random number generator (see std <random> library)
    Arg 5: Distributions class (currently only used for exponential dist) */
void addRadii(int amountToAdd, int famIdx, Shape &shapeFam, std::mt19937_64 &generator, Distributions &distributions) {
    int count = 0;
    double radius;
    double minRadius = 3 * h;
    std::uniform_real_distribution<double> uniformDist(0, 1);
    
    switch (shapeFam.distributionType) {
    case 1: { // Lognormal
        std::lognormal_distribution<double> logDistribution(shapeFam.mean, shapeFam.sd);
        
        for (int k = 0; k < amountToAdd; k++) {
            count = 0;
            
            do {
                radius = logDistribution(generator);
                count++;
                
                if (count % 1000 == 0) {
                    printGeneratingFracturesLessThanHWarning(famIdx, shapeFam);
                }
            } while (radius < minRadius);
            
            shapeFam.radiiList.push_back(radius);
        }
        
        break;
    }
    
    case 2: { // Truncated power-law
        for (int k = 0; k < amountToAdd; k++) {
            count = 0;
            
            do {
                radius = truncatedPowerLaw(uniformDist(generator),
                                           shapeFam.min, shapeFam.max, shapeFam.alpha);
                count++;
                
                if (count % 1000 == 0) {
                    printGeneratingFracturesLessThanHWarning(famIdx, shapeFam);
                }
            } while (radius < minRadius);
            
            shapeFam.radiiList.push_back(radius);
        }
        
        break;
    }
    
    case 3: { // Exponential
        for (int k = 0; k < amountToAdd; k++) {
            count = 0;
            
            do {
                radius = distributions.expDist->getValue(shapeFam.expLambda,
                         shapeFam.minDistInput, shapeFam.maxDistInput);
                count++;
                
                if (count % 1000 == 0) {
                    printGeneratingFracturesLessThanHWarning(famIdx, shapeFam);
                }
            } while (radius < minRadius);
            
            shapeFam.radiiList.push_back(radius);
        }
        
        break;
    }
    }
}


/**********************************************************************/
/********  Estimate Number of Fractures When P32 Option is Used  ******/
/*! Inserts fractures into domain with FRAM disabled
    Simply inserts and truncates fractures on the domain
    until reqired P32 is met.
    Used to estimate and generate radii lists for each fracture
    family.
    Arg 1: vector<Shape> array of stochastic fracture families
    Arg 2: The probabilities for each families insertion into domain
           (famProb) in input file
    Arg 3: Random number generator (see std <random> library)
    Arg 4: Distributions class (currently only used for exponential dist) */
void dryRun(std::vector<Shape> &shapeFamilies, float *shapeProb, std::mt19937_64 &generator, Distributions &distributions) {
    std::string logString = "Estimating number of fractures per family for defined fracture intensities (P32)...\n";
    logger.writeLogFile(INFO,  logString);
    float domVol = domainSize[0] * domainSize[1] * domainSize[2];
    int totalFamilies = shapeFamilies.size();
    int cdfSize = totalFamilies; // This variable shrinks along with CDF when used with fracture intensity (P32) option
    // Create a copy of the family probablity
    // Algoithms used in this function modify this array,
    // we need to keep the original in its original state
    float *famProbability = new float[totalFamilies];
    std::copy(shapeProb, shapeProb + totalFamilies, famProbability);
    // Init uniform dist on [0,1)
    std::uniform_real_distribution<double> uniformDist(0, 1);
    /******  Convert famProb to CDF  *****/
    float *CDF = createCDF(famProbability, cdfSize);
    int familyIndex; // Holds index to shape family of fracture being generated
    unsigned int forceLargeFractCount = 0;
    
    while (p32Complete(totalFamilies) == 0) {
        // Index to CDF array of current family being inserted
        int cdfIdx;
        int rejectCounter = 0;
        Poly newPoly;
        
        if ((forceLargeFractCount < shapeFamilies.size()) && forceLargeFractures == true) {
            double radius = getLargestFractureRadius(shapeFamilies[forceLargeFractCount]);
            familyIndex = forceLargeFractCount;
            cdfIdx = cdfIdxFromFamNum(CDF, p32Status, forceLargeFractCount);
            newPoly = generatePoly_withRadius(radius, shapeFamilies[forceLargeFractCount], generator, distributions, familyIndex);
            forceLargeFractCount++;
        } else {
            // Choose a family based on probabiliyis AND their target p32 completion status
            // if a family has already met is fracture intinisty req. (p32) dont choose that family anymore
            // Choose a family based on probabiliyis AND their target p32 completion status
            // if a family has already met is fracture intinisty reqirement (p32) dont choose that family anymore
            familyIndex = indexFromProb_and_P32Status(CDF, uniformDist(generator), totalFamilies, cdfSize, cdfIdx);
            newPoly = generatePoly(shapeFamilies[familyIndex], generator, distributions, familyIndex, false);
        }
        
        // Truncate poly if needed
        // Returns 1 if poly is outside of domain or truncated to less than 3 vertices
        // Vector for storing intersection boundaries
        bool reject = false;
        
        while (domainTruncation(newPoly, domainSize) == 1) {
            // Poly is completely outside domain, or was truncated to
            // less than 3 vertices due to vertices being too close together
            rejectCounter++; // Counter for re-trying a new translation
            
            // Test if newPoly has reached its limit of insertion attempts
            if (rejectCounter >= rejectsPerFracture) {
                delete[] newPoly.vertices; // Created with new, need to manually deallocate
                reject = true;
                break;; // Reject poly, generate new polygon
            } else { // Retranslate poly and try again, preserving normal, size, and shape
                reTranslatePoly(newPoly, shapeFamilies[familyIndex], generator);
            }
        }
        
        if (reject == true) {
            // Restart while loop
            // Generate new fracture
            continue;
        }
        
        // Calculate poly's area
        newPoly.area = getArea(newPoly);
        
        // Update P32
        if (shapeFamilies[familyIndex].layer == 0 && shapeFamilies[familyIndex].region == 0) { // Whole domain
            shapeFamilies[familyIndex].currentP32 += newPoly.area * 2 / domVol;
        } else if (shapeFamilies[familyIndex].layer > 0 && shapeFamilies[familyIndex].region == 0) { // Layer
            shapeFamilies[familyIndex].currentP32 += newPoly.area * 2 / layerVol[shapeFamilies[familyIndex].layer - 1];
        } else if (shapeFamilies[familyIndex].layer == 0 && shapeFamilies[familyIndex].region > 0) { // Region
            shapeFamilies[familyIndex].currentP32 += newPoly.area * 2 / regionVol[shapeFamilies[familyIndex].region - 1];
        }

        // Save radius for real DFN generation
        shapeFamilies[familyIndex].radiiList.push_back(newPoly.xradius);
        
        // If the last inserted polygon met the p32 requirement, set that family to no longer
        // insert any more fractures. adjust the CDF and family probabilities
        if (shapeFamilies[familyIndex].currentP32 >= shapeFamilies[familyIndex].p32Target ) {
            p32Status[familyIndex] = 1; //mark family as having its p32 requirement met
            
            // Adjust CDF, PDF, and reduce their size by 1. Keep probabilities proportional.
            // Remove the completed families element in the CDF and famProb[]
            // Distribute the removed family probability evenly among the others and rebuild the CDF
            // familyIndex = index of family's probability
            // cdfIdx = index of the family's correspongding cdf, (index to elmt to remove)
            if (cdfSize > 1 ) { // If there are still more families to insert ( cdfSize = 0 means no more families to insert)
                adjustCDF_and_famProb(CDF, famProbability, cdfSize, cdfIdx);
            }
        }
        
        // No need to save any polygons,
        // We are just simulating dfn with no rejections
        // to get an idea of how many fractures we will
        // need for each family
        delete[] newPoly.vertices;
    } // End while loop for inserting polyons
    
    // Reset p32 to 0
    for (int i = 0; i < totalFamilies; i++) {
        p32Status[i] = 0;
        shapeFamilies[i].currentP32 = 0;
    }
}

