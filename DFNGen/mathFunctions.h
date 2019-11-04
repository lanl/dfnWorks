#ifndef _MATHFUNCTIONS_H_
#define _MATHFUNCTIONS_H_

double sumDeviation(const double *data, int n);
double *sumDevAry3(double *data);
int maxElmtIdx(double *data, int n);
int *sortedIndex(const double *arr, int n);
double getArea(struct Poly &poly);
int indexFromProb(float *CDF, double roll, int size);
int indexFromProb_and_P32Status(float *CDF, double roll, int famSize, int cdfSize, int &cdfIdx);
void adjustCDF_and_famProb(float *&CDF, float *&famProbability, int &cdfSize, int idx2Remove);
float *createCDF(float *famProb, int size);
float truncatedPowerLaw(float randomNum, float emin, float emax, float alpha);
int cdfIdxFromFamNum(float *CDF, bool *p32Status, int famIdx);

/****************************************************/
/*! Used for ORing arrays of bool for boundary face codes
    Expectes array size is 6.
    ORs dest with src, then saves to dest.
    e.g destArray = destArray ^ srcArray

    Arg 1: dest array
    Arg 2: souce array */
inline void OR(bool *dest, bool *src) {
    dest[0] = (dest[0] | src[0]);
    dest[1] = (dest[1] | src[1]);
    dest[2] = (dest[2] | src[2]);
    dest[3] = (dest[3] | src[3]);
    dest[4] = (dest[4] | src[4]);
    dest[5] = (dest[5] | src[5]);
}

#endif
