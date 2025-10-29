#ifndef _readInputFunctions_h_
#define _readInputFunctions_h_
#include <fstream>
#include <vector>
#include <string>
#include <iostream>
#include "structures.h"
#include "input.h"
#include "logFile.h"

//Note, Template functions (type t) are coded inside .h files

// Function forward declarations/prototypes
// See readInputFunctions.cpp for descriptions and code
void searchVar(std::ifstream &stream, std::string search);
void checkIfOpen(std::ifstream &stream, std::string fileName);
void checkIfOpen(std::ofstream &stream, std::string fileName);
void getCords(std::ifstream & stream, double *outAry, int nPoly, int nVertices);
std::vector<std::string> splitOnWhiteSpace(std::string line);
void readDomainVertices(std::string filename);

/*****************************************************************/
/*! Gets multiple arrays from input/ Assumes arrays are format: {x,y,z}
    Reads a 2D array in a 1D format.
    Arg 1: if stream object
    Arg 2: OUTPUT, array to place read values into
    Arg 3: Number of rows of array we are reading */
template <typename T>
void get2dAry(std::ifstream &stream, T *var, int rowSize) {
    int i;
    char ch;
    
    for (i = 0; i < rowSize; i++) {
        int x = 3 * i;
        stream >> ch >> var[x] >> ch >> var[x + 1] >> ch >> var [x + 2] >> ch;
    }
}

/*****************************************************************/
/*! Gets multiple arrays from input/ Assumes arrays are format: {x,y}
    Reads a 2D array in a 1D format.
    Arg 1: if stream object
    Arg 2: OUTPUT, array to place read values into
    Arg 3: Number of rows of array we are reading */
template <typename T>
void get2dAry2(std::ifstream &stream, T *var, int rowSize) {
    int i;
    char ch;
    
    for (i = 0; i < rowSize; i++) {
        int x = 2 * i;
        stream >> ch >> var[x] >> ch >> var[x + 1] >> ch;
    }
}



/*****************************************************************/
/*! Used to read in 1d arrays from input file with n Elements
    Arg 1: ifstream object
    Arg 2: OUTPUT, array to place read values into
    Arg 3: Number of elements to read */
template <typename T>
void getInputAry(std::ifstream &stream, T *var, int nElements) {
    int i;
    char ch;
    
    for (i = 0; i < nElements; i++) {
        stream >> ch >> var[i];
    }
}


/*****************************************************************/
/*! Prints array of size 'nElements'
    Arg 1: Pointer to array
    Arg 2: Variable name
    ARg 3: Number of elements */
template <typename T>
void printAry(T *var, std::string varName, int nElements) {
    int i;
    nElements += -1;
    std::string logString = varName + " = {";
    logger.writeLogFile(INFO,  logString);
    
    for (i = 0; i < nElements; i++) {
        logString = to_string(var[i]) + ", ";
        logger.writeLogFile(INFO,  logString);
    }
    
    logString = to_string(var[nElements]) + "}\n";
    logger.writeLogFile(INFO,  logString);
}


/*****************************************************************/
/*! Prints 1-d array in 2-d array form.
    Assumes 3 col per row
    Arg 1: Pointer to array
    Arg 2: Variable name
    ARg 3: Number of row */
template <typename T>
void print2dAry(T *var, std::string varName, int rowSize) {
    int i;
    std::string logString = varName + " :\n";
    logger.writeLogFile(INFO,  logString);
    
    for(i = 0; i < rowSize; i++) {
        int x = 3 * i;
        logString = "{" + to_string(var[x]) + ", " + to_string(var[x + 1]) + ", " + to_string(var[x + 2]) + "}\n";
        logger.writeLogFile(INFO,  logString);
    }
}


/*****************************************************************/
/*! Read list of elements from file seperated by spaces
    Arg 1: ifstream object
    Arg 2: OUTPUT, Pointer to arary to store elements read
    Arg 3: Number of elements to read */
template <typename T>
void getElements(std::ifstream &stream, T *var, int nElements) {
    int i;
    
    for(i = 0; i < nElements; i++) {
        stream >> var[i];
    }
}

void getRectCoords(std::ifstream &stream, double *var, int nRectangles);
void printRectCoords(double *var, std::string varName, int nRectangles);
void printInputVars();
void getInput(char* inputFile, std::vector<Shape> &shapeFamily);
unsigned int getTimeBasedSeed();

#endif
