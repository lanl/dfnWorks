#include <vector>
#include <iostream>
#include "clusterGroups.h"
#include "structures.h"
#include "input.h"
#include "mathFunctions.h"

/*  This code goes through all the polygons accepted into the domain and returns the indexes to those polygons
    which match the users boundary faces option.
    Isoloated fractures and Polygons with no intersections are removed

groupData structure:
***********************
    groupData keeps information as to how many polygons are in the group or cluster. It also keeps
    track of the boundary faces which the cluster is in contact with. There is also a valid variable (0 or 1).
    If a polygon connects two different groups, one of the groups is merged together with the other. The one which
    nolonger exists has it's valid variable set to 0.

    The groupData structure array, or vector, is aligned with the group numbers. If you want to know about group 3 for
    example, you will look at groupData[ (3-1) ], minus 1 because the array starts at 0 while groups start at 1.
    If valid = 1 in the structure, that group still exists and has not been merged

fractGroups structure:
*************************
    fractGroups[] holds the actual pointers/index numbers to the polygon array along with the group number. Unlike
    groupData[] described above, fractGroups does not stay aligned to group numbers. To keep from copying, deleting, and
    re-allocating memory when groups merge together, we simply change the variable groupNum to the new group number.

    Because of this, there will be multiples of the same group numbers, but with different polygons listed. To get all the
    polygons from a group we must search the fractGroups array for all matching groups
*/

/***********************************************************************************/
/*********************  Get Matching Fracture Clusters  ****************************/
/*!
    Uses boundaryFaces input option to get the wanted fracture
    cluster before writing output files.

    NOTE: 'boundaryFaces' array is a global variable

    Arg 1: Program statistics structure
    Return: Array (std vsector) of indices to fractures which remained after isolated and
            non-matching boundary faces fracture removal.
*/
std::vector<unsigned int> getCluster(Stats &pstats) {
    // The max number of groups is pstats.nextGroupNum - 1
    std::vector<unsigned int> matchingGroups;
    std::vector<unsigned int> finalPolyList;
    //int keepIsolated = 1;
    
    std::cout << "In cluster groups\n";
    std::cout << "Number of fractures: "<< pstats.acceptedPolyCount << "\n";
    std::cout << "Number of groups: "<< pstats.groupData.size() << "\n";

    if (keepIsolatedFractures == 0){
    // NOTE: (groupNumber-1) = corresponding groupData structures' index of the arary
    //       similarly, the index of groupData + 1 = groupNumber (due to groupNumber starting at 1, array starting at 0)

        // Find all matching groups:
        // Get matching groups from pstats.groupData[]
        for (unsigned int i = 0; i < pstats.groupData.size(); i++) {
            // If the data is valid, meaning that group still exists (hasn't been merged to a new group) and
            // if the group has more than 1 fracture meaning there are intersections and
            // the cluster matches the requirements of the user's boundaryFaces option
            if (ignoreBoundaryFaces == 0) {
                if (pstats.groupData[i].valid == 1 && pstats.groupData[i].size > 1  && facesMatch(boundaryFaces, pstats.groupData[i].faces)) {
                    matchingGroups.push_back(i + 1); //save matching group number
                }
            } else { // Get all cluster groups
                if (pstats.groupData[i].valid == 1 && pstats.groupData[i].size > 1) {
                    matchingGroups.push_back(i + 1); // Save matching group number
                }
            }
        }
        if (keepOnlyLargestCluster == 1 && matchingGroups.size() > 1) {
            // If only keeping the largest cluster, find group with largest size
            // Initialize largestGroup
            unsigned int largestGroup = matchingGroups[0];
            
            for (unsigned int i = 0; i < matchingGroups.size(); i++) {
                // If largest group < current group, the current group is the new largest group
                if (largestGroup < pstats.groupData[matchingGroups[i] - 1].size) {
                    largestGroup = matchingGroups[i];
                }
            }
            
            matchingGroups.clear(); // Clear group numbers
            matchingGroups.push_back(largestGroup); // Save only the largest group
        }

        // Gather the final polygon numbers/indecies.
        for (unsigned int i = 0; i < matchingGroups.size(); i++) {
            for (unsigned int k = 0; k < pstats.fractGroup.size(); k++) {
                if (matchingGroups[i] == pstats.fractGroup[k].groupNum) {
                    // If the groupNumbers match
                    // copy all poly indecies of matching group
                    for (unsigned int j = 0; j < pstats.fractGroup[k].polyList.size(); j++) {
                        finalPolyList.push_back(pstats.fractGroup[k].polyList[j]);
                    }
                }
            }
        }
    }
    else{
        std::cout << "Number of fractures: "<< pstats.acceptedPolyCount << "\n";
        for (unsigned int i = 0; i < pstats.acceptedPolyCount; i++) {
            finalPolyList.push_back(i);
        }
    }
    return finalPolyList;
}


/***********************************************************************************/
/*******  Test if Boundary Faces Option Match User's Desired Boundary Faces ********/
/*!
    Compares the user's faces option to a fracture cluster
    Arg 1: Boundary faces user input option array ('boundaryFaces' in input file)
    Arg 2: Fracture cluter's boundary faces array.
           Similar to 'boundaryFaces' input option, but denotes which faces the
           fracture cluster connects to.
    Return: 0 - If faces meet user's facesOption requirements
            1 - If faces do not meet requirements
*/
bool facesMatch(bool *facesOption, bool *faces) {
    for (int i = 0; i < 6; i++) {
        // If the user specified the face, check if faces match
        if (facesOption[i] == 1) {
            if ((facesOption[i] & faces[i]) == 0) {
                return 0;
            }
        }
    }
    
    return 1;
}


/********************  Assign New Polygon to a Cluster  ****************************/
/***********************************************************************************/
/*!
    Assigns a new polygon/fracture to a new cluster group number.
    Assumes 'newPoly' does not intersect with any other fractures.
    Arg 1: New polygon
    Arg 2: Program stats structure
    Arg 3: Index of 'newPoly' in the 'acceptedPoly' array (array of all accepted polys)
*/
void assignGroup(Poly &newPoly, Stats &pstats, int newPolyIndex) {
    newPoly.groupNum = pstats.nextGroupNum;
    GroupData newGroupData; // Keeps fracture cluster data
    // Copy newPoly faces info to groupData
    OR(newGroupData.faces, newPoly.faces);
    // Incriment groupData's poly count
    newGroupData.size++;
    pstats.groupData.push_back(newGroupData); // Save boundary face information to permanent location
    FractureGroups newGroup; // 'newPoly' had no intersections, put it in a new group
    newGroup.groupNum = pstats.nextGroupNum; // Assign new group # to newGroup
    pstats.nextGroupNum++;
    newGroup.polyList.push_back(newPolyIndex); // Save index (number) of newPoly
    pstats.fractGroup.push_back(newGroup);
}




/**************************  Update Cluster Groups  ********************************/
/***********************************************************************************/
/*!
    Updates fracture cluster group data for the addition of 'newPoly'.

    If 'newPoly' did not bridge any clusters together, 'newPoly' is added to the cluster of
    the first polygon it intersected with. The cluster groups  boundary connectivity data is
    updated, clusters fracture count is incremented, and 'newPoly' is added to
    the list of polygons.

    If 'newPoly' bridged two or more clusters, the function also merges the multiple
    cluster groups into a single group. 'newPoly' is first added to group of the first
    fracture it intersected with. Then, any remaining cluster groups 'newPoly' intersected with
    will have their group number changed to match that of 'newPolys' group number (see struct FractureGroups).
    Inside the GroupData structure, all polygons will have their group number updated to the new group number.
    Once polygons and struct FractureGroups have been updated, the FractureGroups corresponding GroupData
    structure will have its valid bit set to false. (This is more efficient than deleting the GroupData
    element from its array, which causes memory re-allocation and copying).

    The GroupData structure contains information about it's corresponding FractureGroups structure (see GroupData).
    To access the cooresponding GroupData structure from a cluster group number, the index to the GroupData array
    within the Stats structure (pstats variable) will be the the cluster group number subtracted by 1.
    e.g. If you need to access the GroupData structure for cluster group 10, it will be the variable:
         pstats.groupData[10-1]
    To access the corresponding FractureGroups structure for a cluster group number, you must search the FractureGroups
    structure array and search for ALL matching group numbers (pstats.fractGroup[i].groupNum).

    Arg 1: Reference to new polygon
    Arg 2: Array of all accepted polygons
    Arg 3: Array of group numbers for  any other bridged fracture cluster groups
    Arg 4: Program statistics structure (contains fracture cluster data)
    Arg 5: Index of 'newPoly' once placed into the array of all accepted polygons (arg 2)
*/

void updateGroups(Poly &newPoly, std::vector<Poly> &acceptedPoly, std::vector<unsigned int> &encounteredGroups, Stats &pstats, int newPolyIndex) {
    if (encounteredGroups.size() == 0) {
        // 'newPoly' didn't encounter more than 1 other group of fractures
        // Save newPoly to the group structure
        unsigned int i = 0;
        // Update boundary face info
        OR(pstats.groupData[newPoly.groupNum - 1].faces, newPoly.faces);
        // NOTE: Groups start at 1, but array starts at zero hence the groupNum-1 for index
        // Incriment the groups size for the new polygon
        pstats.groupData[newPoly.groupNum - 1].size++;
        
        // Search for group newPoly belongs to and add newPoly to it's list, add to first matching group found
        while (pstats.fractGroup[i].groupNum != newPoly.groupNum && i != pstats.fractGroup.size()) {
            i++;
        }
        
        // Error check
        if (i == pstats.fractGroup.size() && pstats.fractGroup[i].groupNum != newPoly.groupNum ) {
            std::cout << "ERROR: Group not found (computationalGeometry.cpp)\n";
        }
        
        // Add newPoly to fracture/cluster group
        pstats.fractGroup[i].polyList.push_back(newPolyIndex);
    } else {
        // Multiple cluter groups were encountered.
        // Merge the groups (change/update the group numbers)
        // Search for encountered groups and make them all have the same group numbers
        // First, add newpoly to correct group
        int k = 0;
        
        while (newPoly.groupNum != pstats.fractGroup[k].groupNum) {
            k++;
        }
        
        // Add new poly to the group
        pstats.fractGroup[k].polyList.push_back(newPolyIndex);
        // Incriment size of group by one for newPoly
        pstats.groupData[newPoly.groupNum - 1].size++;
        // Add any boundary face data to group fro newPoly
        OR(pstats.groupData[newPoly.groupNum - 1].faces, newPoly.faces);
        
        // Need merge groups in encounteredGroups list to newPoly.groupNum
        for (unsigned int i = 0; i < encounteredGroups.size(); i++) {
            // Add merging groups size to new group's size
            if (pstats.groupData[encounteredGroups[i] - 1].valid == 1) {
                pstats.groupData[newPoly.groupNum - 1].size += pstats.groupData[encounteredGroups[i] - 1].size;
                // Merge any boundary faces data
                OR(pstats.groupData[newPoly.groupNum - 1].faces, pstats.groupData[encounteredGroups[i] - 1].faces);
                // Mark merged groups group data as invalid
                pstats.groupData[encounteredGroups[i] - 1].valid = 0;
            }
            
            for (unsigned int jj = 0; jj < pstats.fractGroup.size(); jj++) {
                if (pstats.fractGroup[jj].groupNum == encounteredGroups[i]) {
                    // Change group number to the new group number
                    pstats.fractGroup[jj].groupNum = newPoly.groupNum;
                    
                    // Change polys group number inside the group to the new group num
                    for (unsigned int z = 0; z < pstats.fractGroup[jj].polyList.size(); z++) {
                        acceptedPoly[pstats.fractGroup[jj].polyList[z]].groupNum = newPoly.groupNum;
                    }
                }
            }
        }
    }
}

