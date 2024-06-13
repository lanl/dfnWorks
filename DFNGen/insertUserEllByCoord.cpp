#include <cmath>
#include <iostream>
#include "insertShape.h"
#include "vectorFunctions.h"
#include "mathFunctions.h"
#include "computationalGeometry.h"
#include "structures.h"
#include "input.h"
#include "domain.h"

/****************************************************************/
/***********  Insert User Ellipses By Coord  ********************/
/*! Inserts user ellipses using defined coordinates
    provided by the user (see input file).
    Intersection checking, FRAM, and rejection/accptance are all contained
    within this function.
    Arg 1: Array for all accepted polygons
    Arg 2: Array for all accepted intersections
    Arg 3: Program statistics structure
    Arg 4: Array of all triple intersection points */
void insertUserEllByCoord(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints) {
    std::cout << "\n" <<  nEllByCoord << " User Ellipses By Coordinates Defined\n\n";
    
    for (unsigned int i = 0; i < nEllByCoord; i++) {
        Poly newPoly;
        RejectedUserFracture rejectedUserFracture;
        newPoly.familyNum = -1; // Using -1 for all user specified ellipses
        newPoly.vertices = new double[3 * nEllNodes]; // 3 * number of nodes
        // Set number of nodes  - needed for rotations
        newPoly.numberOfNodes = nEllNodes;
        int polyVertIdx = i * 3 * nEllNodes; // Each polygon has nEllNodes * 3 vertices
        
        // Initialize vertices
        for (unsigned int j = 0; j < nEllNodes; j++) {
            int vIdx = j * 3;
            newPoly.vertices[vIdx] = userEllCoordVertices[polyVertIdx + vIdx];
            newPoly.vertices[vIdx + 1] = userEllCoordVertices[polyVertIdx + 1 + vIdx];
            newPoly.vertices[vIdx + 2] = userEllCoordVertices[polyVertIdx + 2 + vIdx];
        }
        
        // Get a normal vector
        // Vector from fist node to node accross middle of polygon
        int midPtIdx = 3 * (int) (nEllNodes / 2);
        double v1[3] = {newPoly.vertices[midPtIdx] - newPoly.vertices[0],
                        newPoly.vertices[midPtIdx + 1] - newPoly.vertices[1],
                        newPoly.vertices[midPtIdx + 2] - newPoly.vertices[2]
                       };
        // Vector from first node to 2nd node
        double v2[3] = {newPoly.vertices[3] - newPoly.vertices[0],
                        newPoly.vertices[4] - newPoly.vertices[1],
                        newPoly.vertices[5] - newPoly.vertices[2]
                       };
        double *xProd1 = crossProduct(v2, v1);
        // Set normal vector
        newPoly.normal[0] = xProd1[0]; //x
        newPoly.normal[1] = xProd1[1]; //y
        newPoly.normal[2] = xProd1[2]; //z
        normalize(newPoly.normal);
        delete[] xProd1;
        // Estimate radius
        newPoly.xradius = .5 * magnitude(v2[0], v2[1], v2[2]); // across middle if even number of nodes
        int tempIdx1 = 3 * (int) (midPtIdx / 2) ; // Get idx for node 1/4 around polygon
        int tempIdx2 = 3 * (tempIdx1 + midPtIdx);  // Get idx for node 3/4 around polygon
        // across middle close to perpendicular to xradius magnitude calculation
        newPoly.yradius = .5 * euclideanDistance(&newPoly.vertices[tempIdx1], &newPoly.vertices[tempIdx2]);
        newPoly.aspectRatio = newPoly.yradius / newPoly.xradius;
        // Estimate translation (middle of poly)
        // Use midpoint between 1st and and half way around polygon
        // Note: For polygons defined by coordinates, the coordinates
        // themselves provide the translation. We need to estimate the center
        // of the polygon and init. the translation array
        newPoly.translation[0] = .5 * (newPoly.vertices[0] + newPoly.vertices[midPtIdx]);
        newPoly.translation[1] = .5 * (newPoly.vertices[1] + newPoly.vertices[midPtIdx + 1]);
        newPoly.translation[2] = .5 * (newPoly.vertices[2] + newPoly.vertices[midPtIdx + 2]);
        
        if (domainTruncation(newPoly, domainSize) == 1) {
            // Poly completely outside domain
            delete[] newPoly.vertices;
            pstats.rejectionReasons.outside++;
            pstats.rejectedPolyCount++;
            std::cout << "\nUser Ellipse (defined by coordinates) " << i + 1 << " was rejected for being outside the defined domain.\n";
            rejectedUserFracture.id = i + 1;
            rejectedUserFracture.userFractureType  = -1;
            pstats.rejectedUserFracture.push_back(rejectedUserFracture);
            continue; // Go to next poly (go to next iteration of for loop)
        }
        
        createBoundingBox(newPoly);
        // Line of intersection and FRAM
        int rejectCode = intersectionChecking(newPoly, acceptedPoly, intpts, pstats, triplePoints);
        
        if(rejectCode == 0) {
            // If intersection is ok (FRAM passed all tests)
            if (newPoly.truncated == 1) {
                pstats.truncated++;
            }
            
            // Incriment counter of accepted polys
            pstats.acceptedPolyCount++;
            // Calculate poly's area
            newPoly.area = getArea(newPoly);
            // Add new rejectsPerAttempt counter
            pstats.rejectsPerAttempt.push_back(0);
            std::cout << "\nUser Defined Elliptical Fracture (Defined By Coordinates) " << (i + 1) << " Accepted\n";
            acceptedPoly.push_back(newPoly); // Save newPoly to accepted polys list
        } else {
            delete[] newPoly.vertices; // Need to delete manually, created with new[]
            pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
            pstats.rejectedPolyCount++;
            std::cout << "\nRejected Eser Defined Elliptical Fracture (Defined By Coordinates) " << i + 1 << "\n";
            printRejectReason(rejectCode, newPoly);
            rejectedUserFracture.id = i + 1;
            rejectedUserFracture.userFractureType  = -1;
            pstats.rejectedUserFracture.push_back(rejectedUserFracture);
        }
    } // End loop
    
    delete[] userEllCoordVertices;
}

