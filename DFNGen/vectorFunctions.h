//vectorFunctions.h
#ifndef _vectorFunctions_h_
#define _vectorFunctions_h_
#include <fstream>
#include <string>
#include <iostream>
#include <cmath>
#include "input.h"
#include "structures.h"


double *projection( const double *v1, const double *v2 );
double euclideanDistance(double *A, double *B);
double euclideanDistance(Point &A, Point &B);
double angleBeteenVectors(const double *vector1, const double *vector2);

/**************************************************/
/*! Calculates crossproduct of v1 and v2
    Arg 1: Pointer to array of three elements
    Arg 2: Pointer to array of three elements
    Return: Pointer to cross product, array of three elements
    NOTE: must use delete[] on returned pointer after use. */
template <typename T>
inline T* crossProduct(const T *v1, const T *v2) {
    T *result = new T[3];
    result[0] = v1[1] * v2[2] - v1[2] * v2[1];
    result[1] = v1[2] * v2[0] - v1[0] * v2[2];
    result[2] = v1[0] * v2[1] - v1[1] * v2[0];
    return result;
}

/**************************************************/
/*! Normalizes vector passed into fucntion.
    Arg 1: Vector (3 element array) to be normalized. */
template <typename T>
inline void normalize(T *vec) {
    double invMag = 1.0f / sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]);
    
    if (!std::isinf(invMag)) {
        vec[0] = vec[0] * invMag;
        vec[1] = vec[1] * invMag;
        vec[2] = vec[2] * invMag;
    } else {
        std::cout << "\nERROR: Attempted to normalize a vector with magnitude = 0\n";
        exit(1);
    }
}


/**************************************************/
/*! Calculates the dot product of vector A with B
    Arg 1: Pointer to array of three elements
    Arg 2: Pointer to array of three elements
    Return: Pointer to dot product, array of three elements
    NOTE: Must use delete[] on returned pointer after use */
template <typename T>
inline T dotProduct(const T *A, const T *B) {
    T result = A[0] * B[0] + A[1] * B[1] + A[2] * B[2];
    return result;
}


/**************************************************/
/*! Prints vertices with {x, y, z} format.
    Arg 1: Pointer to vertice array. Expects array
           length to be a multple of three
    Arg 2: Number of vertices in array */
template <typename T>
void printVertices(T *vert, int numVertices) {
    std::cout << "Vertices:\n";
    
    for (int i = 0; i < numVertices; i++ ) {
        int x = i * 3;
        std::cout << "{" << vert[x] << "," << vert[x + 1] << "," << vert[x + 2] << "}\n";
    }
}


/**************************************************/
/*! Calculates magnitude of a vector
    Arg 1: x
    Arg 2: y
    Arg 3: z
    Return: Magnitude of {x,y,z}  */
template <typename T>
inline T magnitude(T x, T y, T z) {
    return sqrt((x * x) + (y * y) + (z * z));
}


/**************************************************/
/*! Calculates the square magnitude of a vector
    Arg 1: x
    Arg 2: y
    Arg 3: z
    Return: Square magnitude of {x,y,z} */
template <typename T>
inline T sqrMagnitude(T x, T y, T z) {
    return (x * x) + (y * y) + (z * z);
}


/**************************************************/
/*! Check if two vectors are parallel
    Arg 1: Pointer to vector 1, array of three doubles
    Arg 2: Pointer to vector 2, array of three doubles
    Output: True if vectors are parallel
            False otherwise */
inline bool parallel(double *v1, double *v2) {
    normalize(v1);
    normalize(v2);
    double dotProd = dotProduct(v1, v2);
    
    if (1 - eps < dotProd && dotProd < 1 + eps) {
        return 1;
    } else {
        return 0;
    }
}

#endif


