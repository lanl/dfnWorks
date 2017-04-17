#include "readInputFunctions.h"
#include <cstdlib>
#include <chrono>
#include <fstream>
#include <string>


/*******************************************************************/
/*******************************************************************/
/*! Searches for variable in files, moves file pointer to position
    after word. Used to read in varlable values
    Arg 1: ifstream file object
    Arg 2: Word to search for */
void searchVar(std::ifstream &stream, std::string search){
    std::string word;
    stream.clear(); // Reset file pointer in case of eof encountered
    // Reset file position pointer to beginning, allows access to variables in any order
    stream.seekg(0); 
    while (stream >> word) {
        if (word == search) {    
            break;
        }
    }
    if ((int) stream.tellg() == -1){
         std::cout<< "Variable not found: \""<< search << "\"\n";
         exit(1);
    }
}

/*******************************************************************/
/*******************************************************************/
/*! Checks file for being opened correectly with error msg
    Arg 1: ifstream file object
    Arg 2: Filename. Used for error print if there is an error*/
void checkIfOpen(std::ifstream &stream, std::string fileName){
  if (!stream.is_open()){
    std::cout<< "ERROR: unable to open file "<< fileName << std::endl;
    exit(1);
    }
}

void checkIfOpen(std::ofstream &stream, std::string fileName){
  if (!stream.is_open()){
    std::cout<< "ERROR: unable to open file "<< fileName << std::endl;
    exit(1);
    }
}

/**********************************************************************/
/**********************************************************************/
/*! Used to read in rectangualr coordinates when the user is using 
    user rectangles defined by coordinates option.
    Arg 1: ifstream file object
    Arg 2: OUTPUT. Pointer to array to store the coordinates
    Arg 3: Number of rectangles */
void getRectCoords(std::ifstream &stream, double *var, int nRectangles){
    int i;
    char ch;
    for (i = 0; i < nRectangles; i++) {
        int x = i*12;
        stream >> ch >> var[x]   >> ch >> var[x+1]  >> ch >> var[x+2]  >> ch 
               >> ch >> var[x+3] >> ch >> var[x+4]  >> ch >> var[x+5]  >> ch 
               >> ch >> var[x+6] >> ch >> var[x+7]  >> ch >> var[x+8]  >> ch 
               >> ch >> var[x+9] >> ch >> var[x+10] >> ch >> var[x+11] >> ch; 
    }  
}


/**********************************************************************/
/**********************************************************************/
/*! Used to read in ellipse coordinates when the user is using 
    user ellipses defined by coordinates option.
    Arg 1: ifstream file object
    Arg 2: OUTPUT. Pointer to array to store the coordinates
    Arg 3: Number of ellipses 
    Arg 4: Number of points per ellipse */
void getCords(std::ifstream & stream, double *outAry, int nPoly, int nVertices) {

    char ch;
    int size = nPoly * nVertices;
    
    for (int i = 0; i < size; i++) {
        int x = i * 3;
        stream >> ch >> outAry[x]   >> ch >> outAry[x+1]  >> ch >> outAry[x+2]  >> ch;
    }
}


/*******************************************************************/
/*******************************************************************/
/*! Prints rectangular coordinates. Useful for debugging.
    Arg 1: Array that stored all rectangular coordinates.
    Arg 2: Variable name
    Arg 3: Number of rectangles */
void printRectCoords(double *var, std::string varName, int nRectangles){
    int i;
    std::cout << varName << ": \n";
    for (i = 0; i<nRectangles; i++) {
        int x = i*12;
        std::cout << "{" << var[x]   << "," << var[x+1]  << "," << var[x+2]  << "} " 
                  << "{" << var[x+3] << "," << var[x+4]  << "," << var[x+5]  << "} " 
                  << "{" << var[x+6] << "," << var[x+7]  << "," << var[x+8]  << "} " 
                  << "{" << var[x+9] << "," << var[x+10] << "," << var[x+11] << "}\n";    
    }
}


/*******************************************************************/
/*******************************************************************/ 
/*! Gets time based seed 
    Return: Seed based on the system clock */
unsigned int getTimeBasedSeed() {
    return std::chrono::system_clock::now().time_since_epoch().count();
}










