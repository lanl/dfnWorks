#include <iomanip>
#include <algorithm>
#include "computationalGeometry.h"
#include "structures.h"
#include <iostream>
#include <cmath>
#include "vectorFunctions.h"
#include "input.h"
#include "mathFunctions.h"
#include "generatingPoints.h"
#include <fstream>
#include <random>
#include "testing.h"
#include "clusterGroups.h"

/**********************************************************************/
/*********************** 2D rotation matrix ***************************/
/*! Rotates poly around its normal vecotor on x-y plane
    Assumes poly is on x-y plane
    Assumes poly.numberOfNodes is set
    Angle must be in radians
    Arg 1: Poly to be rotated
    Arg 2: Angle to rotate to */
void applyRotation2D(Poly &newPoly, float angle) {
        
    float sinCalc = sin(angle); 
    float cosCalc = cos(angle);
    
    // Rotates polygon on x-y plane counter-clockwise
    for (int i = 0; i < newPoly.numberOfNodes; i++) {
        int idx = i*3;
        double x = newPoly.vertices[idx];
        double y = newPoly.vertices[idx+1];
        newPoly.vertices[idx] = (x * cosCalc) + (y * sinCalc); // x
        newPoly.vertices[idx+1] = (x * -sinCalc) + (y * cosCalc); // y
        newPoly.vertices[idx+2] = 0; // z
    }    
}


//**********************************************************************/
//************************  Translate  *********************************/
/*! Translates 'newPoly' to 'translation'
    Assumes newPoly.numberOfNodes is initialized
    Arg 1: Polygon to translate
    Arg 2: translation (new x,y,z  position) double[3] array */
void translate(Poly &newPoly, double *translation) {

        newPoly.translation[0] = translation[0];
        newPoly.translation[1] = translation[1];
        newPoly.translation[2] = translation[2];

    for (int i = 0; i < newPoly.numberOfNodes; i++) {
        int idx = i*3;
        newPoly.vertices[idx]   = newPoly.vertices[idx]   + translation[0];
        newPoly.vertices[idx+1] = newPoly.vertices[idx+1] + translation[1];
        newPoly.vertices[idx+2] = newPoly.vertices[idx+2] + translation[2];
    }
}


//*********************************************************************/
//******************** Build Rotation Ratrix **************************/
/*! Returns rotation matrix (double, 3x3) of rotation from normalA to normalB
    Requires normals to be normalized
    
    Expects normalA and normalB to be normalized.
    
    Arg1: double pointer to normalA, array of 3 doubles 
    Arg2: double pointer to normalB, array of 3 doubles
    Return: pointer to 3x3 rotation matrix array
    NOTE: Must manually delete reurn pointer with delete[] */
double *rotationMatrix(double *normalA, double *normalB) {
    //***************************************************
    // Note: Normals must be normalized by this point!!!!!!
    // Since vectors are normalized, sin = magnitude(AxB) and cos = A dot B
    //***************************************************
    
    // normalA is current normal
    // nNormalB is target normal
    
    // Delete manually with delete[], created with new[]
    double *xProd = crossProduct(normalA, normalB); 
    
    // If not parallel            
    if (!(std::abs(xProd[0]) < eps && std::abs(xProd[1]) < eps && std::abs(xProd[2]) < eps)) {

        // sin = magnitude(AxB) and cos = A . B
        double sin = sqrt(xProd[0]*xProd[0] + xProd[1]*xProd[1] + xProd[2]*xProd[2]);
        double cos = dotProduct(normalA, normalB);
        double v[9] = {0, -xProd[2], xProd[1], xProd[2], 0, -xProd[0], -xProd[1], xProd[0], 0};
        double scalar = (1.0f-cos)/(sin*sin);

        double vSquared[9];
        vSquared[0] = (v[0]*v[0] + v[1]*v[3] + v[2]*v[6])*scalar;
        vSquared[1] = (v[0]*v[1] + v[1]*v[4] + v[2]*v[7])*scalar;
        vSquared[2] = (v[0]*v[2] + v[1]*v[5] + v[2]*v[8])*scalar;
        vSquared[3] = (v[3]*v[0] + v[4]*v[3] + v[5]*v[6])*scalar;
        vSquared[4] = (v[3]*v[1] + v[4]*v[4] + v[5]*v[7])*scalar;
        vSquared[5] = (v[3]*v[2] + v[4]*v[5] + v[5]*v[8])*scalar;
        vSquared[6] = (v[6]*v[0] + v[7]*v[3] + v[8]*v[6])*scalar;
        vSquared[7] = (v[6]*v[1] + v[7]*v[4] + v[8]*v[7])*scalar;
        vSquared[8] = (v[6]*v[2] + v[7]*v[5] + v[8]*v[8])*scalar;
        
        double *R = new double[9];
        R[0] = 1 + v[0] + vSquared[0];
        R[1] = 0 + v[1] + vSquared[1];
        R[2] = 0 + v[2] + vSquared[2];
        R[3] = 0 + v[3] + vSquared[3];
        R[4] = 1 + v[4] + vSquared[4];
        R[5] = 0 + v[5] + vSquared[5];
        R[6] = 0 + v[6] + vSquared[6];
        R[7] = 0 + v[7] + vSquared[7];
        R[8] = 1 + v[8] + vSquared[8];
        
        delete[] xProd;
        return R; // Make sure to delete R with delete[]    
    }
    else { // normalA and normalB are parallel, return identity matrix
        double *R = new double[9];
        R[0] = 1;
        R[1] = 0;
        R[2] = 0;
        R[3] = 0;
        R[4] = 1;
        R[5] = 0;
        R[6] = 0;
        R[7] = 0;
        R[8] = 1;
        
        delete[] xProd;
        return R; // Make sure to delete R with delete[]    
    }
}


//*********************************************************************/
/********** Applies a Rotation Matrix to poly vertices ****************/
/**********************************************************************/
//  RotMatrix = I + V + V^2((1-cos)/sin^2)) rotate to new normal       /
/**********************************************************************/    
/*! Rotates 'newPoly' from newPoly's current normal 
    so that newPoly's new normal will be 'normalB'
    Assumes poly.numberOfPoints and newPoly.normal are initialized and normalized
    Arg 1: Poly to be rotated
    Arg 2: Normal vector to rotate to (array of 3 doubles) */
void applyRotation3D(Poly &newPoly, double *normalB) {
    // Normals should already be normalized by this point!!!

    // NormalA: newPoly's current normal
    // NormalB: target normal

    // Delete manually with delete[], created with new[]
    double *xProd = crossProduct(newPoly.normal, normalB); 
    
    // If not parallel            
    if (!(std::abs(xProd[0]) < eps && std::abs(xProd[1]) < eps && std::abs(xProd[2]) < eps )) {

        // NOTE: rotationMatrix() requires normals to be normalized                
        double *R = rotationMatrix(newPoly.normal, normalB);
        
        // Apply rotation to all vertices
        for (int i = 0; i < newPoly.numberOfNodes; i++) {
            int idx = i*3;
            double vertices[3];
            vertices[0] = newPoly.vertices[idx]   * R[0] 
                        + newPoly.vertices[idx+1] * R[1] 
                        + newPoly.vertices[idx+2] * R[2];
            vertices[1] = newPoly.vertices[idx]   * R[3] 
                        + newPoly.vertices[idx+1] * R[4] 
                        + newPoly.vertices[idx+2] * R[5];
            vertices[2] = newPoly.vertices[idx]   * R[6] 
                        + newPoly.vertices[idx+1] * R[7] 
                        + newPoly.vertices[idx+2] * R[8];
        
            newPoly.vertices[idx]   = vertices[0];
            newPoly.vertices[idx+1] = vertices[1];
            newPoly.vertices[idx+2] = vertices[2];                
        }
        delete[] R;
    } 
    // xProd was created dynamically in crossProduct(), need to delete it  
    delete[] xProd;       
}


/**********************************************************************/
/* 3D Rotation Matrix for intersection, trip. points, and  polygpons **/
/**********************************************************************/
/*  RotMatrix = I + V + V^2((1-cos)/sin^2))                           */
/**********************************************************************/
/*! Rotates intersections to x-y plane, including triple intersection points.
    While doing this, if poly is not already on x-y plane, poly will 
    also be rotated to x-y plane.
    Doing these all at once keeps us from having to re-calulate rotation
    matricies, or cary them in memory, increasing performance
    Return rotated intersectoins - don't change original intersections 
    Original, non-rotated intersections are need to rotate to the other intersecting polys
    Function is used to wrtie intersection.inp output files
    Arg 1: Intersection, belonging to newPoly(arg 2), to be rotated
    Arg 2: Poly which is being rotated (OK if already on x-y plane)
    Arg 3: Vecor array of all triple intersection points in DFN
    Arg 4: OUTPUT, Array to place rotated triple intersection points
           Because triple intersection points are rotated 3 different ways, 
           we must preserve the original points.
    Return: Rotated version of intersection passed in arg 1 */
struct IntPoints polyAndIntersection_RotationToXY(struct IntPoints &intersection, Poly &newPoly, std::vector<Point> &triplePoints, std::vector<Point> &tempTripPts) {
    // newPoly.normal = newPoly's current normal, should already be normalized
    // normalB = target normal

    double normalB[3] = { 0, 0, 1 };
    IntPoints tempIntpts;

    // Delete xProd manually, created with new[]
    double *xProd = crossProduct(newPoly.normal, normalB); 
        
    // If not parallel (zero vector)
    if (!(std::abs(xProd[0]) < eps && std::abs(xProd[1]) < eps && std::abs(xProd[2]) < eps )) {
        
        // rotationMatrix() requires normals to be normalized
        double *R = rotationMatrix(newPoly.normal, normalB);    
        
        // Because the normal's in the polygon structure don't change (we need them to 
        // write params.txt), the xProd check at the top of the function may not work. 
        // Poly vertices may have already been rotated to XY plane but the normal 
        // was unchanged. newPoly.XYPlane resolves this issue. It will tell us if 
        // the polyon has already been rotated to xy plane
        
        // Check if nodes are not already on x-y plane:
        if (newPoly.XYPlane != 1) { // If not on x-y plane:
            for (int i = 0; i < newPoly.numberOfNodes; i++) {
                int idx = i*3;
                double vertices[3];
                // Apply rotation matrix R to each vertice
                vertices[0] = newPoly.vertices[idx]   * R[0] 
                            + newPoly.vertices[idx+1] * R[1] 
                            + newPoly.vertices[idx+2] * R[2];

                vertices[1] = newPoly.vertices[idx]   * R[3] 
                            + newPoly.vertices[idx+1] * R[4] 
                            + newPoly.vertices[idx+2] * R[5];

                vertices[2] = newPoly.vertices[idx]   * R[6] 
                            + newPoly.vertices[idx+1] * R[7] 
                            + newPoly.vertices[idx+2] * R[8];
        
                // Save vertices back to poly struct, now on x-y plane
                newPoly.vertices[idx]   = vertices[0];
                newPoly.vertices[idx+1] = vertices[1];
                newPoly.vertices[idx+2] = vertices[2];    
            }
        }
        
        // Rotate intersection endpoints
        tempIntpts.x1 = intersection.x1 * R[0] 
                      + intersection.y1 * R[1] 
                      + intersection.z1 * R[2];

        tempIntpts.y1 = intersection.x1 * R[3] 
                      + intersection.y1 * R[4] 
                      + intersection.z1 * R[5];

        tempIntpts.z1 = intersection.x1 * R[6] 
                      + intersection.y1 * R[7] 
                      + intersection.z1 * R[8];
        
        tempIntpts.x2 = intersection.x2 * R[0] 
                      + intersection.y2 * R[1] 
                      + intersection.z2 * R[2];

        tempIntpts.y2 = intersection.x2 * R[3] 
                      + intersection.y2 * R[4] 
                      + intersection.z2 * R[5];

        tempIntpts.z2 = intersection.x2 * R[6] 
                      + intersection.y2 * R[7] 
                      + intersection.z2 * R[8];
        
        // Rotate any existing triple intersection pts to xy plane
        Point tmpPt;
        for (unsigned int i = 0; i<intersection.triplePointsIdx.size(); i++) {
            tmpPt.x = triplePoints[intersection.triplePointsIdx[i]].x*R[0] 
                    + triplePoints[intersection.triplePointsIdx[i]].y*R[1]
                    + triplePoints[intersection.triplePointsIdx[i]].z*R[2];

            tmpPt.y = triplePoints[intersection.triplePointsIdx[i]].x*R[3]
                    + triplePoints[intersection.triplePointsIdx[i]].y*R[4]
                    + triplePoints[intersection.triplePointsIdx[i]].z*R[5];

            tmpPt.z = triplePoints[intersection.triplePointsIdx[i]].x*R[6] 
                    + triplePoints[intersection.triplePointsIdx[i]].y*R[7]
                    + triplePoints[intersection.triplePointsIdx[i]].z*R[8];
        
            tempTripPts.push_back(tmpPt);
        }
    }
    else { // Already on xy plane (normal = {0,0,1}), no rotation required
        // Copy triple points to tempIntpts 
        for (unsigned int i = 0; i < intersection.triplePointsIdx.size(); i++) {
            int idx = intersection.triplePointsIdx[i];
            tempTripPts.push_back(triplePoints[idx]);
        }
        tempIntpts.x1 = intersection.x1;
        tempIntpts.y1 = intersection.y1;
        tempIntpts.z1 = intersection.z1;
        tempIntpts.x2 = intersection.x2;
        tempIntpts.y2 = intersection.y2;
        tempIntpts.z2 = intersection.z2;
    } 

    newPoly.XYPlane = 1; // Mark poly being rotated to xy plane
    delete[] xProd; // xProd was created dynamically in crossProduct(), delete it        
    return tempIntpts;
}


/**********************************************************************/
/********************** Create Bounding box ***************************/
/*! Creates bounding box for polygon/fracture
    Sets bounding box in poly struct
    Arg 1: Poly to create and set bounding box for */
void createBoundingBox(struct Poly &newPoly) {
    // Initialize mins and maxs
    double maxX, minX, maxY, minY, maxZ, minZ;
    maxX = minX = newPoly.vertices[0]; // x1
    maxY = minY = newPoly.vertices[1]; // y1
    maxZ = minZ = newPoly.vertices[2]; // z1
    
    for (int i = 1; i < newPoly.numberOfNodes; i++) {
    int idx = i*3;
        // idx = x
        if (maxX < newPoly.vertices[idx]) {  
            maxX = newPoly.vertices[idx];    
        }                                                                       
        else if (minX > newPoly.vertices[idx]) {
            minX = newPoly.vertices[idx];
        }
        // idx+1 = y
        if (maxY < newPoly.vertices[idx+1]) {
            maxY = newPoly.vertices[idx+1];
        }    
        else if (minY > newPoly.vertices[idx+1]) {
            minY = newPoly.vertices[idx+1];
        }
        // idx+2 = z
        if (maxZ < newPoly.vertices[idx+2]) {
            maxZ = newPoly.vertices[idx+2];
        }    
        else if (minZ > newPoly.vertices[idx+2]) {
            minZ = newPoly.vertices[idx+2];
        }
    }
    newPoly.boundingBox[0] = minX;
    newPoly.boundingBox[1] = maxX;
    newPoly.boundingBox[2] = minY;
    newPoly.boundingBox[3] = maxY;
    newPoly.boundingBox[4] = minZ;
    newPoly.boundingBox[5] = maxZ;    
}


/**********************************************************************/
/*! Bounding box print out to std out.   
    Arg 1: Poly whos bounding box to print to screen. */
void printBoundingBox(struct Poly &newPoly) {
    std::cout<<"\nBounding Box:\n";
    std::cout<<"MinX = "<<newPoly.boundingBox[0]<<"    MaxX = "<<newPoly.boundingBox[1]<<"\n";
    std::cout<<"MinY = "<<newPoly.boundingBox[2]<<"    MaxY = "<<newPoly.boundingBox[3]<<"\n";
    std::cout<<"MinZ = "<<newPoly.boundingBox[4]<<"    MaxZ = "<<newPoly.boundingBox[5]<<"\n";
}


/**********************************************************************/
/*********************** Check Bounding Box ***************************/
/*! Compares two polygons' bounding boxes, returns 1 if bounding boxes intersect
    Arg 1: Poly 1
    Arg 2: Poly 2
    Return: True if bounding box's intersect, false otherwise  */
bool checkBoundingBox(Poly &poly1, Poly &poly2) {

    if (poly1.boundingBox[1] < poly2.boundingBox[0]) return false;
    if (poly1.boundingBox[0] > poly2.boundingBox[1]) return false;
    if (poly1.boundingBox[3] < poly2.boundingBox[2]) return false;
    if (poly1.boundingBox[2] > poly2.boundingBox[3]) return false;
    if (poly1.boundingBox[5] < poly2.boundingBox[4]) return false;
    if (poly1.boundingBox[4] > poly2.boundingBox[5]) return false;
    return true;
}


/**********************************************************************/
/****************** Find Intersections ********************************/
/*! Finds intersection end points of two intersecting polygons (Poly 1 and Poly 2)
    Or, finds that polygons do not intersect (flag will = 0 )
    Arg 1: OUTPUT, flag (see definitions below)
    Arg 2: Poly 1
    Arg 3: Poly 2
    Return: Intersection end points, Valid only if flag != 0 */
struct IntPoints findIntersections(short &flag, Poly &poly1, Poly &poly2) {
/* FLAGS: 0 = no intersection
   NOTE: The only flag which is currently used is '0'
         1 = intersection is completely inside poly 1 (new fracture)/poly)                                 
         2 = intersection is completely inside poly 2 (already accepted poly)
         3 = intsersection on both polys edges
         current implimentation: poly1 is the new fracture being tested            
             poly2 is a previously accepted fracture newPoly is being tested against
*/

// This code is mostly converted directly from the mathematica version. 
// Re-write may be worth doing for increased performance and code clarity 

    flag = 0;
    IntPoints intPts; // Final intersection points                             
                                 
    int count;
    Poly *F1; // Fracture 1 
    Poly *F2; // Fracture 2 
    double inters2[6]; // Temporary intersection points of F2 and P1
    double inters[12]; // Stores 4 possible intersection points {x,y,z} * 3
    double temp[3];      
      
    // Get intersecction points
    for (int jj = 0; jj<2; jj++) {
        count = 0; // Intersection point number
        if (jj == 0 ) {
            F1 = &poly1; 
            F2 = &poly2; 
        }
        else {
            F1 = &poly2;
            F2 = &poly1;        
        }
        int nVertices2 = F2->numberOfNodes;
        int index = (nVertices2-1) * 3; // Index to last vertice

        double vertex1[3] = { F1->vertices[0], F1->vertices[1], F1->vertices[2] };
        
        temp[0] = F2->vertices[index]   - vertex1[0]; // x1 -x2
        temp[1] = F2->vertices[index+1] - vertex1[1]; // y1 - y2
        temp[2] = F2->vertices[index+2] - vertex1[2]; // z1 - z2
    
        double prevdist = dotProduct(temp, F1->normal);
        double currdist;
        
        for (int i = 0; i < nVertices2; i++) { // i: current point
            int idx = i * 3;
            /* vector of vertex1 to a vertex on F2 dot normal vector of F1
               it's absolute value is the distance */
            temp[0] = F2->vertices[idx]   - vertex1[0];
            temp[1] = F2->vertices[idx+1] - vertex1[1];
            temp[2] = F2->vertices[idx+2] - vertex1[2];
            currdist = dotProduct(temp, F1->normal);
            
            if (std::abs(prevdist) < eps) {
                if (i == 0) {
                    // Previous point is intersection point
                    inters2[0] = F2->vertices[index];   // x
                    inters2[1] = F2->vertices[index+1]; // y
                    inters2[2] = F2->vertices[index+2]; // z
                    count++;
                }
                else {
                    int idx = (i-1)*3;
                    int countidx = count*3;
                    inters2[countidx]   = F2->vertices[idx];   // x
                    inters2[countidx+1] = F2->vertices[idx+1]; // y
                    inters2[countidx+2] = F2->vertices[idx+2]; // z
                    count++;
                } 
            }
            else {    
                double currTimesPrev = currdist * prevdist;
                if (std::abs(currTimesPrev) < eps) {
                    currTimesPrev = 0; 
                }
                        
                if (currTimesPrev < 0) { 
                // If consecutive vertices of F2 are at opposide sides of P1,  
                // computes intersection point of F2 and P1
                                        
                    double c = std::abs(prevdist)/(std::abs(currdist)+std::abs(prevdist));
                    int countidx = count * 3;
                    if(i == 0) { 
                        inters2[countidx]   = F2->vertices[index]   
                                            + (F2->vertices[0]-F2->vertices[index]) * c;
                        inters2[countidx+1] = F2->vertices[index+1] 
                                            + (F2->vertices[1]-F2->vertices[index+1]) * c; 
                        inters2[countidx+2] = F2->vertices[index+2] 
                                            + (F2->vertices[2]-F2->vertices[index+2]) * c; 
                        count++;
                    }
                    else {
                        int idx = (i-1) * 3;
                        int x = i*3;
                        inters2[countidx]   = F2->vertices[idx]   
                                            + (F2->vertices[x]-F2->vertices[idx]) * c; 
                        inters2[countidx+1] = F2->vertices[idx+1] 
                                            + (F2->vertices[x+1]-F2->vertices[idx+1]) * c; 
                        inters2[countidx+2] = F2->vertices[idx+2] 
                                            + (F2->vertices[x+2]-F2->vertices[idx+2]) * c;
                        count++;
                    }    
                }
            }
            prevdist = currdist; 
            if (count == 2) {
                break; }    
                    
        } // End vertice loop 
    
        if (count == 1) { 
        // If only one intersection point, happens only when a vertex of F2 is on P1
            count = 2;
            inters2[3] = inters2[0];
            inters2[4] = inters2[1];
            inters2[5] = inters2[2];
        }

        for (int k = 0; k<6; k++) { 
            if (std::abs(inters2[k]) < eps) {
                inters2[k] = 0; }
        }        
        
        // copy to inters array
        int jindx = 6*jj;
        inters[jindx]   = inters2[0]; 
        inters[jindx+1] = inters2[1]; 
        inters[jindx+2] = inters2[2]; 
        inters[jindx+3] = inters2[3]; 
        inters[jindx+4] = inters2[4]; 
        inters[jindx+5] = inters2[5];
        
        if (count == 0) {
            break; 
        } // No intersection
    } // End loop for jj, loop for getting intersections for fracture i and newPoly
        
    if (count == 0) {
        flag = 0;
    }
    else { // Intersection points exist
        if (count >2) { std::cout<<"Error in findIntersections()\n"; }
        
        // Use delete[] on 'stdev', created dynamically
        double *stdev = sumDevAry3(inters); 
        
        int o = maxElmtIdx(stdev,3);
        
        double tempAry[4] = {inters[o], inters[o+3], inters[o+6], inters[o+9]};

        int *s = sortedIndex(tempAry,4); 
                    
        if (!(s[0] + s[1] == 1 || s[0] + s[1] == 5)) {                                                              
        // If the smallest two points are not on the bdy of the same poly, 
        // the polygons intersect. middle two points form intersetion

        int idx1 = s[1]*3;
        int idx2 = s[2]*3;    
        
        intPts.x1 = inters[idx1];   // x1
        intPts.y1 = inters[idx1+1]; // y1
        intPts.z1 = inters[idx1+2]; // z1
        intPts.x2 = inters[idx2];   // x2
        intPts.y2 = inters[idx2+1]; // y2
        intPts.z2 = inters[idx2+2]; // z2

            // Assign flag (definitions at top of funciton)
            if (s[1] + s[2] == 1) {
                flag = 1;}    // Intersection inside poly1
            else if (s[1] + s[2] == 5 ) {
                flag = 2;}    // Intersection inside poly2
            else{ 
                flag = 3;}    // Intersection on edges
        } 
        else { // Intersection doesn't exist
            flag = 0; // No intersection 
        }

        delete[] s;   
        delete[] stdev;
        
    } // End  intersection points exist
    return intPts;      
} 


/*************************************************************************************/
/*************************************************************************************/
/************************************ FRAM *******************************************/
/******************** Feature Rejection Algorithm for Meshing ************************/
/*! Checks new poly and new intersection against other intersecting polygons
    for violation of minimum feature size 'h'
    In some cases, the intersection may be shortened in order to accepted the fracture. 
    Arg 1:  Newest intersection found on new poly
    Arg 2:  OUTPUT, counter of number of intersections on new poly
    Arg 3:  Intersection endpoints list for entire DFN
    Arg 4:  New poly, poly being checked with FRAM
    Arg 5:  Poly which new poly intersects with
    Arg 6:  Stats structure (Should only be one, singleton)
    Arg 7:  OUTPUT, reject code if FRAM rejects fracture
    Arg 8:  Temp triple point data. Must keep intersections and triple points as temp
            data untill newPoly has been accepted
    Arg 9:  Triple points for entire DFN
    Arg 10: Temp intersection points. Must keep intersections and triple points as temp
            data untill newPoly has been accepted
    Return: 0 (False) if accepted, 1 (True) if rejected */
int FRAM(IntPoints &intPts, unsigned int count, std::vector<IntPoints> &intPtsList, Poly &newPoly, Poly &poly2, Stats &pstats, std::vector<TriplePtTempData> &tempData, std::vector<Point> &triplePoints, std::vector<IntPoints> &tempIntPts) {

    if (disableFram == false) {
        /******* Check for intersection of length less than h *******/
        if (magnitude(intPts.x1-intPts.x2, intPts.y1-intPts.y2, intPts.z1-intPts.z2) < h) {
            //std::cout<<"\nrejectCode = -2: Intersection of length <= h.\n";
            pstats.rejectionReasons.shortIntersection++;    
            return -2;
        }

         /******************* distance to edges *****************/ 
        // Reject if intersection shirnks < 'shrinkLimit'
        double shrinkLimit = 0.9 * magnitude(intPts.x1 - intPts.x2, intPts.y1 - intPts.y2, intPts.z1 - intPts.z2);
        if (checkCloseEdge(newPoly, intPts, shrinkLimit, pstats)) {
            // std::cout<<"\nrejectCode = -6: Fracture too close to another fracture's edge.\n";
            pstats.rejectionReasons.closeToEdge++;
            return -6;
        }

        if (checkCloseEdge(poly2, intPts, shrinkLimit, pstats)) {
            // std::cout<<"\nrejectCode = -6: Fracture too close to another fracture's edge.\n";
            pstats.rejectionReasons.closeToEdge++;
            return -6;
        }
        /*************** Triple Intersection Checks *************/
        // NOTE: for debugging, there are several rejection codes for triple intersections
        // -14 <= rejCode <= -10 are for triple intersection rejections

        int rejCode = checkForTripleIntersections(intPts, count, intPtsList, newPoly, poly2, tempData, triplePoints);
        if (rejCode != 0 ) {
            pstats.rejectionReasons.triple++;
            return rejCode;
        }

        /******* Intersection to Intersection Distance Checks ********/
        // Check distance from new intersection to other intersections on 
        // poly2 (fracture newPoly is intersecting with)

        if (checkDistToOldIntersections(intPtsList, intPts, poly2, h)) {
            pstats.rejectionReasons.interCloseToInter++;
            return -5;
        }

        // Check distance from new intersection to intersections already
        // existing on newPoly
        // Also checks for undetected triple points
        if (checkDistToNewIntersections(tempIntPts, intPts, tempData, h)) {
            pstats.rejectionReasons.interCloseToInter++;
            return -5;
        }

        // Check if polys intersect on same plane
        if (std::abs(newPoly.normal[0]-poly2.normal[0]) < eps  // If the normals are the same
            && std::abs(newPoly.normal[1]-poly2.normal[1]) < eps 
            && std::abs(newPoly.normal[2]-poly2.normal[2]) < eps ) {
            
            return -7; // The intersection has already been found so we know that if the
                      // normals are the same they must be on the same plane
        }    
    }
        return 0; 
}


/****************************  FRAM CHECK  *****************************************/
/************ New intersction to Old Intersections Check ***************************/
/*! Checks distance of new intersection to intersections on poly2
    Arg 1: Intersections arry for entire DFN
    Arg 2: Current intersection being checked, intersection between newPoly and poly2
    Arg 3: Poly2
    Arg 4: Minimum distance allowed if not a triple intersection
    Return: 0 if no all distances are larger than minDistance or minDistance = 0 with triple intersection point
            1 Otherwise */
bool checkDistToOldIntersections(std::vector<IntPoints> &intPtsList, IntPoints &intPts, Poly &poly2, double minDistance) {
    double intersection[6] = {intPts.x1, intPts.y1, intPts.z1, intPts.x2, intPts.y2, intPts.z2};
    int intSize = poly2.intersectionIndex.size();
    double dist;
    Point pt;   
    for (int i = 0; i < intSize; i ++) {    
        
        double int2[6] = {intPtsList[poly2.intersectionIndex[i]].x1, intPtsList[poly2.intersectionIndex[i]].y1, intPtsList[poly2.intersectionIndex[i]].z1,
                       intPtsList[poly2.intersectionIndex[i]].x2, intPtsList[poly2.intersectionIndex[i]].y2, intPtsList[poly2.intersectionIndex[i]].z2};
           
        dist = lineSegToLineSeg(intersection, int2, pt); 
        if (dist < (minDistance-eps) && dist > eps) {
            return 1;
        }
    }
    return 0;
}


/****************************  FRAM Check  *****************************************/
/************ New intersction to New Intersections Check ***************************/
/*! Checks distance of new intersection to other intersections on newPoly
    Arg 1: Array of intersections previously found on newPoly 
    Arg 2: Current intersection being checked, intersection between newPoly and poly2
    Arg 3: Temp triple points, triple points found on newPoly
    Arg 4: Minimum distance allowed if not a triple intersection
    Return: 0 if no all distances are larger than minDistance or minDistance = 0 with triple intersection point
            1 Otherwise
    NOTE: If the distance between two intersections is 0, this function will verify the that 
          the triple interersection exists in 'tempTriPts'. If not found, fracture will be rejected
          Due to the shrinkIntersection algorithm, it may be possible for a triple intersection point
          to exist on only one fracture. This check resolves this issue. */
bool checkDistToNewIntersections(std::vector<IntPoints> &tempIntPts, IntPoints &intPts, std::vector<TriplePtTempData> &tempTriPts, double minDistance) {

    int intSize = tempIntPts.size();
    double intersection[6] = {intPts.x1, intPts.y1, intPts.z1, intPts.x2, intPts.y2, intPts.z2};
    Point pt; // Pt of intersection if lines intersect

    for (int i = 0; i < intSize; i ++) {    
        
        double int2[6] = {tempIntPts[i].x1, tempIntPts[i].y1, tempIntPts[i].z1,
                          tempIntPts[i].x2, tempIntPts[i].y2, tempIntPts[i].z2};
           
        double dist = lineSegToLineSeg(intersection, int2, pt);
        
        if (dist < minDistance && dist > eps) {
            return 1;
        }
        else if (dist < eps) { 
            // Make sure there is a triple intersection point
            // before accepting
            bool reject = true;
            int size = tempTriPts.size();
            for (int i = 0; i < size; i++) {    
                // If the triple point is found, continue with checks, else reject
                if (std:: abs(pt.x - tempTriPts[i].triplePoint.x) < eps 
                && std::abs(pt.y - tempTriPts[i].triplePoint.y) < eps 
                && std::abs(pt.z - tempTriPts[i].triplePoint.z) < eps) {
                    reject = false;
                    break;
                }
            }
            if (reject == true) {
                return 1;
            }
        }
    }
    return 0;
}

/**********************************************************************/
/************************* Shrink Intersection ************************/
/*! Shrinks intersection untill the intersection is greater than 'minDist 
    to 'edge', or intersection shrinks to length < 'shrinkLimit'

    'firstNodeMinDist' can be used to allow a shoter first discretized node 
    distance. This allows for slight angles for intersections starting on the
    edges of polygons without there the intersection being shortened.
    If the first node is of distnace smaller than 'firstNodeMinDist', the 
    'minDist' will be used from this point on to shorten the intersection.

    Arg 1: Intersection being shrunk
    Arg 2: Double array[6] of two end points which intersection is being
           tested against
    Arg 3: Minimum length intersection is allowed to shrink
    Arg 4: Fist node minimum distance
    Arg 5: Minimum allowed distance between intersection and edge
    Return: 0 If intersection successfully shortened 
              and minDist <= dist to edge && shrinkLimit <= intersection length
            1 If intersection length shrinks to less than shrinkLimit  */
bool shrinkIntersection(IntPoints &intPts, double *edge, double shrinkLimit, double firstNodeMinDist, double minDist) {

    double vect[3] = {(intPts.x2-intPts.x1), (intPts.y2-intPts.y1), (intPts.z2-intPts.z1)};
    double dist = magnitude(vect[0], vect[1], vect[2]);

    // n is number of discrete points on intersection
    int n = std::ceil(2 * dist / h);
    double stepSize = 1 / (double)n;

    double pt[3] = {intPts.x1, intPts.y1, intPts.z1};

    // Start step at first descrete point
    double step;

    // Check both sides of intersection against edge
    for (int i = 0; i < 2; i++) {
        int nodeCount = 0;
        
        if (i == 0) { 
            step = 0;
        }
        else { 
            step = 1;        
        }

        Point point = lineFunction3D(vect, pt, step);
        double firstPtDistToEdge = pointToLineSeg(point, edge);

        bool firstPt = true; 
        while (nodeCount <= n) {
            nodeCount++;

            if (i == 0) {
                step += stepSize;
            }
            else {
                step -= stepSize;
            }
            
            Point ptOnIntersection = lineFunction3D(vect, pt, step);
            
            double dist = pointToLineSeg(ptOnIntersection, edge);
            if (firstPt == true && (dist > firstNodeMinDist)) { // || (stepSize == 1 && dist < eps)))  {
               if (firstPtDistToEdge < eps || firstPtDistToEdge >= minDist) {
                    // Leave intersection end point un-modified
                    break;
                }
            }
            
            firstPt = false;      
 
            if (dist > minDist) {
                if (i == 0) {
                    intPts.x1 = ptOnIntersection.x;
                    intPts.y1 = ptOnIntersection.y;
                    intPts.z1 = ptOnIntersection.z;
                }
                else {  
                    intPts.x2 = ptOnIntersection.x;
                    intPts.y2 = ptOnIntersection.y;
                    intPts.z2 = ptOnIntersection.z;

                }
                intPts.intersectionShortened = true;
                break;
            }
            if (nodeCount >= n) { // All nodes are bad, reject
                return 1;
            }
        }
    }
    
    // If intersection length shrank to less than shrinkLimit, reject
    if (magnitude(intPts.x2-intPts.x1, intPts.y2-intPts.y1, intPts.z2-intPts.z1) < shrinkLimit) {
        return 1;
    }

    return 0;
}


/****************************************************************************************************/
/************************************** INTERSECTION CHECKING ***************************************/
/*! This function will check for intersections with all polys whos bounding boxes intersect. It also will
    run FRAM on the intersections.
    'newPoly' will be checked with FRAM one intersection at a time. At the first FRAM rejection, further 
    intersection checking will be aborted and the poly will be retranslated or thrown away.
    This function saves intersections, and updates cluster groups when a poly is accepted. 
    This functino returns 0 if the poly was accepted and 1 if rejected. User needs to push the newPoly 
    into the accepted poly array if this function returns 0

    Arg 1: Polygon being tested (newest poly to come into the DFN)
    Arg 2: Array of all accepted polygons
    Arg 3: Array of all accepted intersections
    Arg 4: Program statistics structure
    Arg 5: OUTPUT, reject code if fracture is rejected
    Arg 6: Array of all accepted triple intersection points
    Return: 0 - Fracture had no intersections or features violating 
                the minimum feature size h (Passed all FRAM tests)
            1 - Otherwise */
int intersectionChecking(struct Poly &newPoly, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPtsList, struct Stats &pstats, std::vector<Point> &triplePoints) {

    // List of fractures which new fracture intersected.       
    // Used to update fractures intersections and 
    // intersection count if newPoly is accepted
    std::vector<unsigned int> tempIntersectList; 
    std::vector<IntPoints> tempIntPts;
    std::vector<IntPoints> tempOriginalIntersection;
    // Index to newPoly's position if accepted
    int newPolyIndex = acceptedPoly.size(); 
    // Index to intpts if newPoly intersections accepted
    int intPtsIndex = intPtsList.size(); 
    std::vector<unsigned int> encounteredGroups;
    // Counts number of accepted intersections on newPoly. 
    unsigned int count = 0; 
    std::vector<TriplePtTempData> tempData;


    unsigned int size = acceptedPoly.size();
    for (unsigned int ii = 0; ii < size; ii++) {
        short flag; 

        // NOTE: findIntersections() searches bounding boxes
        // Bounding box search
        if (checkBoundingBox(newPoly, acceptedPoly[ii])) {
            IntPoints intersection = findIntersections(flag, newPoly, acceptedPoly[ii]); 

            if (flag != 0) { // If flag != 0, intersection exists
                // Holds origintal intersection, used to update 
                // stats on how much intersections were shortened
                tempOriginalIntersection.push_back(intersection); 

                // FRAM returns 0 if no intersection problems. 
                // 'count' is number of already accepted intersections on new poly

                int rejectCode = FRAM(intersection, count, intPtsList, newPoly, acceptedPoly[ii], pstats, tempData, triplePoints, tempIntPts);

                // If intersection is NOT rejected
                if (rejectCode == 0) { // If FRAM returned 0, everything is OK
                    
                    // Update group numbers, intersection indexes            
                    intersection.fract1 = ii; // ii is the intersecting fracture
                    intersection.fract2 = newPolyIndex; // newPolys ID/index in array of accpted polys, if accepted

                    // 'tempIntersectList' keeps all fracture #'s intersecting with newPoly
                    tempIntersectList.push_back(ii); // Save fracture index to update if newPoly accepted

                    // Save index to polys intersections (intPts) array    
                    newPoly.intersectionIndex.push_back(intPtsIndex + count);    
                    
                    count++; // Increment counter of number of fractures intersecting with newPoly
                    tempIntPts.push_back(intersection); // Save intersection
                        
                    // If newPoly has not been assigned to a group, 
                    // assign the group of the other intersecting fracture
                        if (newPoly.groupNum == 0) { 
                            newPoly.groupNum = acceptedPoly[ii].groupNum;
                        }
                        else if (newPoly.groupNum != acceptedPoly[ii].groupNum) { // Poly bridged two different groupsa
                            encounteredGroups.push_back(acceptedPoly[ii].groupNum); 
                        }
                    }
                else { // 'newPoly' rejected
                    // SAVE REJECTED POLYS HERE IF THIS FUNCTINALITY IS NEEDED  
                    return rejectCode; // Break loop/function and return 1, poly is rejected
                }
            } 
        } 
    }  // If it makes it here, no problematic intersections with new polygon. SAVE POLY AND UPDATE GROUP/CLUSTER INFO      

     
    // Done searching intersections. All FRAM tests have passed. Polygon is accetepd. 

  
    // After searching for intersections, if newPoly still has no intersection or group:
    if (newPoly.groupNum == 0) { // 'newPoly' had no intersections. Assign it to its own/new group number
        assignGroup(newPoly, pstats, newPolyIndex);
    }
    else {
        // Intersections exist and were accepted, newPoly already has group number
        // Save temp. intersections to intPts (permanent array), 
        // Update all intersected polygons intersection-points index lists and intersection count
        // Update polygon group lists 
        
        // Append temp intersection points array to permanent one
        intPtsList.insert(intPtsList.end(),tempIntPts.begin(),tempIntPts.end()); 

        // Update poly's indexs to intersections list (intpts)
        for (unsigned int i = 0; i < tempIntersectList.size(); i++) {
            // Update each intersected poly's intersection index
            
            acceptedPoly[tempIntersectList[i]].intersectionIndex.push_back(intPtsIndex + i); 
            // intPtsIndex+i will be the index position of the intersection once it is saved to the intersections array
        }
                    
        // Fracture is now accepted.
        // Update intersection structures with triple intersection points.
        // triple intersection points will be found 3 times (3 fractures make up one triple int point)
        // We need only to save the point to the permanent triplePoints array once, and then give each intersection a
        // reference to it. 
        if (tripleIntersections == 1) {
            unsigned int tripIndex = triplePoints.size();            
            for (unsigned int j = 0; j < tempData.size(); j++) { // Loop through newly found triple points        
            
                triplePoints.push_back(tempData[j].triplePoint);
                
                // Update index pointers to the triple intersection points
                for (unsigned int ii = 0; ii < tempData[j].intIndex.size(); ii++) {
                    unsigned int idx = tempData[j].intIndex[ii];
                    intPtsList[idx].triplePointsIdx.push_back(tripIndex + j);
                }
            }    
        }        

        // ***********************
        // Update group numbers **
        // *********************** 
        updateGroups(newPoly, acceptedPoly, encounteredGroups, pstats, newPolyIndex);
    }
    
    // Keep track of how much intersection length we are looising from 'shrinkIntersection()'
    // Calculate and store total original intersection length (all intersections)
    // and actual intersection length, after intersection has been shortened.
    for (unsigned int i = 0; i < tempIntPts.size(); i++) {
        double length = magnitude(tempOriginalIntersection[i].x1 - tempOriginalIntersection[i].x2, 
                                  tempOriginalIntersection[i].y1 - tempOriginalIntersection[i].y2, 
                                  tempOriginalIntersection[i].z1 - tempOriginalIntersection[i].z2);
        
        pstats.originalLength += length;
        
        if (tempIntPts[i].intersectionShortened == true) {
            pstats.intersectionsShortened++;
            
            double newLength = magnitude(tempIntPts[i].x1 - tempIntPts[i].x2, 
                                         tempIntPts[i].y1 - tempIntPts[i].y2, 
                                         tempIntPts[i].z1 - tempIntPts[i].z2);

            pstats.discardedLength += length - newLength;
        }
    }
    return 0;        
}


/********************************************************************************************/
/* Disatance from intersection line to Nodes/Vertices  *************************************/
/*! Checks distance from line of intersection to poly vertices
    Arg 1: Poly to check dist to intersection
    Arg 3: Intersection structure (intersection end points)
    Arg 4: Minimum distance allowed
    Return: 0 - Distance from intersection to vertices are all > 'minDist'
            1 - Na distance less than minDist was found */
bool checkDistanceFromNodes(struct Poly &poly, IntPoints &intPts, double minDist, Stats &pstats) {
    int nNodes = poly.numberOfNodes;
    double dist;
    
    // Intersection dist to poly vertices
    double line[6] = {intPts.x1, intPts.y1, intPts.z1, intPts.x2, intPts.y2, intPts.z2};
    dist = pointToLineSeg(poly.vertices, line);

    for (int i = 1; i < nNodes; i++) {
        int idx = 3*i;
        double temp = pointToLineSeg(&poly.vertices[idx], line);

        // If new distance is less than the last calculated distance...
        if (temp < dist) { 
            dist = temp;
        }
        if (dist < minDist && dist > eps) { 
            pstats.rejectionReasons.closeToNode++;
            return 1; 
        }    
    }
    
    // If it makes it here, no distance less than 'minDist' found
    return 0;
} 


/********************************************************************************/
/******************** Shortest Disatance, point to line seg *********************/
/*! Arg 1: Point in 3D space (array of three doubles)
    Arg 2: Line (array of 6 doubles. Enpoint 1 and end point 2: {x1, y1, z1, x2, y2, z2}
    Return: Returns the shortest distance between the point and the line segment */
double pointToLineSeg(const double *point, const double *line) {
    const double sqrLineLen = sqrMagnitude(line[0]-line[3], line[1]-line[4], line[2]-line[5]);  // i.e. |w-v|^2 -  avoid a sqrt
    if (sqrLineLen < eps) {
        // Line endpoints are equal to each other
        return magnitude(point[0]-line[0], point[1]-line[1], point[2]-line[2]);
    }

    double pL1[3] = { point[0]-line[0], point[1]-line[1], point[2]-line[2] };
    double L1L2[3] = { line[3]-line[0], line[4]-line[1], line[5]-line[2] };

    // Find parameterization for line projection on [0, 1]
    const double t = std::max(0.0, std::min(1.0, dotProduct(pL1, L1L2) / sqrLineLen));

    double projection[3] = { t * L1L2[0], t * L1L2[1], t * L1L2[2] };
    projection[0] += line[0];
    projection[1] += line[1];
    projection[2] += line[2];

    return magnitude(projection[0]-point[0], projection[1]-point[1], projection[2]-point[2]);
}

// Overloaded function 
/*! Arg 1: Point structure. Point in 3D space 
    Arg 2: Line (array of 6 doubles. Enpoint 1 and end point 2: {x1, y1, z1, x2, y2, z2}
    Return: Returns the shortest distance between the point and the line segment */
double pointToLineSeg(const Point &point, const double *line) {
    const double sqrLineLen = sqrMagnitude(line[0]-line[3], line[1]-line[4], line[2]-line[5]);  // i.e. |w-v|^2 -  avoid a sqrt
    if (sqrLineLen < eps) {
        // Line endpoints are equal to each other
        return magnitude(point.x-line[0], point.y-line[1], point.z-line[2]);
    }

    double pL1[3] = { point.x-line[0], point.y-line[1], point.z-line[2] };
    double L1L2[3] = { line[3]-line[0], line[4]-line[1], line[5]-line[2] };

    // Find parameterization for line projection on [0, 1]
    const double t = std::max(0.0, std::min(1.0, dotProduct(pL1, L1L2) / sqrLineLen));

    double projection[3] = { t * L1L2[0], t * L1L2[1], t * L1L2[2] };
    projection[0] += line[0];
    projection[1] += line[1];
    projection[2] += line[2];

    return magnitude(projection[0]-point.x, projection[1]-point.y, projection[2]-point.z);
}


/*******************************************************************************/
/************************* Is Point On Line Segment ****************************/
/*! Arg 1: Point in 3D space, array of three doubles x, y, z
    Arg 2: Line defined by end points, array of 6 doubles
           endPoint1 and endpoint 2, {x1, y1, z1, x2, y2, z2}
    Return: True if the point lies on the line segment
            False otherwise */
bool pointOnLineSeg(const double *pt, const double *line) {

    // A = end pt 1, B = end pt 2, 
    // pt is point we are checking if on line between A and B
    // If mag(A to Pt) + mag(pt to B) = mag(A to B), pt is on line

    // end point A to end point B
    double temp[3] = { line[3]-line[0], line[4]-line[1], line[5]-line[2] };

    double endPttoEndPt_Dist = std::sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2]);

    // end point A to pt
    temp[0] = pt[0] - line[0];
    temp[1] = pt[1] - line[1];
    temp[2] = pt[2] - line[2];

    double endPtToPt_Dist = std::sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2]);

    // pt to end pt B
    temp[0] = line[3] - pt[0];
    temp[1] = line[4] - pt[1];
    temp[2] = line[5] - pt[2];

    double ptToEndPt_Dist = std::sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2]);

    // (end pt A to pt) + (pt to end pt B) - (end pt to end pt)
    // If zero, pt is between endpoints, and on line
    double result  = endPtToPt_Dist + ptToEndPt_Dist - endPttoEndPt_Dist;
    if (-eps < result && result < eps) {
        return true;
    }
    return false;
}


// Overloaded function
/********************************************************************************/
/************************* Is Point On Line Segment ****************************/
/*! Arg 1: Point structure
    Arg 2: Line defined by end points, array of 6 doubles
           endPoint1 and endpoint 2, {x1, y1, z1, x2, y2, z2}
    Return: True if the point lies on the line segment
            False otherwise */
bool pointOnLineSeg(const Point &pt, const double *line) {

    // A = end pt 1, B = end pt 2, 
    // pt is point we are checking if on line between A and B
    // If mag(A to Pt) + mag(pt to B) = mag(A to B), pt is on line

    //end point A to end point B
    double temp[3] = { line[3]-line[0], line[4]-line[1], line[5]-line[2] };

    double endPttoEndPt_Dist = std::sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2]);

    //end point A to pt
    temp[0] = pt.x - line[0];
    temp[1] = pt.y - line[1];
    temp[2] = pt.z - line[2];

    double endPtToPt_Dist = std::sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2]);

    //pt to end pt B
    temp[0] = line[3] - pt.x;
    temp[1] = line[4] - pt.y;
    temp[2] = line[5] - pt.z;

    double ptToEndPt_Dist = std::sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2]);

    // (end pt A to pt) + (pt to end pt B) - (end pt to end pt)
    // if zero, pt is between and on line
    double result  = endPtToPt_Dist + ptToEndPt_Dist - endPttoEndPt_Dist;
    if (-eps < result && result < eps) {
        return true;
    }
    return false;
}


/********************************************************************************/
/****************** Check if nodes are too close to edge ************************/
/*! Checks distances from intersection to poly edges. If the distance is less than 
    h, the intersection is allowed to shrink by %10 of its original length. If 
    the intersection is still closer than h to a poly edge, the polygon is rejected.

    Arg 1: Poly to be tested
    Arg 2: IntPoints intersection to be tested
    Arg 3: Minimum length the intersection is allowed to shinrk to
    Arg 4: Stats program statistics structure, used to report stats on how much 
           intersection length is being reduced by from shrinkIntersection() */
bool checkCloseEdge(Poly &poly1, IntPoints &intPts, double shrinkLimit, Stats &pstats) { 

    // 'line' is newest intersection end points
    double line[6] = {intPts.x1, intPts.y1, intPts.z1, intPts.x2, intPts.y2, intPts.z2};

    // minDist is the minimum distance allowed from an end point to the edge of a polygon
    // if the intersection does not land accross a poly's edge
    double minDist = h;

    // Counts how many endPoints are on the polys edge.
    // If both end points of intersection are on polys edge,
    // we must check the distance from end points to 
    // vertices
    int onEdgeCount = 0;

    for (int i = 0; i < poly1.numberOfNodes; i++) {
        int next;
        int idx = 3*i;
        
        if (i != poly1.numberOfNodes -1) { 
            next = (i+1)*3;
        }
        else{ // If last edge on polygon
            next = 0;
        }    
            
        // Edge is two points, x y and z coords of poly vertices
        double edge[6] = {poly1.vertices[idx],poly1.vertices[idx+1],poly1.vertices[idx+2], 
                         poly1.vertices[next], poly1.vertices[next+1], poly1.vertices[next+2]};
        Point pt; // 'pt' is point of intersection, set in lineSegToLineSeg()

        // Get distances of each point to line
        double endPtsToEdge[4] = { pointToLineSeg(&line[0], edge), pointToLineSeg(&line[3], edge), 
                                   pointToLineSeg(&edge[0], line), pointToLineSeg(&edge[3], line) };
        
        // Sort smallest to largest
        std::sort(endPtsToEdge, endPtsToEdge + 4);

        // If two smallest distances are < h, 
        // the line is almost parallel and closer to edge than h, reject it
        if ((endPtsToEdge[0] < h && endPtsToEdge[1] < h) && endPtsToEdge[0] > eps) {
            return 1;
        }        

        // Minimum dist from poly edge segment to intersection segment
        double dist = lineSegToLineSeg(edge, line, pt);

        if (dist < minDist && dist > eps) {   
            // Try to shrink the intersection slightly in order to 
            // not reject the polygon
            if (shrinkIntersection(intPts, edge, shrinkLimit, h, h) == 1) {
                // Returns one if insterection shrinks to less than .9*h
                return 1;
            }
        }
        else if (dist < eps) {
            // Endpoint is almost exactly on poly's edge, must check 
            // whether the discretized nodes will ne closer 
            // than the minimum allowed distance
            // shrinkIntersection() will check if the descretized intersection points violate any 
            // distance to edge rules  
            // NOTE: Intersections discretize with set size = .5*h
            // Minimum distance to edge must be less than .5*h to allow for angles    
            const static double minDist2 = 0.4 * h;
            if (shrinkIntersection(intPts, edge, shrinkLimit, minDist2, h) == 1) {
                //returns one if insterection shrinks to less than .9*h
                return 1;
            }
            
            onEdgeCount++;

            // If both end points are on the edge we must also check the distnace 
            // of the intersection to the poly vertices. 
            // IF the intersecion is within the polygon, distances less than h to 
            // edges and vertices will be caught by lineSegToLineSeg() in this function.
            if (onEdgeCount >= 2) {
                
                if (checkDistanceFromNodes(poly1, intPts, h, pstats)) {
                    return 1;
                }
            }
        }

    }
    #ifdef DISABLESHORTENINGINT
        if (intPts.intersectionShortened == true) {
            return 1;
        }
    #endif
    
    return 0;
}


/********************************************************************************/
/*****************  Find point of intersection between two lines ****************/
/*! Used in lineSegToLineSeg()
    Arg 1: First end point for line 1
    Arg 2: Array of 3 doubles. Vecotor from second end point
           on line 1 to p1 (first end point)
    Arg 3: First end point for line 2
    Arg 4: Array of 3 doubles. Vecotor from second end point 
           on line 2 to p2 (first end point)
    Return: Point structure of interseciton point if intersections do in fact intersect.
            (in lineSegToLineSeg(), intersection is verified by pointOnLineSeg()) */
Point lineIntersection3D(const double *p1, double *v1, const double *p2, double *v2) {
    normalize(v1);
    normalize(v2);
    
    double v1xv2[3] = {(v1[1]*v2[2])-(v1[2]*v2[1]), (v1[2]*v2[0])-(v1[0]*v2[2]), (v1[0]*v2[1])-(v1[1]*v2[0])};
    double denom = dotProduct(v1xv2, v1xv2);
    double v21[3] = {p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]};
    double v21xv2[3] = {(v21[1]*v2[2])-(v21[2]*v2[1]), (v21[2]*v2[0])-(v21[0]*v2[2]), (v21[0]*v2[1])-(v21[1]*v2[0])};
    double temp[3];
    double temp2 = dotProduct(v21xv2, v1xv2);
    double temp3 = temp2/denom;
    temp[0] = v1[0]*temp3;
    temp[1] = v1[1]*temp3;
    temp[2] = v1[2]*temp3;
        
    Point pt;
    pt.x = temp[0] + p1[0];  
    pt.y = temp[1] + p1[1];  
    pt.z = temp[2] + p1[2];  
    
    return pt;
}


/********************************************************************************/
/************  Closest Distance from Line Seg to Line Seg ***********************/
/*! Calculates the distance between two line segments.
    Also calculates the point of intersection if the lines overlap.

    Arg 1: Array of 6 doubles for line 1 end points:
           {x1, y1, z1, x2, y2, z2}
    Arg 2: Array of 6 doubles for line 2 end points:
           {x1, y1, z1, x2, y2, z2}
    Arg 3: OUTPUT. Point structure object. If lines intersect, pt will contain the
           intersection point.
    Return: Minimum distance between line 1 and line 2 */
double lineSegToLineSeg(const double *line1, const double *line2, Point &pt) {

    // Check if line 1 and line 2 intersect
    const double p1[3] = {line1[0], line1[1], line1[2]};
    const double p2[3] = {line2[0], line2[1], line2[2]};
    double v1[3];
    v1[0] = line1[0] - line1[3];
    v1[1] = line1[1] - line1[4];
    v1[2] = line1[2] - line1[5];
    double v2[3];
    v2[0] = line2[0] - line2[3];
    v2[1] = line2[1] - line2[4];
    v2[2] = line2[2] - line2[5];
    
    double p1p2[3] = {p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]};
    
    if(parallel(v1, v2)) {
        if(magnitude(p1p2[0], p1p2[1], p1p2[2]) < eps || parallel(p1p2, v1) == 1) {
            // If 2 line segs overlap
            if(pointOnLineSeg(line1, line2) == 1 || pointOnLineSeg(&line1[3], line2) == 1) {
                return 0;
            }
            else { // Line segs are colinear but not overlapping
                return lineSegToLineSegSep(line1, line2);
            }    
        }  
        else {// Line segs are parallel but not overlapping
            return lineSegToLineSegSep(line1, line2);
        }
    }    
    else{ // Lines are not parallel
        pt = lineIntersection3D(p1, v1, p2, v2); // Point of intersection if lines intersect
        double temp[3] = {pt.x, pt.y, pt.z};
        if (pointOnLineSeg(temp, line1) && pointOnLineSeg(temp, line2)) { // Case 1: Lines Intersection occurs on the lines
            return 0;
        }
        else {// Case 2: Line Intersection does not occur on both lines, find min distance from 4 endpoints to other line seg
            return lineSegToLineSegSep(line1, line2);
        }
    }
}

/********************************************************************************/
/********** Dist. from line seg to line seg (seperated lines) *******************/
/*! Calculates the minimum distance between two seperated line segments.

    Arg 1: Array of 6 doubles for line 1 end points:
           {x1, y1, z1, x2, y2, z2}
    Arg 2: Array of 6 doubles for line 2 end points:
           {x1, y1, z1, x2, y2, z2}  
    Return: Minimum distance between 'line1' and 'line2' */
double lineSegToLineSegSep(const double *line1, const double *line2) {
    double dist = std::min(pointToLineSeg(line1, line2), pointToLineSeg(&line1[3], line2));
    double temp = std::min(pointToLineSeg(line2, line1), pointToLineSeg(&line2[3], line1));
 
    if (dist < temp) return dist;
    else return temp;
}


/********************************************************************************/
/************** Check for Triple Intersection , get int. point ******************/
/********************************************************************************/
/*! Check for triple intersection features of less than h.
    Returns rejection code if fracture is rejected,  zero if accepted

    Rejection codes: 
    0 = poly accepted
    -10 = triple_intersectionsNotAllowed (rejected triple intersections 
          due to triple intersections not allowed in input file)
    -11 = triple_closeToIntersection (newPoly's intersection landed too close to a previous intersection)
    -12 = triple_smallIntersectionAngle  
    -13 = triple_closeEndPoint   (triple intersection point too close to an endpoint)
    -14 = triple_closeToTriplePt  (new triple point too close to previous triple point) */
int checkForTripleIntersections(IntPoints &intPts, unsigned int count, std::vector<IntPoints> &intPtsList, Poly &newPoly, Poly &poly2, std::vector<TriplePtTempData> &tempData,  std::vector<Point> &triplePoints) {
    
    Point pt;
    double minDist = 1.5*h;
    double intEndPts[6] = {intPts.x1, intPts.y1, intPts.z1, intPts.x2, intPts.y2, intPts.z2};//newest intersection
    
    // Number of intersections already on poly2 
    int n = poly2.intersectionIndex.size();
    // Check new fracure's new intesrsection against previous intersections on poly2
    for (int i = 0; i < n; i++) { 
        unsigned int intersectionIndex = poly2.intersectionIndex[i]; // Index to previous intersecction (old intersection)
        unsigned int intersectionIndex2 = intPtsList.size() + count; // Index to current intersection, if accepted (new intersection)
        
        double line[6] = {intPtsList[intersectionIndex].x1, intPtsList[intersectionIndex].y1, intPtsList[intersectionIndex].z1, intPtsList[intersectionIndex].x2, intPtsList[intersectionIndex].y2, intPtsList[intersectionIndex].z2};

        double dist1 = lineSegToLineSeg(intEndPts, line, pt); //get distance and pt of intersection
        
    if (dist1 >= h) {
        continue;
    }

    if (tripleIntersections == 0 && dist1 < h) {
        return -10; // Triple intersections not allowed (user input option)
    }
    
    if (dist1 > eps && dist1 < h) {
        return -11; // Point too close to other intersection
    }
    
    // Overlaping intersections
    if (dist1 <= eps) {
        // ANGLE CHECK, using definition of dot product: A dot B = Mag(A)*Mag(B) * Cos(angle)
        // Normalize  A and B first. Compare to precalculated values of cos(47deg)= .681998 and cos(133deg)= -.681998
        double U[3] =  {line[3]-line[0], line[4]-line[1], line[5]-line[2]};
        double V[3] = {intPts.x2 - intPts.x1, intPts.y2 - intPts.y1, intPts.z2 - intPts.z1}; //endpoints
        normalize(U);
        normalize(V);
    
        double dotProd = dotProduct(U,V);
    
        if (dotProd < -0.68199836 || dotProd > 0.68199836) { //if angle is less than 47 deg or greater than 133, reject 
            return -12;
        }
    
        // Check that the triple intersection point isn't too close to an endpoint
        double dist2;
        double point[3] = {pt.x, pt.y, pt.z}; // Triple intersection point
        dist1 = euclideanDistance(point,intEndPts);
        dist2 = euclideanDistance(point,&intEndPts[3]);
        if (dist1 < h || dist2 < h) {
            return -13;
        }
        dist1 = euclideanDistance(point,line);
        dist2 = euclideanDistance(point,&line[3]);
        if (dist1 < h || dist2 < h) {
            return -13;
        }
        
        // Check that the triple intersection point isn't too close to previous triple intersection points
        for(unsigned int k = 0; k < intPtsList[intersectionIndex].triplePointsIdx.size(); k++) {
            unsigned int idx =  intPtsList[intersectionIndex].triplePointsIdx[k];
            double triplePt[3] = {triplePoints[idx].x, triplePoints[idx].y,triplePoints[idx].z};
            dist1 = euclideanDistance(point, triplePt);
            if (dist1 < minDist) {
                return -14;
            }
        }
    
        // Look at previously found triple points on current line of intersection,
        // do not save duplicate triple ponits
        // If duplicate point is found, a different intersection may still be needing an update
        // (three intersections per single triple intersection point )
        bool duplicate = 0;
        unsigned int k;
        // See if the found triple pt is already saved
        for (k = 0; k < tempData.size(); k++) {     
            if (std::abs(pt.x - tempData[k].triplePoint.x) < eps 
            &&  std::abs(pt.y - tempData[k].triplePoint.y) < eps 
            &&  std::abs(pt.z - tempData[k].triplePoint.z) < eps) {
                duplicate = 1;
                break;
            }                
        }
        
        // If it is a duplicate triple pt
        if (duplicate == 1) { 
            // The old fracture's intersection needs 
            // a reference to the new triple int pt
            // Save the index to the old fractures intersection
            // which needs updating. If newPoly is accpted
            // the old fracture will be updated 
            tempData[k].intIndex.push_back(intersectionIndex2);
        }
        else{ // Not a duplicate point 
            // Save temp triple point data, store to permanent at end if fracture is accepted
            TriplePtTempData localTemp;
            localTemp.triplePoint = pt;
            localTemp.intIndex.push_back(intersectionIndex);
            localTemp.intIndex.push_back(intersectionIndex2);
            tempData.push_back(localTemp);
        }
    }
}

    // Test distances to triple points on own line of intersection
    // If any triple points are found to be less than 'minDist' to each other, reject.
    unsigned int tripSize = tempData.size(); 
    // Each tempData structure contains 1 triple pt and the intersection index of intersection it is on
    
    if (tripSize != 0 ) {
        unsigned int y = tripSize-1;

        for (unsigned int k = 0; k < y ; k++ ) {
            double point1[3] = {tempData[k].triplePoint.x, tempData[k].triplePoint.y, tempData[k].triplePoint.z};
            for (unsigned int j = k+1; j < tripSize; j++) {
                double point2[3] = {tempData[j].triplePoint.x, tempData[j].triplePoint.y, tempData[j].triplePoint.z};
                double dist = euclideanDistance(point1,point2);
                if ( dist < minDist && dist > eps ) {

                    return -14;
                }
            }
        }
    }
    return 0;
}





