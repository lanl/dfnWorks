#include "output.h"
#include <fstream>
#include <stdlib.h> // remove dir
#include <algorithm>
#include "input.h"
#include <iostream>
#include "structures.h"
#include "vectorFunctions.h"
#include "insertShape.h" // getFamilyNum()
#include "mathFunctions.h"
#include "generatingPoints.h"
#include "computationalGeometry.h" // Rotation matrix functions
#include <cmath>
#include <sys/stat.h> // Checking if output directory exists DIR_exists(dir)
#include <iomanip> // std::setprecision()
#include <sys/stat.h> // mkdir system call 
#include "readInputFunctions.h" // error check for file open checkIfOpen()

//NOTE: do not use std::endl for new lines when writing to files. This will flush the output buffer. Use '\n'

/* void writeOutput() ************************************************************************/
/*! Writes all output for DFNGen
    Arg 1: c syle string (char array) path to output folder
    Arg 2: std::vector Poly array of all accepted polygons
    Arg 3: std::vector Intersection array of all intersections from accepted polygons
    Arg 4: std::vector Point array of all accpeted triple intersection points
    Arg 5: Stats strcuture, running program statistucs (see definition in structures.h)
    Arg 6: std::vector of unsigned int - indices into the Poly array of accepted polgons
           which remain after isolated fractures (polys) were removed
    Arg 7: std::vector Shape - Family structure array  of all stocastic families defined by user input */
void writeOutput(char* outputFolder, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts, std::vector<Point> &triplePoints, struct Stats &pstats, std::vector<unsigned int> &finalFractures, std::vector<Shape> &shapeFamilies) {
    std::string output = outputFolder;
    // Define Output Files:
    std::string permOutputFile = output + "/perm.dat";
    std::string aperture = output + "/aperture.dat";
    std::string intersectionFolder = output + "/intersections";
    std::string radiiFolder = output + "/radii/";
    // Adjust Fracture numbering
    adjustIntFractIDs(finalFractures, acceptedPoly, intPts);
    // Write out graph information
    writeGraphData(finalFractures, acceptedPoly, intPts);
    // Write polygon.dat file
    writePolys(finalFractures, acceptedPoly, output);
    // Write intersection files (must be first file written, rotates polys to x-y plane)
    writeIntersectionFiles(finalFractures, acceptedPoly, intPts, triplePoints, intersectionFolder, pstats);
    // Write polys.inp
    writePolysInp(finalFractures, acceptedPoly, output);
    // Write params.txt
    writeParamsFile(finalFractures, acceptedPoly, shapeFamilies, pstats, triplePoints, output);
    // Write aperture file
    writeApertureFile(finalFractures, acceptedPoly, output);
    // Write permability file
    writePermFile(finalFractures, acceptedPoly, output);
    // Write radii file
    writeRadiiFile(finalFractures, acceptedPoly, output);
    // Write rejection stats file
    writeRejectionStats(pstats, output);
    // Write families to output Files
    writeShapeFams(shapeFamilies, output);
    // Write fracture translations file
    writeFractureTranslations(finalFractures, acceptedPoly, output);
    // Write fracture connectivity (edge graph) file
    writeConnectivity(finalFractures, acceptedPoly, intPts, output);
    // Write rotation data
    writeRotationData(acceptedPoly, finalFractures, shapeFamilies, output);
    // Write normal vectors
    writeNormalVectors(acceptedPoly, finalFractures, shapeFamilies, output);
    // Write rejects per fracture insertion attempt data
    writeRejectsPerAttempt(pstats, output);
    // Write all accepted radii
    writeFinalPolyRadii(finalFractures, acceptedPoly, output);
    // Write all accepted Surface Area
    writeFinalPolyArea(finalFractures, acceptedPoly, output);
    // Write out which fractures touch which boundaries
    writeBoundaryFiles(finalFractures, acceptedPoly);
    
    if (outputAcceptedRadiiPerFamily) {
        std::cout << "Writing Accepted Radii Files Per Family\n";
        // Creates radii files per family, before isolated fracture removal.
        int size = shapeFamilies.size();
        
        for (int i = 0; i < size; i++) {
            writeAllAcceptedRadii_OfFamily(i, acceptedPoly, radiiFolder);
        }
        
        if (userRectanglesOnOff) {
            // Fractures are marked -2 for user rects
            writeAllAcceptedRadii_OfFamily(-2, acceptedPoly, radiiFolder);
        }
        
        if (userEllipsesOnOff) {
            // Fractures are marked -1 for user ellipses
            writeAllAcceptedRadii_OfFamily(-1, acceptedPoly, radiiFolder);
        }
        
        if (userPolygonByCoord) {
            // Fractures are marked -3 for user user polygons
            writeAllAcceptedRadii_OfFamily(-3, acceptedPoly, radiiFolder);
        }
    }
    
    if (outputFinalRadiiPerFamily) {
        std::cout << "Writing Final Radii Files Per Family\n";
        int size = shapeFamilies.size();
        
        for (int i = 0; i < size; i++) {
            writeFinalRadii_OfFamily(finalFractures, i, acceptedPoly, radiiFolder);
        }
        
        if (userRectanglesOnOff) {
            writeFinalRadii_OfFamily(finalFractures, -1, acceptedPoly, radiiFolder);
        }
        
        if (userEllipsesOnOff) {
            writeFinalRadii_OfFamily(finalFractures, -2, acceptedPoly, radiiFolder);
        }
        
        if (userPolygonByCoord) {
            writeFinalRadii_OfFamily(finalFractures, -3, acceptedPoly, radiiFolder);
        }
    }
    
    // If triple intersections are on, write triple intersection points file
    if (tripleIntersections) {
        std::cout << "Writing Triple Intersection Points File\n";
        writeTriplePts(triplePoints, finalFractures, acceptedPoly, intPts, output);
    }
} // End writeOutput()


/*=================================   OUTPUT.CPP FUNCTIONS   ================================*/
/*===========================================================================================*/


/* void writePoints() ************************************************************************/
/*! Helper function for writing discretized intersections
    Function writes n points to file
    Arg 1: Output file stream object (file we are writing to)
    Arg 2: std::vector Point array (discretized points)
    Arg 3: Index to point to start output to file.
           ARG 3 USAGE EAMPLE: When discretizing points, the program can discretize from an end
           point to a triple intersection point, and then from the triple intersection point to
           another end point. This means you have two arrays of points. The last point in the first
           array will be the same as the first point in the second array. In this situation, you
           would set start = 1 while writing the second array to avoid duplicate points in the output
    Arg 4: Counter of poitns written. Used to rember at which node a new intersection starts */
void writePoints(std::ostream &output, std::vector<Point> &points, int start, unsigned int &count) {
    int n = points.size();
    
    for (int i = start; i < n; i++) {
        output << std::setprecision(12) << count << " " << points[i].x
               << " " << points[i].y << " " << points[i].z << "\n";
        count++;
    }
}

/* finishWritingIntFile() ********************************************************************/
/*! Helper function for writing discretized intersection points
    Writes header and line connections after points have been written
    Arg 1: Output file stream object (intersection file)
    Arg 2: Number, or index, of fracture whos intersection is being written
    Arg 3: Number of intersection points on fracture
    Arg 4: Number of intersections on fracture
    Arg 5: std:vector array of node numbers which start an intersection. Used to generate "line"
           connections in intersection inp files
    Arg 6: std::vector array of fracture id's (indices) who intersect fract1 (arg 2) */
void finishWritingIntFile(std::ostream &fractIntFile, int fract1, int numPoints, int numIntersections,
                          std::vector<unsigned int> &intStart, std::vector<unsigned int> &intersectingFractures) {
    unsigned int count = 1;
    int idx = 0;
    
    // Lines
    for (int i = 0; i < numPoints - numIntersections; i++) {
        if(intStart[idx] == count + 1) {
            count++;
            idx++;
        }
        
        fractIntFile << i + 1 << " " << fract1 << " line " << count << " " << count + 1 << "\n";
        count++;
    }
    
    fractIntFile << "2 1 1\n";
    fractIntFile << "a_b, integer\n";
    fractIntFile << "b_a, integer\n";
    idx = 0;
    
    for (int i = 0; i < numPoints; i++) {
        if(intStart[idx] == (unsigned) i + 1) {
            idx++;
        }
        
        fractIntFile << i + 1 << " " << fract1 << " " << intersectingFractures[idx] << "\n";
    }
    
    // Move to header postion
    fractIntFile.seekp(0);
    fractIntFile << numPoints << " " << numPoints - numIntersections << " " << 2 << " " << "0 0";
}


/* bool DIR_exists() *************************************************************************/
/*! Checks if a directory already exists.
    Used for error checking. If DFN generation completes but user entered output folder
    incorrectly, the error check will let them re-enter an output folder so they wont
    lose the DFN data/output
    Arg 1: Path to directory
    Return: true if the directory exists, false otherwise */
bool DIR_exists(const char *path) {
    struct stat sb;
    
    if ((stat(path, &sb) == 0 && S_ISDIR(sb.st_mode))) {
        return 1;
    }
    
    return 0;
}


/* adjustIntFractIds() **********************************************************************/
/*! Adjust the intersectins fracture numbers. The finalFracture list is the indexes of the final polygons.
    If finalFractures = {4, 2, 8}, the fracture ID's must be 1, 2, 3 respectively. Easiest way
    is to adjust the fracture ID's in the corresponding intersections first, before writing output files
    Use the negative value to keep to not loose track of what fracture id's are what (prevent aliasing).

    EXAMPLE: For triple intersections, each intersection lists three fractures which intersect.
    Say fractures 1, 5, and 6 intersect and once adjusted the the fracture IDs become 1, 4, and 5.
    We access the intersection structure through the polygons, so for this particular
    intersection structure, it will be accessed three times (once for each polygon). If we adjust ID 5 to be id 4 during
    the second access, then during the thrid access, ID 4 may be aliasing another ID and be adjusted again.
    To prevent this, we use the negative value to prevent aliasing.
    Arg 1: std::vector of indices to allPolys array of fractures left after isolated fracture removal
    Arg 2: std::vector of all accepted polygons
    Arg 3: std::vector of all intersections */
void adjustIntFractIDs(std::vector<unsigned int> &finalFractures, std::vector<Poly> &allPolys, std::vector<IntPoints> &intPts) {
    //go through all final fractures
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        //go through each final fractures intersections
        for (unsigned int j = 0; j < allPolys[finalFractures[i]].intersectionIndex.size(); j++) {
            //change matching fracture numbers to new number (order of finalFractures list) for output
            unsigned int intIdx = allPolys[finalFractures[i]].intersectionIndex[j];
            
            if (intPts[intIdx].fract1 ==  finalFractures[i]) {
                intPts[intIdx].fract1 =  -( (long int) i + 1);
            } else if (intPts[intIdx].fract2 == finalFractures[i]) {
                intPts[intIdx].fract2 = -( (long int) i + 1);
            }
        }
    }
}


/* writeIntersectionFiles() ******************************************************************/
/*! Writes intersection inp files to output folder
    Rotates intersections, and triple intersection points to x-y plane
    Also rotates polygons to x-y plane to save on computation during writePolysInp()
    Rotating polygons here increases performance as we do not need to recalculate rotation matricies
    Arg 1: std::vector array of indices to fractures (Arg 2) remaining after isolated
           fracture removal
    Arg 2: std::vector array of all accepted fractures (before isolated fracture removal)
    Arg 3: std::vector array of all intersections
    Arg 4: std::vector array all triple intersection points
    Arg 5: Path to intersections folder
    Arg 6: Stats strcture. DFNGen running program stats (keeps track of total intersecion node count) */
void writeIntersectionFiles(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts, std::vector<Point> &triplePoints, std::string intersectionFolder, struct Stats &pstats) {
    Point tempPoint1, tempPoint2; // Keeps track of current un-rotated points we are working with
    std::cout << "Writing Intersection Files\n";
    std::ofstream fractIntFile;
    //int keepIsolated = 1;
    
    // Go through finalFractures. Rotate poly, intersections, and triple intersection points
    // to XY plane. Discretize and write to file
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        // Starting positions for each intersection. Lets us know how to make the line connections
        std::vector<unsigned int> intStart;
        unsigned int count = 1;
        // Counter for intersection header  number of points
        unsigned int numIntPts = 0;
        // Used in writing which nodes belong to which two fractures in finishWritingOutput()
        std::vector<unsigned int> intersectingFractures;
        // Make new intersection file in intersections folder
        std::string file = intersectionFolder + "/intersections_" + std::to_string(i + 1) + ".inp";
        fractIntFile.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
        checkIfOpen(fractIntFile, file);
        // Buffer first line to leave space to write header
        fractIntFile << "                                                               \n";
        // Go through each final fracture's intersections and write to output
        unsigned int size = acceptedPoly[finalFractures[i]].intersectionIndex.size();
        
        if (size > 0 || keepIsolatedFractures == 0) {
            for (unsigned int j = 0; j < size; j++) {
                // tempTripPts holds rotated triple points for an intersection. Triple pts must be rotated 3 different
                // ways so we cannot change the original data
                std::vector<Point> tempTripPts;
                // Used to measure current length before rotation (used to calculate number of points
                // to discretize) based on original intersection. This fixes any precision errors we
                // when calculating length after rotation, both rotations for the same intersection will
                // always have the same step size and same number of discretized points.
                double curLength = 0;
                unsigned int polyIntIdx = acceptedPoly[finalFractures[i]].intersectionIndex[j];
                // Similarly to above, the intersection must be rotated two different ways,
                // one for each intersecting poly. We can't change the original data so we must use temp data
                IntPoints tempIntersection = polyAndIntersection_RotationToXY(intPts[polyIntIdx],
                                             acceptedPoly[finalFractures[i]], triplePoints, tempTripPts);
                // poly and intersection now rotated
                int triplePtsSize = tempTripPts.size();
                // fracture 1 is i
                // fracture 2 is the other intersecting fracture
                unsigned int fract2;
                
                if (-intPts[polyIntIdx].fract1 == i + 1) {
                    fract2 = -intPts[polyIntIdx].fract2;
                    intersectingFractures.push_back(fract2);
                } else {
                    fract2 = -intPts[polyIntIdx].fract1;
                    intersectingFractures.push_back(fract2);
                }
                
                // If triple points exist on intersection, discretize from endpoint to closest triple point,
                // from triple to next triple point, and finally to other end point
                if (triplePtsSize != 0) {
                    // Keep track of number of triple points which will be in the
                    // DFN (this is after isolated fracture removal)
                    // NOTE: This will need to be divided by six to get correct value.
                    // Division by six was determined through testing.
                    pstats.tripleNodeCount += triplePtsSize;
                    // Order the triple points by distances to know to discretize from point to next closest point
                    double *distances = new double[triplePtsSize];
                    double pt1[3] = {tempIntersection.x1, tempIntersection.y1, tempIntersection.z1};
                    tempPoint1.x = intPts[polyIntIdx].x1;
                    tempPoint1.y = intPts[polyIntIdx].y1;
                    tempPoint1.z = intPts[polyIntIdx].z1;
                    
                    // Create array of distances first end point to triple points
                    for (int k = 0; k < triplePtsSize; k++) { //loop through triple points on  intersection i
                        double point[3] = {tempTripPts[k].x, tempTripPts[k].y, tempTripPts[k].z};//triple pt
                        distances[k] = euclideanDistance(pt1, point);//create array of distances
                    }
                    
                    // Order the indices of the distances array shortest to largest distance
                    // this lets us know which point to discritize to next
                    int *s = sortedIndex(distances, triplePtsSize);
                    // Discretize from end point1 to first triple pt
                    // pt1 already = enpoint1
                    double pt2[3] = {tempTripPts[s[0]].x, tempTripPts[s[0]].y, tempTripPts[s[0]].z};
                    tempPoint2 = triplePoints[intPts[polyIntIdx].triplePointsIdx[s[0]]];
                    curLength = euclideanDistance(tempPoint1, tempPoint2);
                    std::vector<Point> points = discretizeLineOfIntersection(pt1, pt2, curLength);
                    // Write points to file
                    numIntPts += points.size();
                    writePoints(fractIntFile, points, 0, count);
                    
                    // If one trip pt, set up points to discretize from only triple pt to other end point
                    if (triplePtsSize == 1) {
                        pt1[0] = pt2[0];
                        pt1[1] = pt2[1];
                        pt1[2] = pt2[2];
                        pt2[0] = tempIntersection.x2;
                        pt2[1] = tempIntersection.y2;
                        pt2[2] = tempIntersection.z2;
                        tempPoint1 = tempPoint2;
                        tempPoint2.x = intPts[polyIntIdx].x2;
                        tempPoint2.y = intPts[polyIntIdx].y2;
                        tempPoint2.z = intPts[polyIntIdx].z2;
                    } else { // More than 1 triple point
                        for (int jj = 0; jj < (triplePtsSize - 1); jj++) {
                            pt1[0] = tempTripPts[s[jj]].x;
                            pt1[1] = tempTripPts[s[jj]].y;
                            pt1[2] = tempTripPts[s[jj]].z;
                            pt2[0] = tempTripPts[s[jj + 1]].x;
                            pt2[1] = tempTripPts[s[jj + 1]].y;
                            pt2[2] = tempTripPts[s[jj + 1]].z;
                            tempPoint1 = triplePoints[intPts[polyIntIdx].triplePointsIdx[s[jj]]];
                            tempPoint2 = triplePoints[intPts[polyIntIdx].triplePointsIdx[s[jj + 1]]];
                            curLength = euclideanDistance(tempPoint1, tempPoint2);
                            points = discretizeLineOfIntersection(pt1, pt2, curLength);
                            // Write points for first fracture to file, save second set of points to temp
                            numIntPts += points.size() - 1;
                            writePoints(fractIntFile, points, 1, count);
                        }
                        
                        // Set up points to go from last triple point to last endpoint
                        pt1[0] = pt2[0];
                        pt1[1] = pt2[1];
                        pt1[2] = pt2[2];
                        pt2[0] = tempIntersection.x2;
                        pt2[1] = tempIntersection.y2;
                        pt2[2] = tempIntersection.z2;
                        tempPoint1 = tempPoint2;
                        tempPoint2.x = intPts[polyIntIdx].x2;
                        tempPoint2.y = intPts[polyIntIdx].y2;
                        tempPoint2.z = intPts[polyIntIdx].z2;
                    }
                    
                    curLength = euclideanDistance(tempPoint1, tempPoint2);
                    points = discretizeLineOfIntersection(pt1, pt2, curLength);
                    numIntPts += points.size() - 1;
                    writePoints(fractIntFile, points, 1, count);
                    delete[] s; // Need to delete these manually. created with new[]
                    delete[] distances;
                } else { // No triple intersection points on intersection line
                    double pt1[3] = {tempIntersection.x1, tempIntersection.y1, tempIntersection.z1};
                    double pt2[3] = {tempIntersection.x2, tempIntersection.y2, tempIntersection.z2};
                    tempPoint1.x = intPts[polyIntIdx].x1;
                    tempPoint1.y = intPts[polyIntIdx].y1;
                    tempPoint1.z = intPts[polyIntIdx].z1;
                    tempPoint2.x = intPts[polyIntIdx].x2;
                    tempPoint2.y = intPts[polyIntIdx].y2;
                    tempPoint2.z = intPts[polyIntIdx].z2;
                    curLength = euclideanDistance(tempPoint1, tempPoint2);
                    std::vector<Point> points = discretizeLineOfIntersection(pt1, pt2, curLength);
                    numIntPts += points.size();
                    writePoints(fractIntFile, points, 0, count);
                }
                
                intStart.push_back(count);
            }
        } else {
            std::vector<Point> tempTripPts;
            IntPoints tempIntersection = polyAndIntersection_RotationToXY(intPts[0],
                                         acceptedPoly[finalFractures[i]], triplePoints, tempTripPts);
        }
        
        // Done with fracture and intersections
        pstats.intersectionNodeCount += numIntPts;
        // Write line connectivity and header
        finishWritingIntFile(fractIntFile, i + 1, numIntPts, size, intStart, intersectingFractures);
        intersectingFractures.clear();
        intStart.clear();
        fractIntFile.close();
    }
    
    //Divide by 6 to remove the duplicate counts
    pstats.tripleNodeCount /= 6;
}

/* rotateFractures() **************************************************************************/
/*! Rotates all fractures to x-y plane.
    Used only for reduced mesh, otherwise fractures are rotated while writing intersections
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures */
void rotateFractures(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly) {
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        if (acceptedPoly[finalFractures[i]].XYPlane == true) {
            continue; // Go to next interation of loop
        }
        
        acceptedPoly[finalFractures[i]].XYPlane = true;
        double normalB[3] = {0, 0, 1};
        applyRotation3D(acceptedPoly[finalFractures[i]], normalB);
    }
}

/* writePolysInp() ****************************************************************************/
/*! Writes polys.inp file containing all polygon (fracture) vertice and connectivity data
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writePolysInp_old(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::ofstream polyOutput;
    std::string polyOutputFile = output + "/polys.inp";
    polyOutput.open(polyOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(polyOutput, polyOutputFile);
    std::cout << "Writing " << polyOutputFile << "\n";
    unsigned long long int vertexCount = 0;
    
    //HEADER
    for (unsigned int j = 0; j < finalFractures.size(); j++) { // Count vertices
        vertexCount += acceptedPoly[finalFractures[j]].numberOfNodes;
    }
    
    polyOutput << vertexCount << " " << vertexCount - finalFractures.size() << " 0" << " 0" << " 0" << "\n";
    int count = 1;
    int polyCount = finalFractures.size();
    
    for (int j = 0; j < polyCount; j++) {
        // Write vertices
        for (int i = 0; i < acceptedPoly[finalFractures[j]].numberOfNodes; i++) {
            int idx = i * 3;
            polyOutput << std::setprecision(12) << count << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 1] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 2] << "\n";
            count++;
        }
    }
    
    // Write line connectivity
    count = 1;// Counter for node numbers
    int count2 = 1;// Counter for lines written
    int j;
    
    for (j = 0; j < polyCount; j++) {
        for (int i = 0; i < acceptedPoly[finalFractures[j]].numberOfNodes - 1; i++) {
            polyOutput << count2 << " " << j + 1 << " line " << count << " " << count + 1 << "\n";
            count++;
            count2++;
        }
        
        count++;
    }
    
    polyOutput.close(); // Done with polygons inp file
}

/* writePolys() ****************************************************************************/
/*! Parses and writes all poly_x.inp files containing polygon (fracture) vertice and connectivity data
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writePolys(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::ofstream polyOutput;
    std::cout << "Writing Polygon Files\n";
    int polyCount = finalFractures.size();
    std::string polyOutputFile = output + "/polygons.dat";
    polyOutput.open(polyOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    polyOutput << "nPolygons: " << polyCount << "\n";
    
    for (int j = 0; j < polyCount; j++) {
        // Write vertices
        int numberOfNodes = acceptedPoly[finalFractures[j]].numberOfNodes;
        //polyOutput << acceptedPoly[finalFractures[j]].familyNum << " ";
        polyOutput << numberOfNodes << " ";
        
        for (int i = 0; i < numberOfNodes; i++) {
            int idx = i * 3;
            polyOutput << std::setprecision(12) << "{"
                       << acceptedPoly[finalFractures[j]].vertices[idx] << ", "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 1] << ", "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 2] << "} ";
        }
        
        polyOutput << "\n";
    }
    
    polyOutput.close();
    std::cout << "Writing Polygon Files Complete\n";
}

/* writePolysInp() ****************************************************************************/
/*! Parses and writes all poly_x.inp files containing polygon (fracture) vertice and connectivity data
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writePolysInp(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::ofstream polyOutput;
    std::cout << "Writing poly inp files\n";
    int polyCount = finalFractures.size();
    
    for (int j = 0; j < polyCount; j++) {
        std::string polyOutputFile = output + "/polys/poly_" + std::to_string(j + 1) + ".inp";
        polyOutput.open(polyOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
        // Write header
        polyOutput << acceptedPoly[finalFractures[j]].numberOfNodes << " "
                   << acceptedPoly[finalFractures[j]].numberOfNodes - 1 << " 0" << " 0" << " 0 " << "\n";
        // Write vertices
        int numberOfNodes = acceptedPoly[finalFractures[j]].numberOfNodes;
        
        for (int i = 0; i < numberOfNodes; i++) {
            int idx = i * 3;
            polyOutput << std::setprecision(12) << i + 1 << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 1] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 2] << "\n";
        }
        
        // Write line connectivity
        for (int i = 1; i < numberOfNodes; i++) {
            polyOutput << i << " " << j + 1  << " line " << i  << " " << i + 1 << "\n";
        }
        
        polyOutput.close();
    }
}

/* writeParamsFile() **************************************************************************/
/*! Writes params.txt
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: std::vector array of fracture families
    Arg 4: Path to output folder */
void writeParamsFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<Shape> &shapeFamilies, Stats &pstats, std::vector<Point> &triplePoints, std::string &output) {
    std::ofstream params;
    std::string paramsOutputFile = output + "/params.txt";
    params.open(paramsOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(params, paramsOutputFile);
    std::cout << "Writing " << paramsOutputFile << "\n";
    params << finalFractures.size() << "\n";
    params << h << "\n";
    params << visualizationMode << "\n"; // Production mode
    params << pstats.intersectionNodeCount / 2 - pstats.tripleNodeCount << "\n";
    params << domainSize[0]  << "\n";
    params << domainSize[1]  << "\n";
    params << domainSize[2]  << "\n";
    params.close();
}


/* writeApertureFile() ************************************************************************/
/*! Writes aperture.dat
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writeApertureFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string file = output + "/aperture.dat";
    std::ofstream ap;
    ap.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(ap, file);
    std::cout << "Writing aperture.dat\n";
    ap << "aperture.dat" << "\n";
    int size = finalFractures.size();
    
    for (int i = 0; i < size; i++) {
        ap << -(7 + i) << " 0 0 " << std::setprecision(10) << acceptedPoly[finalFractures[i]].aperture << "\n";
    }
    
    ap.close();
}

/* writePermFile() ****************************************************************************/
/*! Writes perm.dat (Permeability Data)
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writePermFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string file = output + "/perm.dat";
    std::ofstream perm;
    perm.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(perm, file);
    std::cout << "Writing perm.dat\n";
    perm << "permeability" << "\n";
    int size = finalFractures.size();
    
    for (int i = 0; i < size; i++) {
        perm << -(7 + i) << " 0 0 " <<  std::setprecision(10) << acceptedPoly[finalFractures[i]].permeability << " " << acceptedPoly[finalFractures[i]].permeability << " " << acceptedPoly[finalFractures[i]].permeability << "\n";
    }
    
    perm.close();
}


/* writeRadiiFile() ***************************************************************************/
/*! Writes radii.dat (Radii Data)
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writeRadiiFile(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::cout << "Writing Radii File (radii.dat)\n";
    std::string file = output + "/radii.dat";
    std::ofstream radii;
    radii.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(radii, file);
    radii << "Format: xRadius yRadius Family# Removed (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)\n";
    unsigned int finalFractLimit = finalFractures.size() - 1;
    unsigned int size = acceptedPoly.size();
    unsigned int curFinalIdx = 0;
    
    if (finalFractures.size() <= 0) {
        return;
    }
    
    for (unsigned int i = 0; i < size; i++) {
        radii <<  std::setprecision(8) << acceptedPoly[i].xradius << " " << acceptedPoly[i].yradius
              << " " << acceptedPoly[i].familyNum + 1;
              
        // If poly is not in finalFractures list
        // mark that is was removed
        if (i != finalFractures[curFinalIdx]) {
            radii << " R\n";
        } else {
            if (curFinalIdx < finalFractLimit) {
                curFinalIdx++;
            }
            
            radii << "\n";
        }
    }
    
    radii.close();
}


/* writeFractureTranslations() ****************************************************************/
/*! Wrtes translations file (translations.dat)
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writeFractureTranslations(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::cout << "Writing Fracture Translations File (translations.dat)\n";
    std::string filePath = output + "/translations.dat";
    std::ofstream file;
    file.open(filePath.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, filePath);
    file << "Format: x y z  (R = removed from domain due to fracture isolation)\n";
    unsigned int finalFractLimit = finalFractures.size() - 1;
    unsigned int size = acceptedPoly.size();
    unsigned int curFinalIdx = 0;
    
    if (finalFractures.size() <= 0) {
        return;
    }
    
    for (unsigned int i = 0; i < size; i++) {
        file << std::setprecision(10) << acceptedPoly[i].translation[0] << " "
             << acceptedPoly[i].translation[1] << " " << acceptedPoly[i].translation[2];
             
        // If poly is not in finalFractures list
        // mark that is was removed
        if (i != finalFractures[curFinalIdx]) {
            file << " R\n";
        } else {
            if (curFinalIdx < finalFractLimit) {
                curFinalIdx++;
            }
            
            file << "\n";
        }
    }
    
    file.close();
}

/* writeFinalPolyRadii() **********************************************************************/
/*! Deprecated Function
    Writes final radii file (after isoloated fractures have been removed)
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writeFinalPolyRadii(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string file = output + "/radii_Final.dat";
    std::ofstream radiiFinal;
    radiiFinal.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(radiiFinal, file);
    radiiFinal << "Fracture Radii List After Isolated Fracture and Cluster Removal\n";
    radiiFinal << "Format: xRadius yRadius Family# (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)\n";
    int size =   finalFractures.size();
    
    for (int i = 0; i < size; i++) {
        radiiFinal << acceptedPoly[finalFractures[i]].xradius << " "
                   << acceptedPoly[finalFractures[i]].yradius << " "
                   << acceptedPoly[finalFractures[i]].familyNum + 1 << "\n";
    }
    
    radiiFinal.close();
}

/* writeFinalPolyArea() **********************************************************************/
/*! Deprecated Function
    Writes final radii file (after isoloated fractures have been removed)
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writeFinalPolyArea(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string file = output + "/surface_area_Final.dat";
    std::ofstream areaFinal;
    areaFinal.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(areaFinal, file);
    areaFinal << "Fracture Surface Area After Isolated Fracture and Cluster Removal\n";
    int size = finalFractures.size();
    
    for (int i = 0; i < size; i++) {
        areaFinal << acceptedPoly[finalFractures[i]].area << "\n";
    }
    
    areaFinal.close();
}


/* writeAllAcceptedRadii() ********************************************************************/
/*! Deprecated Function
    Writes radii file (radii_AllAccepted.dat) for all accepted fractures before isolated fracture removal
    Arg 1: std::vector array of indices of fractures left after isolated fracture removal
    Arg 2: std::vector array of all accetped fractures
    Arg 3: Path to output folder */
void writeAllAcceptedRadii(std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string file = output + "/radii_AllAccepted.dat";
    std::ofstream radiiAcpt;
    radiiAcpt.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(radiiAcpt, file);
    radiiAcpt << "Fracture Radii List Before Isolated Fracture and Cluster Removal\n";
    radiiAcpt << "Format: xRadius yRadius Distribution # (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)\n";
    int size = acceptedPoly.size();
    
    for (int i = 0; i < size; i++) {
        radiiAcpt << acceptedPoly[i].xradius << " " << acceptedPoly[i].yradius << " " << acceptedPoly[i].familyNum + 1 << "\n";
    }
    
    radiiAcpt.close();
}


/* writeAllAcceptedRadii_OfFamily() ***********************************************************/
/*! Writes radii file (radii_AllAccepted_Fam_#.dat) for all accepted
    fractures BEFORE isolated fracture removal (one file per family)
    Arg 1: Family number for which radii file will be written for
           -2 - User Rectangles, -1 - User Ellipses, Family# >= 0 - Family in order of 'FamProb' in input file
    Arg 2: std::vector array of indices of fractures left after isolated fracture removal
    Arg 3: std::vector array of all accetped fractures
    Arg 4: Path to output folder */
void writeAllAcceptedRadii_OfFamily(int familyNum, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string fileName = output + "/radii_AllAccepted_Fam_" + std::to_string(familyNum + 1) + ".dat";
    std::ofstream file;
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileName);
    file << "Fracture Radii List Before Isolated Fracture and Cluster Removal (Family " << familyNum + 1 << ")\n";
    file << "Format: xRadius yRadius Distrubution# (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)\n";
    int size = acceptedPoly.size();
    
    for (int i = 0; i < size; i++) {
        if (acceptedPoly[i].familyNum == familyNum) {
            file << acceptedPoly[i].xradius << " " << acceptedPoly[i].yradius << " " << acceptedPoly[i].familyNum + 1 << "\n";
        }
    }
    
    file.close();
}

/* writeAllAcceptedRadii_OfFamily() ***********************************************************/
/*! Writes radii file (radii_AllAccepted_Fam_#.dat) for all accepted
    fractures AFTER isolated fracture removal (one file per family)
    Arg 1: Family number for which radii file will be written for
           -2 - User Rectangles, -1 - User Ellipses, Family# >= 0 - Family in order of 'FamProb' in input file
    Arg 2: std::vector array of indices of fractures left after isolated fracture removal
    Arg 3: std::vector array of all accetped fractures
    Arg 4: Path to output folder */
void writeFinalRadii_OfFamily(std::vector<unsigned int> &finalFractures, int familyNum, std::vector<Poly> &acceptedPoly, std::string &output) {
    std::string fileName = output + "/radii_Final_Fam_" + std::to_string(familyNum + 1) + ".dat";
    std::ofstream file;
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileName);
    file << "Fracture Radii List After Isolated Fracture and Cluster Removal (Family " << familyNum + 1 << ")\n";
    file << "Format: xRadius yRadius Distrubution# (-2 = userPolygon, -1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)\n";
    int size = finalFractures.size();
    
    for (int i = 0; i < size; i++) {
        if (acceptedPoly[finalFractures[i]].familyNum == familyNum) {
            file << acceptedPoly[finalFractures[i]].xradius << " " << acceptedPoly[finalFractures[i]].yradius << " " << acceptedPoly[finalFractures[i]].familyNum + 1 << "\n";
        }
    }
    
    file.close();
}


/* writeAllAcceptedRadii_OfFamily() ***********************************************************/
/*! Writes triple intersection points to file (triple_Points.dat)
    Arg 1: std::vector array of all triple intersection points
    Arg 2: std::vector array of indices of fractures left after isolated fracture removal
    Arg 3: std::vector array of all accetped fractures
    Arg 4: std::vector array of all intersections
    Arg 5: Path to output folder */
void writeTriplePts(std::vector<Point> &triplePoints, std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts, std::string &output) {
    std::string fileName = output + "/triple_points.dat";
    std::ofstream file;
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileName);
    // Save triple point indices from final list of fractures to temp array
    // There will be duplicates  which need to be removed
    // before writing to file
    std::vector<unsigned int> triplePtsList;
    int size = finalFractures.size();
    
    for (int i = 0; i < size; i++) {
        int intersectCount = acceptedPoly[finalFractures[i]].intersectionIndex.size();
        
        for (int j = 0; j < intersectCount; j++) {
            int tripleSize = intPts[acceptedPoly[finalFractures[i]].intersectionIndex[j]].triplePointsIdx.size();
            
            for (int k = 0; k < tripleSize; k++) {
                int triplePtIdx = intPts[acceptedPoly[finalFractures[i]].intersectionIndex[j]].triplePointsIdx[k];
                triplePtsList.push_back(triplePtIdx);
            }
        }
    }
    
    size = triplePtsList.size();
    
    if (size > 0) {
        //remove duplicates
        std::sort(triplePtsList.begin(), triplePtsList.end());
        std::vector<unsigned int> finalPts;
        unsigned int  prevPt = triplePtsList[0];
        finalPts.push_back(prevPt);
        
        for (int i = 1; i < size; i++) {
            unsigned int curPt = triplePtsList[i];
            
            if (curPt != prevPt) {
                finalPts.push_back(curPt);
            }
            
            prevPt = curPt;
        }
        
        triplePtsList.clear();
        size = finalPts.size();
        
        for (int i = 0; i < size; i++) {
            file << std::setprecision(17)
                 << triplePoints[finalPts[i]].x
                 << " " << triplePoints[finalPts[i]].y
                 << " " << triplePoints[finalPts[i]].z
                 << "\n";
        }
    }
    
    file.close();
}


/* writeRejectionStats() **********************************************************************/
/*! Write rejections.dat, rejection statistics
    Arg 1: Stats structure of program statistics
    Arg 2: Path to output folder */
void writeRejectionStats(Stats &pstats, std::string &output) {
    std::cout << "Writing Rejection Statistics File (rejections.dat)\n";
    std::string fileName = output + "/rejections.dat";
    std::ofstream file;
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileName);
    file << "Short Intersection: " << pstats.rejectionReasons.shortIntersection << "\n";
    file << "Close to Node: " << pstats.rejectionReasons.closeToNode << "\n";
    file << "Close to Edge: " << pstats.rejectionReasons.closeToEdge << "\n";
    file << "Vertex Close to Edge: " << pstats.rejectionReasons.closePointToEdge << "\n";
    file << "Outside of Domain: " << pstats.rejectionReasons.outside << "\n";
    file << "Triple Intersection: " << pstats.rejectionReasons.triple << " \n";
    file << "Intersections Too Close: " << pstats.rejectionReasons.interCloseToInter << "\n";
    file.close();
}


/* writeShapeFams() ***************************************************************************/
/*! Writes families.dat, Shape families definition file
    Arg 1: std::vector array of all fracture shape families
    Arg 2: Path to output folder */
void writeShapeFams(std::vector<Shape> &shapeFamilies, std::string &output) {
    double radToDeg = 180 / M_PI;
    std::cout << "Writing Family Definitions File (families.dat)\n";
    std::string fileName = output + "/families.dat";
    std::ofstream file;
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileName);
    using namespace std;
    
    //TODO: add stub code in families.dat for userDefined fractures, IF there are user defined fractures

    if (userEllipsesOnOff) {
        file << "UserDefined Ellipse Family: 0\n\n";
    }
    if (userRectanglesOnOff) {
        file << "UserDefined Rectangle Family: -1\n\n";
    }    
    if (userPolygonByCoord) {
        file << "UserDefined Polygon Family: -2\n\n";
    }
    
    for(unsigned int i = 0; i < shapeFamilies.size(); i++) {
        //name(rect or ell) and number of family
        file << shapeType(shapeFamilies[i]) << " Family: "
             << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << "\n";
        file << "Global Family: " << i + 1 << "\n";
        
        // Print vertice number
        if (shapeFamilies[i].shapeFamily == 0) {  // If ellipse family
            file << "Number of Vertices: " << shapeFamilies[i].numPoints << endl;
        } else {
            file << "Number of Vertices: 4" << endl;
        }
        
        // aspect ratio
        file << "Aspect Ratio: " << shapeFamilies[i].aspectRatio << endl;
        
        // p32 target
        if (stopCondition == 1) {
            file << "P32 (Fracture Intensity) Target: "
                 << shapeFamilies[i].p32Target << endl;
        }
        
        // beta distribution, rotation around normal vector
        if (shapeFamilies[i].betaDistribution == 0) {
            file << "Beta Distribution (Rotation Around Normal Vector): Uniform" << endl;
        } else {
            file << "Beta (Rotation Around Normal Vector)-rad: " << shapeFamilies[i].beta << endl;
            file << "Beta (Rotation Around Normal Vector)-deg: " << shapeFamilies[i].beta * radToDeg << endl;
        }
        
        if (orientationOption == 0) {
            // Theta (angle normal makes with z axis
            file << "Theta-rad: " << shapeFamilies[i].angleOne << endl;
            file << "Theta-deg: " << shapeFamilies[i].angleOne * radToDeg << endl;
            // Phi (angle the projection of normal onto x-y plane  makes with +x axis
            file << "Phi-rad: " << shapeFamilies[i].angleTwo << endl;
            file << "Phi-deg: " << shapeFamilies[i].angleTwo * radToDeg << endl;
        } else if (orientationOption == 1) {
            file << "Trend-rad: " << shapeFamilies[i].angleOne << endl;
            file << "Trend-deg: " << shapeFamilies[i].angleOne * radToDeg << endl;
            // Phi (angle the projection of normal onto x-y plane  makes with +x axis
            file << "Plunge-rad: " << shapeFamilies[i].angleTwo << endl;
            file << "Plunge-deg: " << shapeFamilies[i].angleTwo * radToDeg << endl;
        } else if (orientationOption == 2) {
            file << "Dip-rad: " << shapeFamilies[i].angleOne << endl;
            file << "Dip-deg: " << shapeFamilies[i].angleOne * radToDeg << endl;
            // Phi (angle the projection of normal onto x-y plane  makes with +x axis
            file << "Strike-rad: " << shapeFamilies[i].angleTwo << endl;
            file << "Strike-deg: " << shapeFamilies[i].angleTwo * radToDeg << endl;
        }
        
        // kappa
        file << "Kappa: " << shapeFamilies[i].kappa << endl;
        
        // Print layer family belongs to
        if (shapeFamilies[i].layer == 0) {
            file << "Layer: Entire domain" << endl;
        } else {
            int idx = (shapeFamilies[i].layer - 1) * 2;
            file << "Layer Number: " << shapeFamilies[i].layer << "\n";
            file << "Layer: {" << layers[idx] << "," << layers[idx + 1] << "}" << endl;
        }
        
        // Print layer family belongs to
        if (shapeFamilies[i].region == 0) {
            file << "Region: Entire domain" << endl;
        } else {
            int idx = (shapeFamilies[i].region - 1) * 6;
            file << "Region Number: " << shapeFamilies[i].region << "\n";
            file << "Region: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
        }
        
        // Print distribution data
        switch (shapeFamilies[i].distributionType) {
        case 1: // lognormal
            file << "Distribution: Lognormal\n";
            file << "Mean: " << shapeFamilies[i].mean << endl;
            file << "Standard Deviation: " << shapeFamilies[i].sd <<  endl;
            file << "Minimum Radius (m): " << shapeFamilies[i].logMin << endl;
            file << "Maximum Radius (m): " << shapeFamilies[i].logMax << endl;
            break;
            
        case 2: // power-law
            file << "Distribution: Truncated Power-Law\n";
            file << "Alpha: " << shapeFamilies[i].alpha << endl;
            file << "Minimum Radius (m): " << shapeFamilies[i].min << endl;
            file << "Maximum Radius (m): " << shapeFamilies[i].max <<  endl;
            break;
            
        case 3: // exponential
            file << "Distribution: Exponential\n";
            file << "Mean: " << shapeFamilies[i].expMean << endl;
            file << "Lambda: " << shapeFamilies[i].expLambda << endl;
            file << "Minimum Radius (m): " << shapeFamilies[i].expMin << endl;
            file << "Maximum Radius (m): " << shapeFamilies[i].expMax << endl;
            break;
            
        case 4: // constant
            file << "Distribution: Constant\n";
            file << "Radius (m): " << shapeFamilies[i].constRadi << endl;
        }
        
        file << "Family Insertion Probability: " << famProbOriginal[i] << "\n\n";
    }
    
    file.close();
}


/* makeDIR() **********************************************************************************/
/*! Creates a directory
    If dir already exists, the directoy will not be overwritten
    Arg 1: Path to directory to be created */
void makeDIR(const char *dir) {
    // If dir already exists, remove it
    if (DIR_exists(dir)) {
        std::string tempStr = "rm -r ";
        tempStr += dir;
        
        if (system(tempStr.c_str())) {
            std::cout << "ERROR: Problem executing system "
                      << "command: " << tempStr << "\n";
            exit(1);
        }
    }
    
    // If directory doesn't exist, create it
    if (!DIR_exists(dir)) {
        int dir_err = mkdir(dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
        
        if (-1 == dir_err)  {
            std::cout << "\nError creating directory " << dir << "\n";
            exit(1);
        }
    }
}


/* writeConnectivity() **********************************************************************************/
/*! Writes fracture connectivity edge graph
    Arg 1: Array of indices to polys in 'acceptedPoly' which are left after isolated fracture removal
    Arg 2: Array off all polygons in DFN before isolated fracture removal
    Arg 3: Array of all intersections in DFN
    Arg 4: Path to output folder */
void writeConnectivity(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts, std::string &output) {
    std::cout << "Writing Connectivity Data (connectivity.dat)\n";
    std::string fileName = output + "/connectivity.dat";
    std::ofstream file;
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileName);
    
    // Format for connectivity: Line number = poly number, integers on line are intersecting fractures
    //  eg:
    // 2 3
    // 1 3
    // 1 2
    // Fracture 1 intersects frac 2 and 3, fract 2 intersects 1 and 3 etc
    
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        unsigned int size = acceptedPoly[finalFractures[i]].intersectionIndex.size();
        
        for (unsigned int j = 0; j < size; j++) {
            long int intIdx = acceptedPoly[finalFractures[i]].intersectionIndex[j];
            
            // Don't write fractures own fracture ID
            
            // NOTE: At this stage in the program, the fracture ID's have been changed to
            // negative. See 'adjustIntFractIds()' for more details.
            // Use '-' to make them positive again.
            if(-intPts[intIdx].fract1 == i + 1) {
                file << -intPts[intIdx].fract2 << " ";
            } else {
                file << -intPts[intIdx].fract1 << " ";
            }
        }
        
        file << "\n";
    }
    
    file.close();
}


/* writeRotationData() ******************************************************************************/
/*! Writes poly_info.dat
    Writes fracture rotation data. Also includes shape families each fracture belongs to.
    Arg 1: Array off all polygons in DFN before isolated fracture removal
    Arg 2: Array of indices to polys in 'acceptedPoly' which are left after isolated fracture removal
    Arg 3: Array of all fracture shape families
    Arg 4: Path to output folder */
void writeRotationData(std::vector<Poly> &acceptedPoly, std::vector<unsigned int> &finalFractures, std::vector<Shape> &shapeFamilies, std::string output) {
    std::ofstream file;
    std::string fileOutputFile = output + "/poly_info.dat";
    file.open(fileOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileOutputFile);
    std::cout << "Writing Rotation Data File (poly_info.dat)\n";
    double maxDomainSize = domainSize[0];
    
    if (maxDomainSize < domainSize[1]) {
        maxDomainSize = domainSize[1];
    }
    
    if (maxDomainSize < domainSize[2]) {
        maxDomainSize = domainSize[2];
    }
    
    maxDomainSize *= 10;
    
    for (unsigned int i = 0; i < finalFractures.size(); i++ ) {
        // poly's normal is already normalized at this point
        double normal[3] = {acceptedPoly[finalFractures[i]].normal[0], acceptedPoly[finalFractures[i]].normal[1], acceptedPoly[finalFractures[i]].normal[2]};
        double e3[3] = {0, 0, 1};
        // Rotation angle in radians
        double theta = std::acos(dotProduct(normal, e3));
        // rad to deg
        theta = theta * (180.0 / M_PI);
        // Rotation into xy plane
        double *v = crossProduct(e3, normal);
        
        if (!(std::abs(v[0]) < eps && std::abs(v[1]) < eps && std::abs(v[2]) < eps)) { //if not zero vector
            normalize(v);
        }
        
        double x0 = 1.1 * (-maxDomainSize * v[0]);
        double y0 = 1.1 * (-maxDomainSize * v[1]);
        double z0 = 1.1 * (-maxDomainSize * v[2]);
        double x1 = 1.1 * maxDomainSize * v[0];
        double y1 = 1.1 * maxDomainSize * v[1];
        double z1 = 1.1 * maxDomainSize * v[2];
        // The last number is the shape family number. Throughout this program,
        // -1 and -2 are used to denote user defined ell. and rectangles.
        // -1 and -2 are not good numbers to use as material IDs in Lagrit.
        // If the family number is -1 or -2 we change these numbers to be
        // number of stochastic families + 1 and number of stochastic families + 2
        int famNum;
        
        if (acceptedPoly[finalFractures[i]].familyNum == -1) {
            famNum = shapeFamilies.size() + 1;
        } else if (acceptedPoly[finalFractures[i]].familyNum == -2) {
            famNum = shapeFamilies.size() + 2;
        } else {
            famNum = acceptedPoly[finalFractures[i]].familyNum + 1;
        }
        
        // Format: fracture#, x0, y0, z0, x1, y1, z1, family#
        file << (i + 1) << " " << famNum << std::setprecision(15) << " " << theta << " " << x0
             << " " << y0 << " " << z0 << " " << x1 << " " << y1 << " " << z1 << "\n";
        delete[] v;
    }
    
    file.close();
}
/* writeNormalVectors() ******************************************************************************/
/*! Writes normal_vectors.dat
    Writes fracture rotation data. Also includes shape families each fracture belongs to.
    Arg 1: Array off all polygons in DFN before isolated fracture removal
    Arg 2: Array of indices to polys in 'acceptedPoly' which are left after isolated fracture removal
    Arg 3: Array of all fracture shape families
    Arg 4: Path to output folder */
void writeNormalVectors(std::vector<Poly> &acceptedPoly, std::vector<unsigned int> &finalFractures, std::vector<Shape> &shapeFamilies, std::string output) {
    std::ofstream file;
    std::string fileOutputFile = output + "/normal_vectors.dat";
    file.open(fileOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileOutputFile);
    std::cout << "Writing Normal Vectors into File (normal_vectors.dat)\n";
    
    for (unsigned int i = 0; i < finalFractures.size(); i++ ) {
        // poly's normal is already normalized at this point
        // Format: nx, ny, nz
        //std::cout <<  std::setprecision(15) << acceptedPoly[finalFractures[i]].normal[0] << " "
        //<< acceptedPoly[finalFractures[i]].normal[1] << " " << acceptedPoly[finalFractures[i]].normal[2]  << "\n";
        file <<  std::setprecision(15) << " " << acceptedPoly[finalFractures[i]].normal[0] << " "
             << acceptedPoly[finalFractures[i]].normal[1] << " " << acceptedPoly[finalFractures[i]].normal[2]  << "\n";
    }
    
    file.close();
}

/* writeRejectsPerAttempt()**************************************************************************/
/*! Writes rejectsPerAttempt.dat
    Outputs a file that contains a list of integers of the number
    of attempts per fracture.
    For example, if the 5th number in the list is 100, it means that
    it took 100 fracture insertion attemps for before the 5th fracture
    was accepted.
    Arg 1: Stats structure, program statistics
    Arg 2: Path to output*/
void writeRejectsPerAttempt(Stats &pstats, std::string &output) {
    std::ofstream file;
    std::string fileOutputFile = output + "/rejectsPerAttempt.dat";
    file.open(fileOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(file, fileOutputFile);
    std::cout << "Writing Rotation Data File (rejectsPerAttempt.dat)\n";
    
    for (unsigned int i = 0; i < pstats.rejectsPerAttempt.size(); i++) {
        file << pstats.rejectsPerAttempt[i] << "\n";
    }
    
    file.close();
}

/* writeGraphData() ******************************************************************/
/*! Writes graph data files to intersections_list.dat and fracture_info.dat
    Arg 1: std::vector array of indices to fractures (Arg 2) remaining after isolated
           fracture removal
    Arg 2: std::vector array of all accepted fractures (before isolated fracture removal)
    Arg 3: std::vector array of all intersections*/
void writeGraphData(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly, std::vector<IntPoints> &intPts) {
    double domainX = domainSize[0] * .5;
    double domainY = domainSize[1] * .5;
    double domainZ = domainSize[2] * .5;
    Point tempPoint1, tempPoint2, tempPoint3; // Keeps track of current un-rotated points we are working with
    std::cout << "\nWriting Graph Data Files\n";
    //adjustIntFractIDs(finalFractures,acceptedPoly, intPts);
    // Make new intersection file in intersections folder
    std::ofstream intFile;
    std::string file = "intersection_list.dat";
    intFile.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(intFile, file);
    intFile << "f1 f2 x y z length\n";
    // Make new intersection file in intersections folder
    std::ofstream fractFile;
    std::string file2 = "fracture_info.dat";
    fractFile.open(file2.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(fractFile, file2);
    fractFile << "num_connections perm aperture\n";
    
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        int num_conn = 0;
        // Go through each final fracture's intersections and write to output
        unsigned int size = acceptedPoly[finalFractures[i]].intersectionIndex.size();
        
        for (unsigned int j = 0; j < size; j++) {
            // Used to measure current length before rotation (used to calculate number of points
            // to discretize) based on original intersection. This fixes any precision errors we
            // when calculating length after rotation, both rotations for the same intersection will
            // always have the same step size and same number of discretized points.
            unsigned int polyIntIdx = acceptedPoly[finalFractures[i]].intersectionIndex[j];
            // fracture 1 is i
            // fracture 2 is the other intersecting fracture
            unsigned int fract1;
            unsigned int fract2;
            
            if (-intPts[polyIntIdx].fract1 == i + 1) {
                fract1 = -intPts[polyIntIdx].fract1;
                fract2 = -intPts[polyIntIdx].fract2;
            } else {
                fract2 = -intPts[polyIntIdx].fract1;
                fract1 = -intPts[polyIntIdx].fract2;
            }
            
            if(fract1 < fract2) {
                writeMidPoint(intFile, fract1, fract2, intPts[polyIntIdx].x1,  intPts[polyIntIdx].y1, intPts[polyIntIdx].z1,
                              intPts[polyIntIdx].x2, intPts[polyIntIdx].y2, intPts[polyIntIdx].z2);
                num_conn++;
            }
        }
        
        // Find intersections with domain boundaries
        // bools are so that lines of intersection are only found and written to file once
        // once an intersection with a domain boundary is found the bool = true
        bool right = false;
        bool left = false;
        bool top = false;
        bool bottom = false;
        bool front = false;
        bool back = false;
        int temp = acceptedPoly[finalFractures[i]].numberOfNodes;
        
        // fracture 2 index are based on FEHM format
        // top / Z+ / 1
        // bottom / Z- / 2
        // left / X- / 3
        // front / Y+ / 4
        // right / X- / 5
        // back / Y- / 6
        for (int k = 0; k < temp; k++) {
            // Check boundary faces
            // Update which boundaries newPoly touches
            int idx = k * 3;
            
            // if fracture if on right boundary
            if (acceptedPoly[finalFractures[i]].vertices[idx] >= domainX - eps) {
                for (int kk = 0; kk < temp; kk++) {
                    int iidx = kk * 3;
                    
                    if (acceptedPoly[finalFractures[i]].vertices[iidx] >= domainX - eps && idx != iidx && !right) {
                        writeMidPoint(intFile, i + 1, -5, acceptedPoly[finalFractures[i]].vertices[idx], acceptedPoly[finalFractures[i]].vertices[idx + 1], acceptedPoly[finalFractures[i]].vertices[idx + 2], acceptedPoly[finalFractures[i]].vertices[iidx], acceptedPoly[finalFractures[i]].vertices[iidx + 1], acceptedPoly[finalFractures[i]].vertices[iidx + 2]);
                        right = true;
                        num_conn++;
                        break;
                    }
                }
            }
            // if fracture if on left boundary
            else if (acceptedPoly[finalFractures[i]].vertices[idx] <= -domainX + eps) {
                for (int kk = 0; kk < temp; kk++) {
                    int iidx = kk * 3;
                    
                    if (acceptedPoly[finalFractures[i]].vertices[iidx] <= -domainX + eps && idx != iidx && !left) {
                        writeMidPoint(intFile, i + 1, -3, acceptedPoly[finalFractures[i]].vertices[idx], acceptedPoly[finalFractures[i]].vertices[idx + 1], acceptedPoly[finalFractures[i]].vertices[idx + 2], acceptedPoly[finalFractures[i]].vertices[iidx], acceptedPoly[finalFractures[i]].vertices[iidx + 1], acceptedPoly[finalFractures[i]].vertices[iidx + 2]);
                        left = true;
                        num_conn++;
                        break;
                    }
                }
            }
            
            // if fracture if on front boundary
            if (acceptedPoly[finalFractures[i]].vertices[idx + 1] >= domainY - eps) {
                for (int kk = 0; kk < temp; kk++) {
                    int iidx = kk * 3;
                    
                    if (acceptedPoly[finalFractures[i]].vertices[iidx + 1] >= domainY - eps && idx != iidx && !front) {
                        writeMidPoint(intFile, i + 1, -4, acceptedPoly[finalFractures[i]].vertices[idx], acceptedPoly[finalFractures[i]].vertices[idx + 1], acceptedPoly[finalFractures[i]].vertices[idx + 2], acceptedPoly[finalFractures[i]].vertices[iidx], acceptedPoly[finalFractures[i]].vertices[iidx + 1], acceptedPoly[finalFractures[i]].vertices[iidx + 2]);
                        front = true;
                        num_conn++;
                        break;
                    }
                }
            }
            // if fracture if on back boundary
            else if (acceptedPoly[finalFractures[i]].vertices[idx + 1] <= -domainY + eps) {
                for (int kk = 0; kk < temp; kk++) {
                    int iidx = kk * 3;
                    
                    if (acceptedPoly[finalFractures[i]].vertices[iidx + 1] <= -domainY + eps && idx != iidx && !back) {
                        writeMidPoint(intFile, i + 1, -6, acceptedPoly[finalFractures[i]].vertices[idx], acceptedPoly[finalFractures[i]].vertices[idx + 1], acceptedPoly[finalFractures[i]].vertices[idx + 2], acceptedPoly[finalFractures[i]].vertices[iidx], acceptedPoly[finalFractures[i]].vertices[iidx + 1], acceptedPoly[finalFractures[i]].vertices[iidx + 2]);
                        back = true;
                        num_conn++;
                        break;
                    }
                }
            }
            
            if (acceptedPoly[finalFractures[i]].vertices[idx + 2] >= domainZ - eps) {
                for (int kk = 0; kk < temp; kk++) {
                    int iidx = kk * 3;
                    
                    if (acceptedPoly[finalFractures[i]].vertices[iidx + 2] >= domainZ - eps && idx != iidx && !top) {
                        writeMidPoint(intFile, i + 1, -1, acceptedPoly[finalFractures[i]].vertices[idx], acceptedPoly[finalFractures[i]].vertices[idx + 1], acceptedPoly[finalFractures[i]].vertices[idx + 2], acceptedPoly[finalFractures[i]].vertices[iidx], acceptedPoly[finalFractures[i]].vertices[iidx + 1], acceptedPoly[finalFractures[i]].vertices[iidx + 2]);
                        top = true;
                        num_conn++;
                        break;
                    }
                }
            } else if (acceptedPoly[finalFractures[i]].vertices[idx + 2] <= -domainZ + eps) {
                for (int kk = 0; kk < temp; kk++) {
                    int iidx = kk * 3;
                    
                    if (acceptedPoly[finalFractures[i]].vertices[iidx + 2] <= -domainZ + eps && idx != iidx && !bottom) {
                        writeMidPoint(intFile, i + 1, -2, acceptedPoly[finalFractures[i]].vertices[idx], acceptedPoly[finalFractures[i]].vertices[idx + 1], acceptedPoly[finalFractures[i]].vertices[idx + 2], acceptedPoly[finalFractures[i]].vertices[iidx], acceptedPoly[finalFractures[i]].vertices[iidx + 1], acceptedPoly[finalFractures[i]].vertices[iidx + 2]);
                        bottom = true;
                        num_conn++;
                        break;
                    }
                }
            }
        }
        
        fractFile << num_conn << " " << std::setprecision(10) << acceptedPoly[finalFractures[i]].permeability << " " << acceptedPoly[finalFractures[i]].aperture << "\n";
    }
    
    // Done with fracture and intersections
    intFile.close();
    fractFile.close();
}
/* writeMidPoint() ******************************************************************/
/*! Writes mid point and length of line defined by x1,y1,z1 and x2,y2,z2 into file fp
    Arg 1: std::ofstream file to write informatino into
    Arg 2: int fracture 1
    Arg 3: int fracture 2
    Arg 4: double x1 x coordinate of first endpoint
    Arg 5: double y1 y coordinate of first endpoint
    Arg 6: double z1 z coordinate of first endpoint
    Arg 7: double x2 x coordinate of second endpoint
    Arg 8: double y2 y coordinate of second endpoint
    Arg 9: double z2 z coordinate of second endpoint */

void writeMidPoint(std::ofstream &fp, int fract1, int fract2, double x1, double y1, double z1, double x2, double y2, double z2) {
    Point tempPoint1, tempPoint2, tempPoint3; // Keeps track of current un-rotated points we are working with
    tempPoint1.x = x1;
    tempPoint1.y = y1;
    tempPoint1.z = z1;
    tempPoint2.x = x2;
    tempPoint2.y = y2;
    tempPoint2.z = z2;
    tempPoint3.x = 0.5 * (tempPoint1.x + tempPoint2.x);
    tempPoint3.y = 0.5 * (tempPoint1.y + tempPoint2.y);
    tempPoint3.z = 0.5 * (tempPoint1.z + tempPoint2.z);
    double curLength = 0;
    curLength = euclideanDistance(tempPoint1, tempPoint2);
    fp << fract1  << " " << fract2 << std::setprecision(10) << " " << tempPoint3.x << " " << tempPoint3.y << " " << tempPoint3.z << " " << curLength << "\n";
}

/* writeBoundaryfiles() ******************************************************************/
/*! Writes fracture numbers into ASCII files corresponding to which boundary they touch
    Arg 1: std::vector array of indices to fractures (Arg 2) remaining after isolated
           fracture removal
    Arg 2: std::vector array of all accepted fractures (before isolated fracture removal)*/
void writeBoundaryFiles(std::vector<unsigned int> &finalFractures, std::vector<Poly> &acceptedPoly) {
    std::cout << "Writing Boundary Files\n";
    std::ofstream leftFile;
    std::string leftFileName = "left.dat";
    leftFile.open(leftFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(leftFile, leftFileName);
    std::ofstream rightFile;
    std::string rightFileName = "right.dat";
    rightFile.open(rightFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(rightFile, rightFileName);
    std::ofstream frontFile;
    std::string frontFileName = "front.dat";
    frontFile.open(frontFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(frontFile, frontFileName);
    std::ofstream backFile;
    std::string backFileName = "back.dat";
    backFile.open(backFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(backFile, backFileName);
    std::ofstream topFile;
    std::string topFileName = "top.dat";
    topFile.open(topFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(topFile, topFileName);
    std::ofstream bottomFile;
    std::string bottomFileName = "bottom.dat";
    bottomFile.open(bottomFileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(bottomFile, bottomFileName);
    
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        // If touching X max
        if(acceptedPoly[finalFractures[i]].faces[0] > 0) {
            rightFile << i + 1 << "\n";
        }
        
        // If touching X min
        if(acceptedPoly[finalFractures[i]].faces[1] > 0) {
            leftFile << i + 1 << "\n";
        }
        
        // If touching Y max
        if(acceptedPoly[finalFractures[i]].faces[2] > 0) {
            frontFile << i + 1 << "\n";
        }
        
        // If touching Y min
        if(acceptedPoly[finalFractures[i]].faces[3] > 0) {
            backFile << i + 1 << "\n";
        }
        
        // If touching Z max
        if(acceptedPoly[finalFractures[i]].faces[4] > 0) {
            topFile << i + 1 << "\n";
        }
        
        // If touching Z min
        if(acceptedPoly[finalFractures[i]].faces[5] > 0) {
            bottomFile << i + 1 << "\n";
        }
    }
    
    leftFile.close();
    rightFile.close();
    frontFile.close();
    backFile.close();
    topFile.close();
    bottomFile.close();
}


