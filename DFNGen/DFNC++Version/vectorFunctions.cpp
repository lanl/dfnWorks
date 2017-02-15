#include <cmath>
#include "structures.h"
#include "vectorFunctions.h"
#include <iostream>
#include <cmath>
#include "input.h"//eps

//see vectorFunctions.h for template function implimentations
//such as crossProduct, dorProduct, magnitude,...


/************************************************************/
/************************************************************/
// Projection funcion without sqrt()
// Projects v1 onto v2
// Arg 1: Pointer to vector 1 containing {x,y,z}, all doubles
// Arg 2: Pointer to vector 2 containing {x,y,z}, all doubles
// Return: Resulting vector. 
//         Must delete return array manually. Created with new.
double *projection( const double *v1, const double *v2 ) {
		      
    double v2_ls = v2[0]*v2[0] + v2[1]*v2[1] + v2[2]*v2[2];
    
    double *result = new double[3];
    
    if (v2_ls < eps) {
    	result[0] = 0;
    	result[1] = 0;
    	result[2] = 0;    	    	
    }
    else {
        double temp = ((v2[0]*v1[0] + v2[1]*v1[1] + v2[2]*v1[2] )/v2_ls );
        result[0] =  v2[0] * temp;
        result[1] =  v2[1] * temp;
        result[2] =  v2[2] * temp;
	}
    return result;
}

/************************************************************/
/************************************************************/
// Calculates the distance between two points in 3D space.
// Arg 1: Pointer to 3 element double array {x,y,z}
// Arg 2: Pointer to 3 element double array {x,y,z}
// Return: Distance between point A and point B
double euclideanDistance(double *A, double *B){
        double temp1 = A[0] - B[0];
        double temp2 = A[1] - B[1];
        double temp3 = A[2] - B[2];
        temp1 = temp1*temp1;
        temp2 = temp2*temp2;
        temp3 = temp3*temp3;

        return std::sqrt(temp1+temp2+temp3);
}

double euclideanDistance(Point &A, Point &B) {
        double temp1 = A.x - B.x;
        double temp2 = A.y - B.y;
        double temp3 = A.z - B.z;
        temp1 = temp1*temp1;
        temp2 = temp2*temp2;
        temp3 = temp3*temp3;

        return std::sqrt(temp1+temp2+temp3);
}

/************************************************************/
/************************************************************/
// Claculates the angle between two vectors
// Arg 1: Pointer to 3 element double array, {x,y,z} vector
// Arg 2: Pointer to 3 element double array, {x,y,z} vector
// Return: Angle between both vectors in radians
double angleBeteenVectors(const double *vector1,const double *vector2) {
    // cos(x) = u.v / (mag(u) * mag(v))
    // x = arccos(x) = (mag(u) * mag(v)) / u.v
    double dot = dotProduct(vector1, vector2); 
    double v1Mag = magnitude(vector1[0], vector1[1], vector1[2]);
    double v2Mag = magnitude(vector2[0], vector2[1], vector2[2]);
    double angle = std::acos(dot/(v1Mag*v2Mag));

    return angle;
}
	

