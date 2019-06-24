#include <cmath>
#include <iomanip> // std::setprecision()
#include <iostream>
#include "insertShape.h"
#include "vectorFunctions.h"
#include "mathFunctions.h"
#include "computationalGeometry.h"
#include "structures.h"
#include "input.h"
#include "domain.h"

/*************************************************************/
/***********  Insert User Rects By Coord  ********************/
/*! Inserts user rectangles using defined coordinates
    provided by the user (see input file).
    Intersection checking, FRAM, and rejection/accptance are all contained
    within this function.
    Arg 1: Array for all accepted polygons
    Arg 2: Array for all accepted intersections
    Arg 3: Program statistics structure
    Arg 4: Array of all triple intersection points */
void insertUserRectsByCoord(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints) {
    std::cout << "\n" <<  nRectByCoord << " User Rectangles By Coordinates Defined\n\n";
    
    for (unsigned int i = 0; i < nRectByCoord; i++) {
        Poly newPoly;
        newPoly.familyNum = -2; // Using -2 for all user specified rectangles
        newPoly.vertices = new double[12]; // 4 * {x,y,z}
        // Set number of nodes  - needed for rotations
        newPoly.numberOfNodes = 4;
        int polyVertIdx = i * 12; // Each polygon has 4 vertices (12 elements, 4*{x,y,z}))
        
        // Initialize vertices
        for (int j = 0; j < 4; j++) {
            int vIdx = j * 3;
            newPoly.vertices[vIdx] = userRectCoordVertices[polyVertIdx + vIdx];
            newPoly.vertices[vIdx + 1] = userRectCoordVertices[polyVertIdx + 1 + vIdx];
            newPoly.vertices[vIdx + 2] = userRectCoordVertices[polyVertIdx + 2 + vIdx];
        }
        
        // Check that rectangle lays one a single plane:
        // let xProd1 = cross Product vector (1st node to 2nd node) with vector(1st node to 3rd node)
        // and xProd2 = cross product vector (1st node to 3th node) with vector (1st node to 4th node)
        // Then, cross product xProd1 and xProd2, if this produces zero vector, all coords are on the same plane
        // v1 is vector from first vertice to third vertice
        // Vector from fist node to 3rd node (vector through middle of sqare)
        double v1[3] = {newPoly.vertices[6] - newPoly.vertices[0],
                        newPoly.vertices[7] - newPoly.vertices[1],
                        newPoly.vertices[8] - newPoly.vertices[2]
                       };
        // Vector from first node to 2nd node
        double v2[3] = {newPoly.vertices[3] - newPoly.vertices[0],
                        newPoly.vertices[4] - newPoly.vertices[1],
                        newPoly.vertices[5] - newPoly.vertices[2]
                       };
        double *xProd1 = crossProduct(v2, v1);
        // Vector from fist node to 4th node
        double v3[3] = {newPoly.vertices[9] - newPoly.vertices[0], newPoly.vertices[10] - newPoly.vertices[1], newPoly.vertices[11] - newPoly.vertices[2]};
        double *xProd2 = crossProduct(v3, v1);
        double *xProd3 = crossProduct(xProd1, xProd2); //will be zero vector if all vertices are on the same plane
        //TODO: Error check below is too sensitive. Adjust it.
        // Error check for points not on the same plane
//        if (std::abs(magnitude(xProd3[0],xProd3[1],xProd3[2])) > eps) { //points do not lay on the same plane. reject poly else meshing will fail
        /*        if (!(std::abs(xProd3[0]) < eps && std::abs(xProd3[1]) < eps && std::abs(xProd3[2]) < eps)) {
                    delete[] newPoly.vertices;
                    pstats.rejectedPolyCount++;
                    std::cout << "\nUser Rectangle (defined by coordinates) " << i+1 << " was rejected. The defined vertices are not co-planar.\n";
                    std::cout << "Please check user defined coordinates for rectanle " << i+1 << " in input file\n";
                    delete[] xProd1;
                    delete[] xProd2;
                    delete[] xProd3;
                    continue; //go to next poly
                }    */
        // Set normal vector
        newPoly.normal[0] = xProd1[0]; //x
        newPoly.normal[1] = xProd1[1]; //y
        newPoly.normal[2] = xProd1[2]; //z
        //std::cout << "Normal Vector " << std::setprecision(12)<< newPoly.normal[0] << " " << newPoly.normal[1] << " " << newPoly.normal[2] << "\n";
        normalize(newPoly.normal);
        //std::cout << "Normal Vector " << std::setprecision(12)<< newPoly.normal[0] << " " << newPoly.normal[1] << " " << newPoly.normal[2] << "\n";
        delete[] xProd1;
        delete[] xProd2;
        delete[] xProd3;
        // Set radius (x and y radii might be switched based on order of users coordinates)
        newPoly.xradius = .5 * magnitude(v2[0], v2[1], v2[2]);
        newPoly.yradius = .5 * magnitude(v3[0], v3[1], v3[2]);
        newPoly.aspectRatio = newPoly.yradius / newPoly.xradius;
        // Estimate translation
        // Use midpoint between 1st and 3rd vertices
        // Note: For polygons defined by coordinates, the coordinates
        // themselves provide the translation. We are just filling the
        // translation array for completeness even though the translation
        // array might not be used
        newPoly.translation[0] = .5 * (newPoly.vertices[0] + newPoly.vertices[6]);
        newPoly.translation[1] = .5 * (newPoly.vertices[1] + newPoly.vertices[7]);
        newPoly.translation[2] = .5 * (newPoly.vertices[2] + newPoly.vertices[8]);
        
        if (domainTruncation(newPoly, domainSize) == 1) {
            // Poly completely outside domain
            delete[] newPoly.vertices;
            pstats.rejectionReasons.outside++;
            pstats.rejectedPolyCount++;
            std::cout << "\nUser Rectangle (defined by coordinates) " << i + 1 << " was rejected for being outside the defined domain.\n";
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
            std::cout << "\nUser Defined Rectangular Fracture (Defined By Coordinates) " << (i + 1) << " Accepted\n";
            acceptedPoly.push_back(newPoly); // Save newPoly to accepted polys list
        } else {
            delete[] newPoly.vertices; // Need to delete manually, created with new[]
            pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
            pstats.rejectedPolyCount++;
            std::cout << "\nRejected User Defined Rectangular Fracture (Defined By Coordinates) " << i + 1 << "\n";
            printRejectReason(rejectCode, newPoly);
        }
    } // End loop
    
    delete[] userRectCoordVertices;
}

