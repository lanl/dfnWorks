#include "distributions.h"
#include "insertShape.h"
#include <float.h>
#include <cmath>
#include <cstdlib>
#include <iostream>

/*
    The Distributions class was created specifically for
    easy use of a customized exponential distribution
    which allows users to specify the min and max limit
    which the distribution function can return.
    (exponentail distribution function truncated on both sides)

    The Distributions class was created keeping in mind
    other distributions may be needed later.

    Currently, exponential distribution is the only
    distribution contained in the Distributions class.
*/

/***********************************************************/
/******************* Constructor ***************************/
/*! Initialize maxInput. maxInput is the maximum double
    less than 1. (0.9999... before being recognized as 1)

    Initialize exponential distribution class.

    Arg 1: Random number generator */
Distributions::Distributions(std::mt19937_64 &_generator, std::vector<Shape> &shapeFamilies) {
    // Maximum double less than 1.0
    // (0.9999... before being recognized as 1)
    maxInput = getMaxDecimalForDouble();
    // Init exponential dist class
    expDist = new ExpDist(maxInput, _generator);
    // User input check and exp dist init
    checkDistributionUserInput(shapeFamilies);
}

/***********************************************************/
/******************  Get Max Digits  ***********************/
/*! Calculates and returns the maximum precision, in number of
    digits, after the decimal place for a number between 0 and 1. */
int Distributions::getMaxDigits() {
    // log(2) / log (10) = 0.301029995663982
    return std::floor(DBL_MANT_DIG * 0.30102999566398) + 2;
}


/***********************************************************/
/************** Get Max Number Less Than 1.0  **************/
/*! Returns the largest number less than 1.0 before being
    considered 1.0 by the computer (0.99999...). */
double Distributions::getMaxDecimalForDouble() {
    char temp[32];
    int length = getMaxDigits();
    temp[0] = '.';
    
    for (int i = 1; i < length; i++) {
        temp[i] = '9';
    }
    
    temp[length] = '\0'; // Add NULL char
    double returnVal = atof(temp);
    return returnVal;
}

/********************************************************************************/
/*** Initialize and  Error Check On User Input for Exponendtail Distribution  ***/
/*! MANDATORY FUNCTION FOR USING EXPONENTIAL DISTRIBUTION
    This function currently only error checks the exponential
    distribution option. The code has been outlined to
    add other distributions easily in the future.
    A custom exponential distribution function was needed to allow
    the user to define the minimum and maximum value the distribution
    would return, without sampling randomly and throwing away numbers
    larger than the maximum or less than the minimum user defined limit.

    This function checks that the user's min and max limit for exponential
    distribution is acceptible. That is, that the machine is able to produce
    the min and maximum given. For example, if the mean is set very small,
    and the user defined maximim is set very large, it may be the case that the
    largest number able to be produced from the distribution will be less than
    the user defined maximum. This check will warn the user
    if this is the case.

    This function is MANDATORY for the min and max input options to work.
    The function initializes the minimum and maximum input to the
    distrubution function in order to return a value which is between
    the user's min and max distribution limit from the input file.

    Arg 1: Array of all stochastic fracture families */
void Distributions::checkDistributionUserInput(std::vector<Shape> &shapeFamilies) {
    for (unsigned int i = 0; i < shapeFamilies.size(); i++) {
        switch (shapeFamilies[i].distributionType) {
            double input;
            
        case 1: // Lognormal
            break;
            
        case 2: // Truncated power-law
            break;
            
        case 3: // Exponential
            // Check exponential minimum value
            input = expDist->computeInput(shapeFamilies[i].expMin, shapeFamilies[i].expLambda);
            
            if (input >= 1) {
                std::cout << "\n\nWARNING: The defined minimum value, " << shapeFamilies[i].expMin
                          << ", for " << shapeType(shapeFamilies[i])
                          << " family " << getFamilyNumber(i, shapeFamilies[i].shapeFamily)
                          << " will not be able to be produced by the exponential distribution due to precision issues.\n";
                std::cout << "The minimum value is too large. The largest value the distribution can "
                          << "produce with current parameters is "
                          << expDist->getMaxValue(shapeFamilies[i].expLambda) << "\n";
                std::cout << "Please adjust the minimum value, or the mean, and try again.\n";
                exit(1);
            } else {
                shapeFamilies[i].minDistInput = input;
            }
            
            // Check exponential maximum value
            input = expDist->computeInput(shapeFamilies[i].expMax, shapeFamilies[i].expLambda);
            
            if (input >= 1) {
                std::cout << "\n\nWARNING: The defined maximum value, " << shapeFamilies[i].expMax << ", for "
                          << shapeType(shapeFamilies[i]) << " family " << getFamilyNumber(i, shapeFamilies[i].shapeFamily)
                          << " will not be able to be produced by the exponential distribution due to precision issues.\n";
                std::cout << "The largest value the distribution can produce with current parameters is "
                          << expDist->getMaxValue(shapeFamilies[i].expLambda) << "\n";
                std::cout << "Press Enter to automatically adjust this exponential maximum value to "
                          << expDist->getMaxValue(shapeFamilies[i].expLambda) << " (q to Quit)\n";
                // Prompt user to press enter to continue or q to quit
                quitOrContinue();
                double max  = expDist->getMaxValue(shapeFamilies[i].expLambda);
                
                //check that the max is not less or equal to the min
                if (max <= shapeFamilies[i].expMin) {
                    std::cout << "ERROR: The maximum exponetnial distribution radius possible for " << shapeType(shapeFamilies[i])
                              << " family " << getFamilyNumber(i, shapeFamilies[i].shapeFamily)
                              << " is less than or equal to the minimum exponential distribution radius.\n";
                    std::cout << "Please adjust the exponential distribution parameters in " << shapeType(shapeFamilies[i])
                              << " family " << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << "\n";
                    exit(1);
                }
            }
            
            shapeFamilies[i].maxDistInput = input;
            break; // End case 3
        }
    }
}


/******************************************************/
/*************** Quit or Continue *********************/
/*! Stops program execution and waits for input from user
    to continue.
    'q' or 'Q' to quit program and exit
    enter/return key to continue with program execution.*/
void Distributions::quitOrContinue() {
    char str[256];
    
    do {
        // Get input
        std::cin.get(str, 256);
        std::cin.clear();
        std::cin.ignore();
        
        if ((str[0] == 'q' && str[1] == '\0') || (str[0] == 'Q' && str[1] == '\0')) {
            exit(1);
        }
        
        if (str[0] != 0) {
            std::cout << "Invalid input.\n";
        }
    } while (str[0] != 0);
}

/******************************************************/
/** Destructor ****************************************/
Distributions::~Distributions() {
    delete expDist;
}

