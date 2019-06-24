#include <iostream>
#include <numeric>
#include <algorithm>
#include "mathFunctions.h"
#include <math.h>
#include "structures.h"
#include "vectorFunctions.h"
#include <iomanip>

/****************************************************************************/
/****************************************************************************/
/*! There are several spots in the code which used to use standard
    deviation to know how to sort a list of points.
    To increase performance, the standard deviation is now calculated without
    the square root and division by N elements.
    Arg 1: Pointer to array which we need the sum deviation of
    Arg 2: Number of elements in array pointed to by arg 1
    Return: The sum-deviation of array 'v' */
double sumDeviation(const double *v, int n) {
    double mean = 0, sumDeviation = 0;
    int i;
    
    for(i = 0; i < n; i++) {
        mean += v[i];
    }
    
    mean = mean / n;
    
    for(i = 0; i < n; i++) {
        double temp = v[i] - mean;
        sumDeviation += temp * temp;
    }
    
    return sumDeviation;
}

/******************************************************************/
/*************  Sum deviaiton array X 3  **************************/
/*! Used in intersectionChecking()
    How function is used:
    v is a pointer to an array of 4 points, each point
    contains x, y, and z coordinates
    The 4 sumDeviation is computed on all points' x, y, and z coord.
    An array of three elements is returned containing the sum deviation
    of all x's, all y's, and all z's

    Arg 1: Array of 12 elements: 4 points, {x1, y1, z1, ... , x4, y4, z4}
    Return: Array of 3 elements x,y,z with each stdDev, respectively */
double *sumDevAry3(double *v) {
    double *result = new double[3];
    const double x[4] = {v[0], v[3], v[6], v[9]};
    const double y[4] = {v[1], v[4], v[7], v[10]};
    const double z[4] = {v[2], v[5], v[8], v[11]};
    result[0] = sumDeviation(x, 4);
    result[1] = sumDeviation(y, 4);
    result[2] = sumDeviation(z, 4);
    return result;	// MUST DELETE RETURN MANUALLY
}

/******************************************************************/
/*******************  Get Max Element's Index  ********************/
/*! Used to find index of element with max value from array4
    Used in intersectionChecking()
    Arg 1: Array of doubles
    Arg 2: Size of array
    Return: Max element's array index

    If elements happen to be equal, returns the first one */
int maxElmtIdx(double *v, int n) {
    double max = v[0]; // Initialize
    int i;
    int idx = 0;
    
    for (i = 1; i < n; i++) {
        if (max < v[i] ) {
            max = v[i];
            idx = i;
        }
    }
    
    return idx;
}

/******************************************************************/
/********************  Sort Array Indices  ************************/
/*! Similar to mathematica's Ordering[] funct.
    Arg 1: Pointer to array of doubles
    Arg 2: Size of array, number of elements
    Return: Array of sorted indicies to elements in 'v'
            sorted smallest to largest  */
int* sortedIndex(const double *v, int n) {
    // Initialize original index locations
    int *idx = new int[n];
    std::iota(idx, idx + n, 0);
    // Sort indexes based on comparing values in v
    std::sort(idx, idx + n, [v](size_t i1, size_t i2) {
        return v[i1] < v[i2];
    });
    return idx;
}

/******************************************************************/
/********************  Get Poly's Area  ***************************/
/*! Calculate exact area of polygon (after truncation)
    Summary of algorithm:
    1: Creates a point on the inside of the polygon (insidePt)
    2: Uses 'insidePt' to create vectors to all outside vertices, breaking the polygon into triangles
    3: Uses .5 * (magnitude of cross product) for each triangle for area calculation
    4: Sums the areas for each trianlge for total area of polygon
    Arg 1: Polygon
    Return: Area of polygon */
double getArea(struct Poly &poly) {
    if (poly.numberOfNodes == 3) { //area = 1/2 mag of xProd
        double v1[3] = {poly.vertices[3] - poly.vertices[0], poly.vertices[4] - poly.vertices[1], poly.vertices[5] - poly.vertices[2]};
        double v2[3] = {poly.vertices[6] - poly.vertices[0], poly.vertices[7] - poly.vertices[1], poly.vertices[8] - poly.vertices[2]};
        double *xProd = crossProduct(v1, v2);
        double area = .5 * magnitude(xProd[0], xProd[1], xProd[2]);
        delete[] xProd;
        return area;
    } else { // More than 3 vertices
        double polyArea = 0; // For summing area over trianlges of polygon
        // Get coordinate within polygon
        double insidePt[3];
        int idxAcross = poly.numberOfNodes / 2 * 3;
        insidePt[0] = poly.vertices[0] + (.5 * (poly.vertices[idxAcross] - poly.vertices[0])); //x
        insidePt[1] = poly.vertices[1] + (.5 * (poly.vertices[idxAcross + 1] - poly.vertices[1])); //y
        insidePt[2] = poly.vertices[2] + (.5 * (poly.vertices[idxAcross + 2] - poly.vertices[2])); //z
        
        for (int i = 0; i < poly.numberOfNodes - 1; i++) {
            int idx = i * 3;
            double v1[3] = {poly.vertices[idx] - insidePt[0], poly.vertices[idx + 1] - insidePt[1], poly.vertices[idx + 2] - insidePt[2]};
            double v2[3] = {poly.vertices[idx + 3] - insidePt[0], poly.vertices[idx + 4] - insidePt[1], poly.vertices[idx + 5] - insidePt[2]};
            double *xProd = crossProduct(v1, v2);
            double area = .5 * magnitude(xProd[0], xProd[1], xProd[2]);
            delete[] xProd;
            polyArea += area; // Accumulate area
        }
        
        // Last portion of polygon, insidePt to first vertice and insidePt to last vertice
        int last = 3 * (poly.numberOfNodes - 1);
        double v1[3] = {poly.vertices[0] - insidePt[0], poly.vertices[1] - insidePt[1], poly.vertices[2] - insidePt[2]};
        double v2[3] = {poly.vertices[last] - insidePt[0], poly.vertices[last + 1] - insidePt[1], poly.vertices[last + 2] - insidePt[2]};
        double *xProd = crossProduct(v1, v2);
        double area = .5 * magnitude(xProd[0], xProd[1], xProd[2]);
        delete[] xProd;
        polyArea += area; // Accumulate area
        return polyArea;
    }
}


/******************************************************************/
/*************  Index from Probability  ***************************/
/*! CDF is 1 to 1 and algined with the stochastic family
    shapes array (std vector). This chooses the family index based
    on a random roll (random number between 0 and 1) and 'famProb'
    Arg 1: CDF of shape families based on famProb array in input file
    Arg 2: Random number between 0 and 1
    Arg 3: Number of elements in 'CDF' array
    Return: Index to family based on the probability famProb  */
int indexFromProb(float *CDF, double roll, int size) {
    for (int i = 0; i < size; i++) {
        if (roll <= CDF[i]) {
            return i;
        }
    }
    
    return size - 1;
}


/****************************************************************************/
/******  Choose Family Randomly Based On P32 and CDF  ***********************/
/*! Use with fracture intensity (p32) stopping option
    Arg 1: Pointer to CDF array
    Arg 2: Random variable between 0 and 1
    Arg 3: Number of stochastic families
    Arg 4: Number of elements in CDF array
    Arg 5: OUTPUT, index of CDF element which was chosen randomly
    Return: Index of chosen family based on its family probability, and p32Status
            (avoids inserting a fracture from a family which has already met it's fracture intensity requrement) */
int indexFromProb_and_P32Status(float *CDF, double roll, int famSize, int cdfSize, int &cdfIdx) {
    // The p32Status bool array stays 1 to 1 with the number of total families.
    // The p32Status array with element = 1 means that family has reached its p32 requirement.
    // The CDF contains an amount of elements equal to the number of families which has not met its intensity requirement.
    // To get the correct familyShape[] index from cdf, me must ignore any families their p32 requirement alrady met
    // Index we hit based on random roll,
    cdfIdx = indexFromProb(CDF, roll, cdfSize);
    // If cdfIndex = 2 (thrid element including 0)
    // we need to find the families with p32Status still 0, and choose the thrid one
    // this family will be used to create the next polygon
    int count = 0; // Count of families encountered with p32Status = 0
    
    for (int i = 0; i < famSize; i++) {
        if (cdfIdx == count && p32Status[i] == 0) {
            return i; // Returns family index we need to build poly with.
        } else if (p32Status[i] == 0) {
            count++; // Count number of 0's ( number of families not having met their p32 req. )
        }
    }
    
    std::cout << "ERROR: see indexFromProb_and_P32Status(), funct did not return anything\n";
    return famSize - 1;
}


/****************************************************************************/
/******  Choose Family Randomly Based On P32 and CDF  ***********************/
/*! Given a family number, return its corresponding CDF array index
    Arg 1: CDF array
    Arg 2: p32Status array
    Arg 3: Family index of family whos CDF index to return
    Return: Index of CDF which belongs to shapeFamily[famIdx] */
int cdfIdxFromFamNum(float *CDF, bool *p32Status, int famIdx) {
    int idx = -1;
    // The CDF array only contains elements for families who have not
    // met their P32 requirenment (p32 option)
    // If Npoly option is being used, the CDF array and shape familyies array
    // are aligned and 1:1
    
    // Check how many 0's (p32's not complete) before the given family index
    // This gives the index in the CDF array for the given family
    for (int i = famIdx; i >= 0; i--) {
        if (p32Status[i] == 0) {
            idx++;
        }
    }
    
    return idx;
}

/******************************************************************/
/************************  Create CDF *****************************/
/*! Creates CDF from famProb[]
    Arg 1: Pointer to famProb array (see input file, and readInput())
    Arg 2: Size of array */
float *createCDF(float *famProb, int size) {
    // Convert famProb to CDF
    float *CDF = new float[size];
    CDF[0] = famProb[0];
    
    for (int i = 1; i < size; i++) {
        CDF[i] = CDF[i - 1] + famProb[i];
    }
    
    if ((CDF[size - 1] < 0.999) || (CDF[size - 1] > 1.001)) {
        std::cout << "\nWARNING: Familiy probabilities (famProb in input file) do not sum to 1 \nsum = "
                  << std::setprecision(17) << CDF[size - 1] << "\nPlease check input file.\n\n";
    }
    
    return CDF;
}

/**************************************************************************************/
/**************************************************************************************/
/*! Adjusts the CDF and the famProb array. Used with P32 stopping contdition (see input file)
    When a family's P32 requrement is met, the CDF is adjusted to remove that family from
    the array. The famProb is also adjusted in the same way.
    Arg 1: Pointer to CDF array
    Arg 2: Pointer to famProb array
    Arg 3: Number of elements in CDF array
    Arg 4: Index to the element in the famProb array which is being removed */
void adjustCDF_and_famProb(float *&CDF, float *&famProbability, int &cdfSize, int idx2Remove) {
    cdfSize--;
    float *newProbs = new float[cdfSize];
    // Adjust probabilities, remove element while keeping the rest of probabilities in proportion
    // Take probability of the familiy being removed, and divide it equally among remaining probabilities
    float addToRemainingElmts = famProbability[idx2Remove] / cdfSize; // Distribute removed probability among leftore famillies probabilities
    // cdfIdx is index to that families cdf index AND familily probability index
    int idx = 0;
    
    for (int i = 0; i < cdfSize + 1; i++) { // cdfSize+1 becuase of cdfSize-- at the beginning of function. This
        // makes the loop cover the all probabilities in the ary before one is removed
        // and distributed to the rest
        if (i != idx2Remove) {
            newProbs[idx] = famProbability[i] + addToRemainingElmts;
            idx++;
        }
    }
    
    delete[] famProbability; // Delete old prob array
    famProbability = newProbs; // Assign famProbability array to new probabilities array
    delete[] CDF; // Delete old CDF array
    CDF = createCDF(famProbability, cdfSize); // Create new CDF array
}


