#ifndef _expDist_h_
#define _expDist_h_
#include <random>

/*! Exponentail Distribution Class

    This class was created to allow the user to specify
    the min and max values to be produced by the exponential
    distrubution. */


class ExpDist {

  private:
    /*! Maximum input to distribution
        .999999... before being recognized
        as 1 by the computer. (1 returns inf).
        Initialized during Distributions constructor. */
    double maxInput;
    
    double unifRandom(double, double);
    
    /*! Reference to std library <random> random generator using 64-bit
        Mersenne twister engine. */
    std::mt19937_64 &generator;
    
  public:
  
    // Constructor. maxDecimal is the maximum number less than 1,
    // using maximum digits in the double's mantissa, to use
    // when sampling the dist. This prevents .999999... being
    // turned into 1, causing a return of inf from the distribution
    //ExpDist(double maxDecimal, std::mt19937_64 &_generator);
    ExpDist(double maxDecimal, std::mt19937_64 &_generator);
    
    // Returns double using rv as "random variable"
    double getValue(double lambda, double rv);
    
    // Generates its own random input to distribution
    double getValue(double lambda, double minInput, double maxInput);
    
    // Returns maximum value computer is able to produce
    // can be relatively small with certain parameters for lambda
    // due to precision issues.
    double getMaxValue(double lambda);
    
    // Computes what the input value needs to be in
    // order for the distribution to return "output" value
    double computeInput(double output, double lambda);
};

#endif


