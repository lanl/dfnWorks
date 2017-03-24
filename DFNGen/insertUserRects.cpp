#include <cmath>
#include <iostream>
#include "insertShape.h"
#include "vectorFunctions.h"
#include "mathFunctions.h"
#include "computationalGeometry.h"
#include "structures.h"
#include "input.h"
#include "domain.h"
#include "testing.h"


/***********************************************************************/
/********************  Insert User Rectangles  *************************/
/*! Inserts a user defined rectangle into the domain
    Intersection checking, FRAM, and rejection/accptance is all contained
    within this function.
    Arg 1: Array for all accepted polygons
    Arg 2: Array for all accepted intersections
    Arg 3: Program statistics structure
    Arg 4: Array of all triple intersection points */
void insertUserRects(std::vector<Poly>& acceptedPoly, std::vector<IntPoints> &intpts, struct Stats &pstats, std::vector<Point> &triplePoints) {

    std::cout << "\n" << nUserRect << " User Rectangles Defined\n";

    for (int i = 0; i < nUserRect; i++) {
        
        Poly newPoly;
        newPoly.familyNum = -2; // Using -2 for all user specified rectangles

        newPoly.vertices = new double[12]; // 4*{x,y,z}

        // Set number of nodes. Needed for rotations.
        newPoly.numberOfNodes = 4;

        int index = i*3; // Index to start of vertices/nodes
        
        // initializeRectVertices() sets newpoly.xradius, newpoly.yradius, newpoly.aperture
        initializeRectVertices(newPoly, urRadii[i], uraspect[i]);

        // Convert angle to rad if necessary
        float angle = urBeta[i];
        if (urAngleOption == 1 ){
            angle = urBeta[i] * M_PI/180;
        }
        else {
            angle = urBeta[i];
        } 
        
        // Initialize normal to {0,0,1}. need initialized for 3D rotation
        newPoly.normal[0] = 0; //x
        newPoly.normal[1] = 0; //y
        newPoly.normal[2] = 1; //z
        
        // Apply 2d rotation matrix, twist around origin
        // Assumes polygon on x-y plane
        // Angle must be in rad
        applyRotation2D(newPoly, angle);

        // Rotate into 3D from poly.normal to "urnormal", new normal
        normalize(&urnormal[index]);

        // Rotate vertices to urnormal[index] (new normal)
        applyRotation3D(newPoly, &urnormal[index]); 
        
        // Save newPoly's new normal vector
        newPoly.normal[0] = urnormal[index];
        newPoly.normal[1] = urnormal[index+1];
        newPoly.normal[2] = urnormal[index+2];

        // Translate newPoly to urtranslation 
        translate(newPoly, &urtranslation[index]); 
    
        if (domainTruncation(newPoly, domainSize) == 1) {
            //poly completely outside domain
            delete[] newPoly.vertices;
            pstats.rejectionReasons.outside++;
            pstats.rejectedPolyCount++;
            std::cout << "\nUser Rectangle " << i+1 << " was rejected for being outside the defined domain.\n";
            continue; // Go to next poly (go to next iteration of for loop)
        }
        
        createBoundingBox(newPoly);

        // Line of intersection and FRAM                    
        int rejectCode = intersectionChecking(newPoly, acceptedPoly, intpts, pstats, triplePoints);       
        if(rejectCode == 0) {
        // If intersection is ok
            if (newPoly.truncated == 1) { 
                pstats.truncated++;
            }            
            
            // Incriment counter of accepted polys
            pstats.acceptedPolyCount++;     
            
            // Calculate poly's area
            newPoly.area = getArea(newPoly);         

            // Add new rejectsPerAttempt counter
            pstats.rejectsPerAttempt.push_back(0);
         
            std::cout << "\nUser Defined Rectangular Fracture " << (i+1) << " Accepted\n";
            acceptedPoly.push_back(newPoly); // Save newPoly to accepted polys list
        }
        else {
            delete[] newPoly.vertices; // Delete manually, created with new[]
            pstats.rejectedPolyCount++;
            pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
            std::cout << "\nRejected user defined rectangular fracture " << i+1 << "\n";
            printRejectReason(rejectCode, newPoly);
            
            #ifdef TESTING
                exit(1);
            #endif
        
        }    
        
    }//end loop

    delete[] urRadii;
    delete[] uraspect;
    delete[] urBeta;
    delete[] urtranslation;
    delete[] urnormal;
                
}
    
    

    
    
