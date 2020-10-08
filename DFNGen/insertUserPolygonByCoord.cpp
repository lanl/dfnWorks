#include <cmath>
#include <iostream>
#include <random>
#include "insertShape.h"
#include "vectorFunctions.h"
#include "mathFunctions.h"
#include "computationalGeometry.h"
#include "structures.h"
#include "input.h"
#include "domain.h"
#include "readInputFunctions.h"

/**********************************************************************/
/**********************************************************************/
/*! Used to read in ellipse coordinates when the user is using
    user ellipses defined by coordinates option.
    Arg 1: ifstream file object
    Arg 2: OUTPUT. Pointer to array to store the coordinates
    Arg 3: Number of ellipses
    Arg 4: Number of points per ellipse */
void getPolyCoords(std::ifstream & stream, double *outAry, int nVertices) {
    char ch;
    
    for (int i = 0; i < nVertices; i++) {
        int x = i * 3;
        stream >> ch >> outAry[x]   >> ch >> outAry[x + 1]  >> ch >> outAry[x + 2]  >> ch;
    }
}


/****************************************************************/
/***********  Insert User Polygon By Coord  ********************/
/*! Inserts user polygon using defined coordinates
    provided by the user (see input file).
    Intersection checking, FRAM, and rejection/acceptance are all contained
    within this function.
    Arg 1: Array for all accepted polygons
    Arg 2: Array for all accepted intersections
    Arg 3: Program statistics structure
    Arg 4: Array of all triple intersection points */
void insertUserPolygonByCoord(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints) {
    unsigned int nPolygonByCoord;
    unsigned int nPolyNodes;
    //int familyNum;
    std::cout << "Reading User Defined Polygons from " << polygonFile << "\n";
    std::ifstream file;
    file.open(polygonFile.c_str(), std::ifstream::in);
    checkIfOpen(file, polygonFile);
    searchVar(file, "nPolygons:");
    file >> nPolygonByCoord;
    std::cout << "There are " << nPolygonByCoord << " polygons\n";
    
    for (unsigned int i = 0; i < nPolygonByCoord; i++) {
        Poly newPoly;
        // file >> familyNum;
        newPoly.familyNum = -3;
        file >> nPolyNodes;
        // std::cout << "There are " << nPolyNodes <<" nodes in this polygon\n";
        newPoly.numberOfNodes = nPolyNodes;
        newPoly.vertices = new double[3 * nPolyNodes ]; // 3 * number of nodes
        getPolyCoords(file, newPoly.vertices, nPolyNodes);
        // int idx = 0;
        // for(unsigned int j = 0; j < nPolyNodes; j++){
        //    idx = j*3;
        //    std::cout << newPoly.vertices[idx] << " " << newPoly.vertices[idx+1] << " " << newPoly.vertices[idx+2] << "\n";
        // }
        // Get a normal vector
        // Vector from fist node to node across middle of polygon
        int midPtIdx = 3 * (int) (nPolyNodes / 2);
        
        if (nPolyNodes == 3) {
            midPtIdx = 8;
        }
        
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
        //std::cout << "Normal Vector " << newPoly.normal[0]<<" "<< newPoly.normal[1] << "  " << newPoly.normal[2] << "\n";
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
            std::cout << "\nUser Polygon (defined by coordinates) " << i + 1 << " was rejected for being outside the defined domain.\n";
            continue; // Go to next poly (go to next iteration of for loop)
        }
        
        createBoundingBox(newPoly);
        // Line of intersection and FRAM
        int rejectCode = intersectionChecking(newPoly, acceptedPoly, intpts, pstats, triplePoints);
        
        if(rejectCode == 0) {
            // Incriment counter of accepted polys
            pstats.acceptedPolyCount++;
            // Calculate poly's area
            newPoly.area = getArea(newPoly);
            // Add new rejectsPerAttempt counter
            pstats.rejectsPerAttempt.push_back(0);
            std::cout << "\nUser Defined Polygon Fracture (Defined By Coordinates) " << (i + 1) << " Accepted\n";
            acceptedPoly.push_back(newPoly); // Save newPoly to accepted polys list
        } else  {
            delete[] newPoly.vertices; // Need to delete manually, created with new[]
            pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
            pstats.rejectedPolyCount++;
            std::cout << "\nRejected User Defined Polygon Fracture (Defined By Coordinates) " << i + 1 << "\n";
            printRejectReason(rejectCode, newPoly);
        }
    }
    
    file.close();
}
