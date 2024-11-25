#include "expDist.h"
#include "logFile.h"
#include <cmath>
#include <iostream>

using std::string;

/*
    Exponential Distribution Class

    This class was created to allow the user to specify
    the min and max values received from the exponential
    distrubution function.
*/

/***************************************************************************/
/**************************** Constructor **********************************/
/*! Initializes 'maxInput': the maximum deecimal value the machine can produce
    less than 1.0
    Initializes 'generator': the random number generator
    Arg 1: maxDecimal, the maximum double less than 1.0 the machine can produce
           e.g. 0.9999999... before being recognized as 1.0
    Arg 2: Reference to std library <random> random number Mersenne twister engine generator. */
ExpDist::ExpDist(double maxDecimal, std::mt19937_64 &_generator) : generator(_generator) {
    maxInput = maxDecimal;
    generator = _generator;
}


/***************************************************************************/
/************** Random Uniform Random Number Generator *********************/
/*! Function returns a random double on [min, max]
    Arg 1: Minimum bound
    Arg 2: Maximum bound
    Return: Random double on [min, max] */
double ExpDist::unifRandom(double min, double max) {
    return ((max - min) *  double(generator()) / generator.max() + min);
}


/***************************************************************************/
/***************************************************************************/
// Overloaded Function
/*! Returns a random number from the distribution with a random variable
    given as an argument.
    Arg 1: Lambda
    Arg 2: Random variable between 0 and 1
    Return: Random number from exponential distribution described by 'lambda' */
double ExpDist::getValue(double lambda, double rv) {
    std::string logString;
    
    if (rv > 1) {
        logString = "ERROR: Attempted to input random value of greater than 1 to the exponential distribution class's getValue() function. Input must be on [0,1] interval.\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    
    // Using inverse CDF
    if (rv != 1) {
        return  -std::log(1 - rv) / lambda;
    } else {
        return -std::log(1 - maxInput) / lambda;
    }
}


/***************************************************************************/
/***************************************************************************/
// Overloaded Function
/*! Generates a random value from the exponental distribution between the user's
    defined minimum and maximum range.

    minVal and maxVal are the inputs needed to produce the user's minimum and maximum
    fracture sizes. minVal and maxVal are initialized within the Distributions constructor
    and saved in the Shape structure. Using a uniform random variable with range
    [minVal, maxVal], the exponential distrubition will always return a value
    within that range.

    Arg 1: Exponential Lambda (1/mean)
    Arg 2: Minimum input (between 0 and 1)
    Arg 3: Maximum input (between 0 and 1)
    Return: Random number from exponential distribution described by 'lambda'
            and sampled with random variable between minInput and maxVal */
double ExpDist::getValue(double lambda, double minVal, double maxVal) {
    std::string logString;
    
    // Uniform distrubution on [minVal, maxVal)
    if ( maxVal > 1 || minVal > 1) {
        // Passing 1 into exp. distribution will reuturn inf
        logString = "ERROR: Passed min, or max, input value of greater than 1 to getValue() in expDist.cpp. Input must be in [0,1] interval.\n";
        logger.writeLogFile(ERROR,  logString);
        exit(1);
    }
    
    double randVar = unifRandom(minVal, maxVal);
    
    // Using inverse CDF
    // If randVar is 1, this function returns inf
    if (randVar != 1) {
        return  -std::log(1 - randVar) / lambda;
    } else {
        return -std::log(1 - maxInput) / lambda;
    }
}


/***************************************************************************/
/*******************  Get Max Value Possible  ******************************/
/*! Returns maximum possible value from distribution.
    (What the inverse CDF returns when given 0.9999... to maximum precision.
    Inputing 1.0 into the distribution results in 'inf'.)

    Used to print warning to user if their desired maximum is larger than the
    machine is able to produce.

    Arg 1: Lambda
    Return: Maximum value possible due to machine precision issues
            before reutrning inf */
double ExpDist::getMaxValue(double lambda) {
    return -std::log(1 - maxInput) / lambda;
}


/***************************************************************************/
/*********  Compute Input to Distribution for a Certain Output  ************/
/*! Computes what the input value needs to be in
    order for the distribution to return 'output'
    Uses the distributions CDF for computation.

    Arg 1: The desired output of from the distribution (getValue())
    Arg 2: Lambda
    Return: The necessary input to getValue() to produce a value of 'output' */
double ExpDist::computeInput(double output, double lambda) {
    return 1.0 - std::exp(-lambda * output);
}


