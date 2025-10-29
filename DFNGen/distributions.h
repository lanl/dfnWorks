#ifndef _distributions_h
#define _distributions_h
#include "expDist.h"
#include <random>
#include "structures.h"
#include "logFile.h"

extern Logger logger;

/*! The Distributions class is used to hold all the custom distribution classes
    that are used by DFNgen. As of now, the only distribution we have completely customized
    is the exponential distribution class ExpDist. The customizations allow us
    to limit the range of numbers the distribution is able to produce. This allows
    the user to define the minimum and maximum size fractures they want from the
    distribution.*/


class Distributions {

  public:
    Distributions(std::mt19937_64 &_generator, std::vector<Shape> &shapeFamilies);
    ~Distributions();
    ExpDist *expDist;
    
    /*! Maximum input to distributions. 0.999999... before being recognized as 1
        by the computer (1 returns inf for some distributions).
    
        Set in the Distributions constructor. */
    double maxInput;
    
  private:
    /*  Calculates the maximum precision in number of digits after the
        decimal place for a number between 0 and 1. */
    int getMaxDigits();
    
    // Retrns something like 0.99999... to the maximum precision
    // before becomming considered 1 by the computer
    double getMaxDecimalForDouble();
    
    // See distributions.cpp
    void checkDistributionUserInput(std::vector<Shape> &shapeFamilies);
    void quitOrContinue();
};

#endif
