#include "removeFractures.h"
#include "computationalGeometry.h"
#include "structures.h"
#include "input.h"
#include <vector>
#include <algorithm>
#include <iostream>

/***********************************************************************/
/***********  Remove Fractures Smaller Than Minimum Size  **************/
// Function is designed to be used AFTER DFN generation
// Originally created to compare the difference in distributions 
// if small fractures were removed after a DFN was generated 
// as opposed limiting their insertion during DFN generation.
//
// The minimum size options in the input files will still be used. 
// If the user wishes to also removeFractures after DFN generation,
// 'minSize' here must be larger than the minimum size fractures in the 
// input file. Fratrues with radii less than 'minSize' will be removed
// after DFN has been created.
// Arg 1: Minimum size. All fractures smaller than 'minSize' will be
//        removed.
// Arg 2: Array of accepted polygons
// Arg 3: Array of accepted intersections
// Arg 4: Array of all triple intersection points
// Arg 5: Stats structure (DFN Statisctics) 
//
// NOTE: Must be executed before getCluster()
//       This funciton rebuilds the DFN. Using getCluster() before this 
//       funciton executes causes undefined behavior. 
void removeFractures(double minSize, std::vector<Poly> &acceptedPolys, std::vector<IntPoints> &intPts, std::vector<Point> triplePoints, Stats &pstats) {

    std::vector<Poly> finalPolyList;
    
    // Clear GroupData
    pstats.groupData.clear();
    // Clear FractGroup 
    pstats.fractGroup.clear();
    // Clear Triple Points
    triplePoints.clear(); 
    // Clear IntPoints
    intPts.clear();

    // Re-init nextGroupNum
    pstats.nextGroupNum = 1;

    for (unsigned int i = 0; i < acceptedPolys.size(); i++) {

        if (acceptedPolys[i].xradius < minSize) {
            delete[] acceptedPolys[i].vertices;
            continue;
        }

        Poly newPoly = acceptedPolys[i];

        newPoly.groupNum = 0; // Reset cluster group number 
    
        newPoly.intersectionIndex.clear(); // Remove ref to old intersections

        // Find line of intersection and FRAM check
        int rejectCode = intersectionChecking(newPoly, finalPolyList, intPts, pstats, triplePoints);

        // IF POLY ACCEPTED:
        if (rejectCode == 0) { // Intersections are ok

            // SAVING POLYGON (intersection and triple points saved witchin intersectionChecking())        
            finalPolyList.push_back(newPoly); // SAVE newPoly to accepted polys list
        }

        else { // Poly rejected

            std::cout << "\nError rebuilding dfn, previously accepted fracture was rejected during DFN rebuild.\n";
        }
    }

    std::cout << "Rebuilding DFN complete.\n";

    acceptedPolys.clear();
    acceptedPolys = finalPolyList;
}


