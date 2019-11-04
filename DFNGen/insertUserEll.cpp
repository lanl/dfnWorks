#include <cmath>
#include <iostream>
#include "insertShape.h"
#include "vectorFunctions.h"
#include "mathFunctions.h"
#include "computationalGeometry.h"
#include "input.h"
#include "generatingPoints.h"
#include "domain.h"
#include "testing.h"

/***********************************************************************/
/*********************  Insert User Ellipse  ***************************/
/*! Inserts a user defined ellipse into the domain.
    Intersection checking, FRAM, and rejection/accptance are all called
    within this function.
    Arg 1: Array for all accepted polygons
    Arg 2: Array for all accepted intersections
    Arg 3: Program statistics structure
    Arg 4: Array of all triple intersection points */
void insertUserEll(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints) {
    std::cout << "\n" << nUserEll << " User Ellipses Defined\n\n";
    
    for (int i = 0; i < nUserEll; i++) {
        int index = i * 3; // Index to start of vertices/nodes
        Poly newPoly; // New poly/fracture to be tested
        newPoly.familyNum = -1; // Using -1 for all user specified ellipses
        newPoly.vertices = new double[uenumPoints[i] * 3];
        // Set number of nodes  - needed for rotations
        newPoly.numberOfNodes = uenumPoints[i];
        // Initialize translation data
        newPoly.translation[0] = uetranslation[index];
        newPoly.translation[1] = uetranslation[index + 1];
        newPoly.translation[2] = uetranslation[index + 2];
        // Generate theta array used to place vertices
        float *thetaAry;
        generateTheta(thetaAry, ueaspect[i], uenumPoints[i]);
        // Initialize vertices on x-y plane
        initializeEllVertices(newPoly, ueRadii[i], ueaspect[i], thetaAry, uenumPoints[i]);
        delete[] thetaAry;
        // Convert angle to rad if necessary
        float angle = ueBeta[i];
        
        if (ueAngleOption == 1 ) {
            angle = ueBeta[i] * M_PI / 180;
        } else {
            angle = ueBeta[i];
        }
        
        // Initialize normal to {0,0,1}. need initialized for 3D rotation
        newPoly.normal[0] = 0; //x
        newPoly.normal[1] = 0; //y
        newPoly.normal[2] = 1; //z
        // Apply 2d rotation matrix, twist around origin
        // Assumes polygon on x-y plane
        // Angle must be in rad
        applyRotation2D(newPoly, angle);
        // Normalize user denined normal vector
        normalize(&uenormal[index]);
        // Rotate vertices to uenormal[index] (new normal)
        applyRotation3D(newPoly, &uenormal[index]);
        // Save newPoly's new normal vector
        newPoly.normal[0] = uenormal[index];
        newPoly.normal[1] = uenormal[index + 1];
        newPoly.normal[2] = uenormal[index + 2];
        // Translate newPoly to uetranslation
        translate(newPoly, &uetranslation[index]);
        
        if (domainTruncation(newPoly, domainSize) == 1) {
            // Poly completely outside domain
            delete[] newPoly.vertices;
            pstats.rejectionReasons.outside++;
            pstats.rejectedPolyCount++;
            std::cout << "\nUser Ellipse " << i + 1 << " was rejected for being outside the defined domain.\n";
            continue; // Go to next poly (go to next iteration of for loop)
        }
        
        createBoundingBox(newPoly);
        // Line of intersection and FRAM
        int rejectCode = intersectionChecking(newPoly, acceptedPoly, intpts, pstats, triplePoints);
        
        if(rejectCode == 0) {//if intersection is ok
            if (newPoly.truncated == 1) {
                pstats.truncated++;
            }
            
            // Incriment counter of accepted polys
            pstats.acceptedPolyCount++;
            // Calculate poly's area
            newPoly.area = getArea(newPoly);
            // Add new rejectsPerAttempt counter
            pstats.rejectsPerAttempt.push_back(0);
            std::cout << "User Defined Elliptical Fracture " << (i + 1) << " Accepted\n";
            acceptedPoly.push_back(newPoly); // Save newPoly to accepted polys list
        } else {
            delete[] newPoly.vertices; // Need to delete manually, created with new[]
            pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
            pstats.rejectedPolyCount++;
            std::cout << "\nRejected User Defined Elliptical Fracture " << i + 1 << "\n";
            printRejectReason(rejectCode, newPoly);
#ifdef TESTING
            exit(1);
#endif
        }
        
        std::cout << "\n\n";
    } // End loops
    
    delete[] ueRadii;
    delete[] ueaspect;
    delete[] ueBeta;
    delete[] uetranslation;
    delete[] uenormal;
    delete[] uenumPoints;
}




