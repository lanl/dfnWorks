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
#include "logFile.h"

using std::cout;
using std::endl;
using std::string;

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


/**********************************************************************/
/*! Set translation, xradius, yradius, and aspectRatio of a user polygon
    from its vertices. Requires poly.normal to be set (unit length).
    translation: area-weighted centroid of the planar polygon.
    xradius: largest centroid-to-vertex distance (the enclosing radius).
    yradius: largest in-plane extent perpendicular to the xradius direction.
    Arg 1: Poly with vertices, numberOfNodes, and normal set */
static void setUserPolygonCenterAndRadii(Poly &poly) {
    const int n = poly.numberOfNodes;
    const double *v = poly.vertices;
    // Vertex mean, used as the fan origin
    double m[3] = {0, 0, 0};

    for (int i = 0; i < n; i++) {
        for (int d = 0; d < 3; d++) {
            m[d] += v[3 * i + d] / n;
        }
    }

    // Area-weighted centroid from a triangle fan about the vertex mean
    double c[3] = {0, 0, 0};
    double totalArea = 0;

    for (int i = 0; i < n; i++) {
        const double *a = &v[3 * i];
        const double *b = &v[3 * ((i + 1) % n)];
        double ea[3] = {a[0] - m[0], a[1] - m[1], a[2] - m[2]};
        double eb[3] = {b[0] - m[0], b[1] - m[1], b[2] - m[2]};
        double *x = crossProduct(ea, eb);
        double area = 0.5 * dotProduct(x, poly.normal); // signed area
        delete[] x;

        for (int d = 0; d < 3; d++) {
            c[d] += area * (m[d] + a[d] + b[d]) / 3.0;
        }

        totalArea += area;
    }

    if (std::fabs(totalArea) > 1e-12) {
        for (int d = 0; d < 3; d++) {
            c[d] /= totalArea;
        }
    } else {
        for (int d = 0; d < 3; d++) {
            c[d] = m[d];
        }
    }

    for (int d = 0; d < 3; d++) {
        poly.translation[d] = c[d];
    }

    // xradius: farthest vertex from the centroid
    double xr = 0;
    int far = 0;

    for (int i = 0; i < n; i++) {
        double r = magnitude(v[3 * i] - c[0], v[3 * i + 1] - c[1], v[3 * i + 2] - c[2]);

        if (r > xr) {
            xr = r;
            far = i;
        }
    }

    // yradius: largest extent along the in-plane direction perpendicular
    // to the centroid -> farthest-vertex direction
    double e1[3] = {v[3 * far] - c[0], v[3 * far + 1] - c[1], v[3 * far + 2] - c[2]};
    double *e2 = crossProduct(poly.normal, e1);
    double e2mag = magnitude(e2[0], e2[1], e2[2]);
    double yr = 0;

    if (e2mag > 0) {
        for (int i = 0; i < n; i++) {
            double p[3] = {v[3 * i] - c[0], v[3 * i + 1] - c[1], v[3 * i + 2] - c[2]};
            double s = std::fabs(dotProduct(p, e2)) / e2mag;

            if (s > yr) {
                yr = s;
            }
        }
    }

    delete[] e2;
    poly.xradius = xr;
    poly.yradius = yr;
    poly.aspectRatio = (xr > 0) ? yr / xr : 1;
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
    std::string logString = "Domain Size " + to_string(domainSize[0]) + " " + to_string(domainSize[1]) + " " + to_string(domainSize[2]);
    logger.writeLogFile(INFO,  logString);
    logString = "Reading User Defined Polygons from " + polygonFile;
    logger.writeLogFile(INFO,  logString);
    std::ifstream file;
    file.open(polygonFile.c_str(), std::ifstream::in);
    checkIfOpen(file, polygonFile);
    searchVar(file, "nPolygons:");
    file >> nPolygonByCoord;
    logString = "There are " + to_string(nPolygonByCoord) + " polygons\n";
    logger.writeLogFile(INFO,  logString);
    acceptedPoly.reserve(nPolygonByCoord);
    
    for (unsigned int i = 0; i < nPolygonByCoord; i++) {
        Poly newPoly;
        RejectedUserFracture rejectedUserFracture;
        // file >> familyNum;
        newPoly.familyNum = -3;
        file >> nPolyNodes;
        //std::cout << "There are " << nPolyNodes <<" nodes in this polygon\n";
        newPoly.numberOfNodes = nPolyNodes;
        newPoly.vertices = new double[3 * nPolyNodes ]; // 3 * number of nodes
        getPolyCoords(file, newPoly.vertices, nPolyNodes);
        /*
        int idx = 0;
        for(unsigned int j = 0; j < nPolyNodes; j++){
           idx = j*3;
           std::cout << newPoly.vertices[idx] << " " << newPoly.vertices[idx+1] << " " << newPoly.vertices[idx+2] << "\n";
        }
        */
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
        // Center, radii, and aspect ratio from the actual vertices.
        // Downstream tools (e.g., mapdfn_ecpm) treat a fracture as a disk of
        // radius xradius about translation, so translation must be the
        // polygon centroid and xradius must enclose every vertex.
        setUserPolygonCenterAndRadii(newPoly);
        
        if (domainTruncation(newPoly, domainSize) == 1) {
            // Poly completely outside domain
            pstats.rejectionReasons.outside++;
            pstats.rejectedPolyCount++;
            logString = "User Polygon (defined by coordinates) " + to_string(i + 1) + " was rejected for being outside the defined domain.\n";
            logger.writeLogFile(ERROR,  logString);
            int idx = 0;
            
            for(unsigned int j = 0; j < nPolyNodes; j++) {
                idx = j * 3;
                logString = to_string(newPoly.vertices[idx]) + " " + to_string(newPoly.vertices[idx + 1]) + " " + to_string(newPoly.vertices[idx + 2]) + "\n";
                logger.writeLogFile(INFO,  logString);
            }
            
            rejectedUserFracture.id = i + 1;
            rejectedUserFracture.userFractureType  = -3;
            pstats.rejectedUserFracture.push_back(rejectedUserFracture);
            delete[] newPoly.vertices;
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
            logString = "User Defined Polygon Fracture (Defined By Coordinates) " + to_string((i + 1)) + " Accepted\n";
            logger.writeLogFile(INFO,  logString);
            acceptedPoly.push_back(newPoly); // Save newPoly to accepted polys list
            //std::cout << "size of accepted Poly " << acceptedPoly.size() << std::endl;
        } else  {
            delete[] newPoly.vertices; // Need to delete manually, created with new[]
            pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
            pstats.rejectedPolyCount++;
            logString = "Rejected User Defined Polygon Fracture (Defined By Coordinates) " + to_string(i + 1) + "\n";
            logger.writeLogFile(INFO,  logString);
            printRejectReason(rejectCode, newPoly);
            rejectedUserFracture.id = i + 1;
            rejectedUserFracture.userFractureType  = -3;
            pstats.rejectedUserFracture.push_back(rejectedUserFracture);
        }
    }
    
    file.close();
}
