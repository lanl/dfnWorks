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
#include "logFile.h"

// NOTE: do not use std::endl for new lines when writing to files. This will flush the output buffer. Use '\n'

/*!
 * \brief Writes all output files for DFNGen.
 *
 * \param outputFolder Path to output folder (C-style string).
 * \param acceptedPoly Vector of all accepted polygons.
 * \param intPts Vector of all intersections from accepted polygons.
 * \param triplePoints Vector of all accepted triple intersection points.
 * \param pstats Stats structure with running program statistics.
 * \param finalFractures Vector of indices into \p acceptedPoly remaining after isolated fractures removed.
 * \param shapeFamilies Vector of stochastic shape families defined by user input.
 */
void writeOutput(char* outputFolder,
                 std::vector<Poly> &acceptedPoly,
                 std::vector<IntPoints> &intPts,
                 std::vector<Point> &triplePoints,
                 struct Stats &pstats,
                 std::vector<unsigned int> &finalFractures,
                 std::vector<Shape> &shapeFamilies) {
    std::string output = outputFolder;
    std::string dfnGenExtension = "/dfnGen_output";
    output += dfnGenExtension;
    std::string logString = output + "\n";
    logger.writeLogFile(INFO,  logString);
    std::string intersectionFolder = output + "/../intersections";
    std::string radiiFolder      = output + "/radii/";
    adjustIntFractIDs(finalFractures, acceptedPoly, intPts);
    writeGraphData(finalFractures, acceptedPoly, intPts);
    writePolys(finalFractures, acceptedPoly, output);
    writeIntersectionFiles(finalFractures, acceptedPoly, intPts, triplePoints, intersectionFolder, pstats);
    writePolysInp(finalFractures, acceptedPoly, output);
    writeParamsFile(finalFractures, acceptedPoly, shapeFamilies, pstats, triplePoints, output);
    writeRadiiFile(finalFractures, acceptedPoly, output);
    writeRejectionStats(pstats, output);
    writeUserRejectedFractureInformation(pstats, output);
    writeShapeFams(shapeFamilies, output);
    writeFractureTranslations(finalFractures, acceptedPoly, output);
    writeConnectivity(finalFractures, acceptedPoly, intPts, output);
    writeRotationData(acceptedPoly, finalFractures, shapeFamilies, output);
    writeNormalVectors(acceptedPoly, finalFractures, shapeFamilies, output);
    writeRejectsPerAttempt(pstats, output);
    writeFinalPolyRadii(finalFractures, acceptedPoly, output);
    writeFinalPolyArea(finalFractures, acceptedPoly, output);
    writeBoundaryFiles(finalFractures, acceptedPoly);
    
    if (outputAcceptedRadiiPerFamily) {
        logString = "Writing Accepted Radii Files Per Family\n";
        logger.writeLogFile(INFO,  logString);
        int size = shapeFamilies.size();
        for (int i = 0; i < size; i++) {
            writeAllAcceptedRadii_OfFamily(i, acceptedPoly, radiiFolder);
        }
        if (userRectanglesOnOff)
            writeAllAcceptedRadii_OfFamily(-2, acceptedPoly, radiiFolder);
        if (userEllipsesOnOff)
            writeAllAcceptedRadii_OfFamily(-1, acceptedPoly, radiiFolder);
        if (userPolygonByCoord)
            writeAllAcceptedRadii_OfFamily(-3, acceptedPoly, radiiFolder);
    }
    
    if (outputFinalRadiiPerFamily) {
        logString = "Writing Final Radii Files Per Family\n";
        logger.writeLogFile(INFO,  logString);
        int size = shapeFamilies.size();
        for (int i = 0; i < size; i++) {
            writeFinalRadii_OfFamily(finalFractures, i, acceptedPoly, radiiFolder);
        }
        if (userRectanglesOnOff)
            writeFinalRadii_OfFamily(finalFractures, -1, acceptedPoly, radiiFolder);
        if (userEllipsesOnOff)
            writeFinalRadii_OfFamily(finalFractures, -2, acceptedPoly, radiiFolder);
        if (userPolygonByCoord)
            writeFinalRadii_OfFamily(finalFractures, -3, acceptedPoly, radiiFolder);
    }
    
    if (tripleIntersections) {
        logString = "Writing Triple Intersection Points File\n";
        logger.writeLogFile(INFO,  logString);
        writeTriplePts(triplePoints, finalFractures, acceptedPoly, intPts, output);
    }
}

/*!
 * \brief Writes a sequence of discretized intersection points to a file stream.
 *
 * \param output Output file stream to write to.
 * \param points Vector of discretized points.
 * \param start Starting index in \p points to avoid duplicate endpoints.
 * \param count Reference to global point counter.
 */
void writePoints(std::ostream &output,
                 std::vector<Point> &points,
                 int start,
                 unsigned int &count) {
    int n = points.size();
    for (int i = start; i < n; i++) {
        output << std::setprecision(12)
               << count << " "
               << points[i].x << " "
               << points[i].y << " "
               << points[i].z << "\n";
        count++;
    }
}

/*!
 * \brief Writes header and line connections for an intersection file after point data.
 *
 * \param fractIntFile Output file stream for the intersection .inp file.
 * \param fract1 Fracture number being written.
 * \param numPoints Total number of intersection points.
 * \param numIntersections Number of individual intersections on the fracture.
 * \param intStart Vector of start-node indices for each intersection segment.
 * \param intersectingFractures Vector of fracture IDs that intersect \p fract1.
 */
void finishWritingIntFile(std::ostream &fractIntFile,
                          int fract1,
                          int numPoints,
                          int numIntersections,
                          std::vector<unsigned int> &intStart,
                          std::vector<unsigned int> &intersectingFractures) {
    unsigned int count = 1;
    int idx = 0;
    for (int i = 0; i < numPoints - numIntersections; i++) {
        if (intStart[idx] == count + 1) {
            count++;
            idx++;
        }
        fractIntFile << i + 1 << " "
                     << fract1 << " line "
                     << count << " "
                     << count + 1 << "\n";
        count++;
    }
    fractIntFile << "2 1 1\n";
    fractIntFile << "a_b, integer\n";
    fractIntFile << "b_a, integer\n";
    idx = 0;
    for (int i = 0; i < numPoints; i++) {
        if (intStart[idx] == (unsigned)i + 1) {
            idx++;
        }
        fractIntFile << i + 1 << " "
                     << fract1 << " "
                     << intersectingFractures[idx] << "\n";
    }
    fractIntFile.seekp(0);
    fractIntFile << numPoints << " "
                 << numPoints - numIntersections << " "
                 << 2 << " 0 0";
}

/*!
 * \brief Checks if a directory exists.
 *
 * \param path Path to directory.
 * \return true if the directory exists; false otherwise.
 */
bool DIR_exists(const char *path) {
    struct stat sb;
    return (stat(path, &sb) == 0 && S_ISDIR(sb.st_mode));
}

/*!
 * \brief Adjusts intersection fracture IDs to new sequential IDs based on the finalFractures list.
 *
 * \param finalFractures Vector of indices of final accepted fractures.
 * \param allPolys Vector of all polygons (accepted).
 * \param intPts Vector of intersection structures.
 */
void adjustIntFractIDs(std::vector<unsigned int> &finalFractures,
                       std::vector<Poly> &allPolys,
                       std::vector<IntPoints> &intPts) {
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        for (unsigned int j = 0; j < allPolys[finalFractures[i]].intersectionIndex.size(); j++) {
            unsigned int intIdx = allPolys[finalFractures[i]].intersectionIndex[j];
            if (intPts[intIdx].fract1 == finalFractures[i]) {
                intPts[intIdx].fract1 = -((long)i + 1);
            } else if (intPts[intIdx].fract2 == finalFractures[i]) {
                intPts[intIdx].fract2 = -((long)i + 1);
            }
        }
    }
}

/*!
 * \brief Writes intersection .inp files by rotating fractures and discretizing intersections.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param intPts Vector of all intersection structures.
 * \param triplePoints Vector of all accepted triple intersection points.
 * \param intersectionFolder Path to folder for intersection files.
 * \param pstats Stats structure tracking node counts and other metrics.
 */
void writeIntersectionFiles(std::vector<unsigned int> &finalFractures,
                            std::vector<Poly> &acceptedPoly,
                            std::vector<IntPoints> &intPts,
                            std::vector<Point> &triplePoints,
                            std::string intersectionFolder,
                            struct Stats &pstats) {
    Point tempPoint1, tempPoint2;
    std::string logString = "Writing Intersection Files\n";
    logger.writeLogFile(INFO,  logString);
    std::ofstream fractIntFile;
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        std::vector<unsigned int> intStart;
        unsigned int count = 1;
        unsigned int numIntPts = 0;
        std::vector<unsigned int> intersectingFractures;
        std::string file = intersectionFolder + "/intersections_" + std::to_string(i + 1) + ".inp";
        fractIntFile.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
        checkIfOpen(fractIntFile, file);
        fractIntFile << "                                                               \n";
        unsigned int size = acceptedPoly[finalFractures[i]].intersectionIndex.size();
        if (size > 0 || keepIsolatedFractures == 0) {
            for (unsigned int j = 0; j < size; j++) {
                std::vector<Point> tempTripPts;
                double curLength = 0;
                unsigned int polyIntIdx = acceptedPoly[finalFractures[i]].intersectionIndex[j];
                IntPoints tempIntersection = polyAndIntersection_RotationToXY(intPts[polyIntIdx],
                                                                             acceptedPoly[finalFractures[i]],
                                                                             triplePoints,
                                                                             tempTripPts);
                int triplePtsSize = tempTripPts.size();
                unsigned int fract2;
                if (-intPts[polyIntIdx].fract1 == i + 1) {
                    fract2 = -intPts[polyIntIdx].fract2;
                } else {
                    fract2 = -intPts[polyIntIdx].fract1;
                }
                intersectingFractures.push_back(fract2);
                if (triplePtsSize != 0) {
                    pstats.tripleNodeCount += triplePtsSize;
                    double *distances = new double[triplePtsSize];
                    double pt1[3] = {tempIntersection.x1, tempIntersection.y1, tempIntersection.z1};
                    tempPoint1.x = intPts[polyIntIdx].x1;
                    tempPoint1.y = intPts[polyIntIdx].y1;
                    tempPoint1.z = intPts[polyIntIdx].z1;
                    for (int k = 0; k < triplePtsSize; k++) {
                        double point[3] = {tempTripPts[k].x, tempTripPts[k].y, tempTripPts[k].z};
                        distances[k] = euclideanDistance(pt1, point);
                    }
                    int *s = sortedIndex(distances, triplePtsSize);
                    double pt2[3] = {tempTripPts[s[0]].x, tempTripPts[s[0]].y, tempTripPts[s[0]].z};
                    tempPoint2 = triplePoints[intPts[polyIntIdx].triplePointsIdx[s[0]]];
                    curLength = euclideanDistance(tempPoint1, tempPoint2);
                    std::vector<Point> points = discretizeLineOfIntersection(pt1, pt2, curLength);
                    numIntPts += points.size();
                    writePoints(fractIntFile, points, 0, count);
                    if (triplePtsSize == 1) {
                        pt1[0] = pt2[0]; pt1[1] = pt2[1]; pt1[2] = pt2[2];
                        pt2[0] = tempIntersection.x2; pt2[1] = tempIntersection.y2; pt2[2] = tempIntersection.z2;
                        tempPoint1 = tempPoint2;
                        tempPoint2.x = intPts[polyIntIdx].x2;
                        tempPoint2.y = intPts[polyIntIdx].y2;
                        tempPoint2.z = intPts[polyIntIdx].z2;
                    } else {
                        for (int jj = 0; jj < triplePtsSize - 1; jj++) {
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
                            numIntPts += points.size() - 1;
                            writePoints(fractIntFile, points, 1, count);
                        }
                        pt1[0] = pt2[0]; pt1[1] = pt2[1]; pt1[2] = pt2[2];
                        pt2[0] = tempIntersection.x2; pt2[1] = tempIntersection.y2; pt2[2] = tempIntersection.z2;
                        tempPoint1 = tempPoint2;
                        tempPoint2.x = intPts[polyIntIdx].x2;
                        tempPoint2.y = intPts[polyIntIdx].y2;
                        tempPoint2.z = intPts[polyIntIdx].z2;
                    }
                    curLength = euclideanDistance(tempPoint1, tempPoint2);
                    points = discretizeLineOfIntersection(pt1, pt2, curLength);
                    numIntPts += points.size() - 1;
                    writePoints(fractIntFile, points, 1, count);
                    delete[] s;
                    delete[] distances;
                } else {
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
            polyAndIntersection_RotationToXY(intPts[0], acceptedPoly[finalFractures[i]], triplePoints, tempTripPts);
        }
        pstats.intersectionNodeCount += numIntPts;
        finishWritingIntFile(fractIntFile, i + 1, numIntPts, size, intStart, intersectingFractures);
        fractIntFile.close();
    }
    pstats.tripleNodeCount /= 6;
}

/*!
 * \brief Rotates all fractures to the x-y plane (for reduced mesh).
 *
 * \param finalFractures Vector of indices of accepted fractures.
 * \param acceptedPoly Vector of all accepted polygons.
 */
void rotateFractures(std::vector<unsigned int> &finalFractures,
                     std::vector<Poly> &acceptedPoly) {
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        if (acceptedPoly[finalFractures[i]].XYPlane) continue;
        acceptedPoly[finalFractures[i]].XYPlane = true;
        double normalB[3] = {0, 0, 1};
        applyRotation3D(acceptedPoly[finalFractures[i]], normalB);
    }
}

/*!
 * \brief Writes a single polys.inp file containing all polygon vertex and connectivity data.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writePolysInp_old(std::vector<unsigned int> &finalFractures,
                       std::vector<Poly> &acceptedPoly,
                       std::string &output) {
    std::ofstream polyOutput;
    std::string polyOutputFile = output + "/polys.inp";
    polyOutput.open(polyOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(polyOutput, polyOutputFile);
    unsigned long long vertexCount = 0;
    for (unsigned int j = 0; j < finalFractures.size(); j++) {
        vertexCount += acceptedPoly[finalFractures[j]].numberOfNodes;
    }
    polyOutput << vertexCount << " " << vertexCount - finalFractures.size() << " 0 0 0\n";
    int count = 1, count2 = 1;
    for (int j = 0; j < (int)finalFractures.size(); j++) {
        for (int i = 0; i < acceptedPoly[finalFractures[j]].numberOfNodes; i++) {
            int idx = i * 3;
            polyOutput << std::setprecision(12)
                       << count++ << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx+1] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx+2] << "\n";
        }
    }
    count = 1;
    for (int j = 0; j < (int)finalFractures.size(); j++) {
        for (int i = 0; i < acceptedPoly[finalFractures[j]].numberOfNodes - 1; i++) {
            polyOutput << count2++ << " " << j+1 << " line " << count << " " << count+1 << "\n";
            count++;
        }
        count++;
    }
    polyOutput.close();
}

/*!
 * \brief Writes the combined polygons.dat file listing all polygons.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writePolys(std::vector<unsigned int> &finalFractures,
                std::vector<Poly> &acceptedPoly,
                std::string &output) {
    std::ofstream polyOutput;
    std::string logString = "Writing Polygon Files\n";
    logger.writeLogFile(INFO,  logString);
    int polyCount = finalFractures.size();
    std::string polyOutputFile = output + "/polygons.dat";
    polyOutput.open(polyOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    polyOutput << "nPolygons: " << polyCount << "\n";
    for (int j = 0; j < polyCount; j++) {
        int numNodes = acceptedPoly[finalFractures[j]].numberOfNodes;
        polyOutput << numNodes << " ";
        for (int i = 0; i < numNodes; i++) {
            int idx = i*3;
            polyOutput << std::setprecision(12)
                       << "{"
                       << acceptedPoly[finalFractures[j]].vertices[idx]     << ", "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 1] << ", "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 2] << "} ";
        }
        polyOutput << "\n";
    }
    polyOutput.close();
    logString = "Writing Polygon Files Complete\n";
    logger.writeLogFile(INFO,  logString);
}

/*!
 * \brief Writes individual poly_*.inp files, one per polygon.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writePolysInp(std::vector<unsigned int> &finalFractures,
                   std::vector<Poly> &acceptedPoly,
                   std::string &output) {
    std::ofstream polyOutput;
    std::string logString = "Writing poly inp files\n";
    logger.writeLogFile(INFO,  logString);
    int polyCount = finalFractures.size();
    for (int j = 0; j < polyCount; j++) {
        std::string polyOutputFile = output + "/../polys/poly_" + std::to_string(j+1) + ".inp";
        polyOutput.open(polyOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
        polyOutput << acceptedPoly[finalFractures[j]].numberOfNodes << " "
                   << acceptedPoly[finalFractures[j]].numberOfNodes - 1 << " 0 0 0\n";
        int numNodes = acceptedPoly[finalFractures[j]].numberOfNodes;
        for (int i = 0; i < numNodes; i++) {
            int idx = i*3;
            polyOutput << std::setprecision(12)
                       << i+1 << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx]     << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 1] << " "
                       << acceptedPoly[finalFractures[j]].vertices[idx + 2] << "\n";
        }
        for (int i = 1; i < numNodes; i++) {
            polyOutput << i << " " << j+1 << " line " << i << " " << i+1 << "\n";
        }
        polyOutput.close();
    }
}

/*!
 * \brief Writes the params.txt file containing run parameters.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param shapeFamilies Vector of all fracture shape families.
 * \param pstats Stats structure for program statistics.
 * \param triplePoints Vector of triple intersection points.
 * \param output Path to output folder.
 */
void writeParamsFile(std::vector<unsigned int> &finalFractures,
                     std::vector<Poly> &acceptedPoly,
                     std::vector<Shape> &shapeFamilies,
                     Stats &pstats,
                     std::vector<Point> &triplePoints,
                     std::string &output) {
    std::ofstream params;
    std::string paramsOutputFile = output + "/../params.txt";
    params.open(paramsOutputFile.c_str(), std::ofstream::out | std::ofstream::trunc);
    checkIfOpen(params, paramsOutputFile);
    std::string logString = "Writing " + paramsOutputFile + "\n";
    logger.writeLogFile(INFO,  logString);
    params << finalFractures.size() << "\n";
    params << h << "\n";
    params << visualizationMode << "\n";
    params << pstats.intersectionNodeCount / 2 - pstats.tripleNodeCount << "\n";
    params << domainSize[0] << "\n";
    params << domainSize[1] << "\n";
    params << domainSize[2] << "\n";
    params.close();
}

/*!
 * \brief Writes the radii.dat file listing radii for each fracture.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeRadiiFile(std::vector<unsigned int> &finalFractures,
                    std::vector<Poly> &acceptedPoly,
                    std::string &output) {
    std::string logString = "Writing Radii File (radii.dat)\n";
    logger.writeLogFile(INFO,  logString);
    std::string file = output + "/radii.dat";
    std::ofstream radii(file);
    checkIfOpen(radii, file);
    radii << "Format: xRadius yRadius Family# Removed\n";
    if (finalFractures.empty()) return;
    unsigned int curFinalIdx = 0, finalLimit = finalFractures.size() - 1;
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        radii << std::setprecision(8)
              << acceptedPoly[i].xradius << " "
              << acceptedPoly[i].yradius << " "
              << acceptedPoly[i].familyNum + 1;
        if (i != finalFractures[curFinalIdx]) {
            radii << " R\n";
        } else {
            if (curFinalIdx < finalLimit) curFinalIdx++;
            radii << "\n";
        }
    }
}

/*!
 * \brief Writes the translations.dat file listing translation vectors for each fracture.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeFractureTranslations(std::vector<unsigned int> &finalFractures,
                               std::vector<Poly> &acceptedPoly,
                               std::string &output) {
    std::string logString = "Writing Fracture Translations File (translations.dat)\n";
    logger.writeLogFile(INFO,  logString);
    std::string filePath = output + "/translations.dat";
    std::ofstream file(filePath);
    checkIfOpen(file, filePath);
    file << "Format: x y z (R=removed)\n";
    if (finalFractures.empty()) return;
    unsigned int curFinalIdx = 0, finalLimit = finalFractures.size() - 1;
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        file << std::setprecision(10)
             << acceptedPoly[i].translation[0] << " "
             << acceptedPoly[i].translation[1] << " "
             << acceptedPoly[i].translation[2];
        if (i != finalFractures[curFinalIdx]) {
            file << " R\n";
        } else {
            if (curFinalIdx < finalLimit) curFinalIdx++;
            file << "\n";
        }
    }
}

/*!
 * \brief Writes the radii_Final.dat file listing radii after isolated and cluster removal.
 *
 * \param finalFractures Vector of indices of final accepted fractures.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeFinalPolyRadii(std::vector<unsigned int> &finalFractures,
                         std::vector<Poly> &acceptedPoly,
                         std::string &output) {
    std::ofstream radiiFinal(output + "/radii_Final.dat");
    checkIfOpen(radiiFinal, output + "/radii_Final.dat");
    radiiFinal << "Fracture Radii List After Removal\n";
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        radiiFinal << acceptedPoly[finalFractures[i]].xradius << " "
                   << acceptedPoly[finalFractures[i]].yradius << " "
                   << acceptedPoly[finalFractures[i]].familyNum + 1 << "\n";
    }
}

/*!
 * \brief Writes the surface_area_Final.dat file listing polygon surface areas after removal.
 *
 * \param finalFractures Vector of indices of final accepted fractures.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeFinalPolyArea(std::vector<unsigned int> &finalFractures,
                        std::vector<Poly> &acceptedPoly,
                        std::string &output) {
    std::ofstream areaFinal(output + "/surface_area_Final.dat");
    checkIfOpen(areaFinal, output + "/surface_area_Final.dat");
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        areaFinal << acceptedPoly[finalFractures[i]].area << "\n";
    }
}

/*!
 * \brief Writes the radii_AllAccepted.dat file listing radii before any removal.
 *
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeAllAcceptedRadii(std::vector<Poly> &acceptedPoly,
                           std::string &output) {
    std::ofstream radiiAcpt(output + "/radii_AllAccepted.dat");
    checkIfOpen(radiiAcpt, output + "/radii_AllAccepted.dat");
    radiiAcpt << "Fracture Radii List Before Removal\n";
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        radiiAcpt << acceptedPoly[i].xradius << " "
                  << acceptedPoly[i].yradius << " "
                  << acceptedPoly[i].familyNum + 1 << "\n";
    }
}

/*!
 * \brief Writes radii_AllAccepted_Fam_#.dat for each family before removal.
 *
 * \param familyNum Family number (-2=userRect, -1=userEll, >=0 stochastic).
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeAllAcceptedRadii_OfFamily(int familyNum,
                                    std::vector<Poly> &acceptedPoly,
                                    std::string &output) {
    std::string fileName = output + "/radii_AllAccepted_Fam_" + std::to_string(familyNum+1) + ".dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    file << "Fracture Radii List Before Removal (Family " << familyNum+1 << ")\n";
    for (auto &poly : acceptedPoly) {
        if (poly.familyNum == familyNum) {
            file << poly.xradius << " " << poly.yradius << " " << poly.familyNum+1 << "\n";
        }
    }
}

/*!
 * \brief Writes radii_Final_Fam_#.dat for each family after removal.
 *
 * \param finalFractures Vector of indices of final accepted fractures.
 * \param familyNum Family number (-2=userRect, -1=userEll, >=0 stochastic).
 * \param acceptedPoly Vector of all accepted polygons.
 * \param output Path to output folder.
 */
void writeFinalRadii_OfFamily(std::vector<unsigned int> &finalFractures,
                              int familyNum,
                              std::vector<Poly> &acceptedPoly,
                              std::string &output) {
    std::string fileName = output + "/radii_Final_Fam_" + std::to_string(familyNum+1) + ".dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    file << "Fracture Radii List After Removal (Family " << familyNum+1 << ")\n";
    for (auto idx : finalFractures) {
        if (acceptedPoly[idx].familyNum == familyNum) {
            file << acceptedPoly[idx].xradius << " "
                 << acceptedPoly[idx].yradius << " "
                 << acceptedPoly[idx].familyNum+1 << "\n";
        }
    }
}

/*!
 * \brief Writes unique triple intersection points to triple_points.dat.
 *
 * \param triplePoints Vector of all triple intersection points.
 * \param finalFractures Vector of indices of final accepted fractures.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param intPts Vector of all intersection structures.
 * \param output Path to output folder.
 */
void writeTriplePts(std::vector<Point> &triplePoints,
                    std::vector<unsigned int> &finalFractures,
                    std::vector<Poly> &acceptedPoly,
                    std::vector<IntPoints> &intPts,
                    std::string &output) {
    std::string fileName = output + "/triple_points.dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    std::vector<unsigned int> triplePtsList;
    for (auto idx : finalFractures) {
        for (auto intIdx : acceptedPoly[idx].intersectionIndex) {
            for (auto tp : intPts[intIdx].triplePointsIdx) {
                triplePtsList.push_back(tp);
            }
        }
    }
    if (!triplePtsList.empty()) {
        std::sort(triplePtsList.begin(), triplePtsList.end());
        unsigned int prev = triplePtsList[0];
        file << std::setprecision(17)
             << triplePoints[prev].x << " "
             << triplePoints[prev].y << " "
             << triplePoints[prev].z << "\n";
        for (size_t i = 1; i < triplePtsList.size(); i++) {
            if (triplePtsList[i] != prev) {
                prev = triplePtsList[i];
                file << std::setprecision(17)
                     << triplePoints[prev].x << " "
                     << triplePoints[prev].y << " "
                     << triplePoints[prev].z << "\n";
            }
        }
    }
}

/*!
 * \brief Writes rejections.dat with counts of rejection reasons.
 *
 * \param pstats Stats structure containing rejection counts.
 * \param output Path to output folder.
 */
void writeRejectionStats(Stats &pstats, std::string &output) {
    std::string fileName = output + "/rejections.dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    logger.writeLogFile(INFO, "Writing Rejection Statistics File (rejections.dat)\n");
    file << "Short Intersection: "    << pstats.rejectionReasons.shortIntersection   << "\n"
         << "Close to Node: "         << pstats.rejectionReasons.closeToNode         << "\n"
         << "Close to Edge: "         << pstats.rejectionReasons.closeToEdge         << "\n"
         << "Vertex Close to Edge: "  << pstats.rejectionReasons.closePointToEdge    << "\n"
         << "Outside of Domain: "     << pstats.rejectionReasons.outside             << "\n"
         << "Triple Intersection: "   << pstats.rejectionReasons.triple              << "\n"
         << "Intersections Too Close: "<< pstats.rejectionReasons.interCloseToInter   << "\n";
}

/*!
 * \brief Writes userFractureRejections.dat listing user-defined fractures rejected.
 *
 * \param pstats Stats structure containing user rejection info.
 * \param output Path to output folder.
 */
void writeUserRejectedFractureInformation(Stats &pstats, std::string &output) {
    if (pstats.rejectedUserFracture.empty()) return;
    std::string fileName = output + "/userFractureRejections.dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    logger.writeLogFile(INFO, "Writing User Fracture Rejection File (userFractureRejections.dat)\n");
    file << "Fracture id,User Fracture Type\n";
    for (auto &r : pstats.rejectedUserFracture) {
        file << r.id << "," << r.userFractureType << "\n";
    }
}

/*!
 * \brief Writes families.dat defining each shape family’s parameters.
 *
 * \param shapeFamilies Vector of all fracture shape families.
 * \param output Path to output folder.
 */
void writeShapeFams(std::vector<Shape> &shapeFamilies, std::string &output) {
    double radToDeg = 180.0 / M_PI;
    std::string fileName = output + "/families.dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    logger.writeLogFile(INFO, "Writing Family Definitions File (families.dat)\n");
    using namespace std;
    if (userEllipsesOnOff)  file << "UserDefined Ellipse Family: 0\n\n";
    if (userRectanglesOnOff)file << "UserDefined Rectangle Family: -1\n\n";
    if (userPolygonByCoord)  file << "UserDefined Polygon Family: -2\n\n";
    for (unsigned int i = 0; i < shapeFamilies.size(); i++) {
        auto &sf = shapeFamilies[i];
        file << shapeType(sf) << " Family: " << getFamilyNumber(i, sf.shapeFamily) << "\n";
        file << "Global Family: " << i+1 << "\n";
        file << "Number of Vertices: " << (sf.shapeFamily==0 ? sf.numPoints : 4) << "\n";
        file << "Aspect Ratio: " << sf.aspectRatio << "\n";
        if (stopCondition == 1) file << "P32 Target: " << sf.p32Target << "\n";
        if (sf.betaDistribution==0)
            file << "Beta Distribution: Uniform\n";
        else {
            file << "Beta (rad): " << sf.beta << "\n";
            file << "Beta (deg): " << sf.beta*radToDeg << "\n";
        }
        if (orientationOption==0) {
            file << "Theta (rad): " << sf.angleOne << "\n";
            file << "Theta (deg): " << sf.angleOne*radToDeg << "\n";
            file << "Phi (rad): "   << sf.angleTwo << "\n";
            file << "Phi (deg): "   << sf.angleTwo*radToDeg << "\n";
        } else if (orientationOption==1) {
            file << "Trend (rad): "  << sf.angleOne << "\n";
            file << "Trend (deg): "  << sf.angleOne*radToDeg << "\n";
            file << "Plunge (rad): " << sf.angleTwo << "\n";
            file << "Plunge (deg): " << sf.angleTwo*radToDeg << "\n";
        } else {
            file << "Dip (rad): "    << sf.angleOne << "\n";
            file << "Dip (deg): "    << sf.angleOne*radToDeg << "\n";
            file << "Strike (rad): " << sf.angleTwo << "\n";
            file << "Strike (deg): " << sf.angleTwo*radToDeg << "\n";
        }
        if (sf.kappa)  file << "Kappa: "  << sf.kappa  << "\n";
        if (sf.kappa2) file << "Kappa2: " << sf.kappa2 << "\n";
        if (sf.layer==0) {
            file << "Layer: Entire domain\n";
        } else {
            int idx = (sf.layer-1)*2;
            file << "Layer Number: " << sf.layer << "\n";
            file << "Layer: {" << layers[idx] << "," << layers[idx+1] << "}\n";
        }
        if (sf.region==0) {
            file << "Region: Entire domain\n";
        } else {
            int idx = (sf.region-1)*6;
            file << "Region Number: " << sf.region << "\n";
            file << "Region: {"
                 << regions[idx]   << "," << regions[idx+1] << ","
                 << regions[idx+2] << "," << regions[idx+3] << ","
                 << regions[idx+4] << "," << regions[idx+5] << "}\n";
        }
        switch (sf.distributionType) {
            case 1:
                file << "Distribution: Lognormal\n"
                     << "Mean: " << sf.mean << "\n"
                     << "SD: "   << sf.sd   << "\n"
                     << "Min Radius: " << sf.logMin << "\n"
                     << "Max Radius: " << sf.logMax << "\n";
                break;
            case 2:
                file << "Distribution: Truncated Power-Law\n"
                     << "Alpha: " << sf.alpha << "\n"
                     << "Min Radius: " << sf.min << "\n"
                     << "Max Radius: " << sf.max << "\n";
                break;
            case 3:
                file << "Distribution: Exponential\n"
                     << "Mean: "   << sf.expMean << "\n"
                     << "Lambda: " << sf.expLambda << "\n"
                     << "Min Radius: " << sf.expMin << "\n"
                     << "Max Radius: " << sf.expMax << "\n";
                break;
            default:
                file << "Distribution: Constant\n"
                     << "Radius: " << sf.constRadi << "\n";
        }
        file << "Family Insertion Probability: " << famProbOriginal[i] << "\n\n";
    }
    file.close();
}

/*!
 * \brief Creates a directory; removes existing first if present.
 *
 * \param dir Path to directory.
 */
void makeDIR(const char *dir) {
    std::string logString;
    if (DIR_exists(dir)) {
        std::string tempStr = "rm -r ";
        tempStr += dir;
        if (system(tempStr.c_str())) {
            logString = "ERROR executing: " + tempStr;
            logger.writeLogFile(ERROR,  logString);
            exit(1);
        }
    }
    if (!DIR_exists(dir)) {
        int dir_err = mkdir(dir, S_IRWXU|S_IRWXG|S_IROTH|S_IXOTH);
        if (dir_err == -1) {
            logString = "Error creating directory " + std::string(dir);
            logger.writeLogFile(ERROR,  logString);
            exit(1);
        }
    }
}

/*!
 * \brief Writes connectivity.dat listing adjacent fractures for each fracture.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param intPts Vector of all intersection structures.
 * \param output Path to output folder.
 */
void writeConnectivity(std::vector<unsigned int> &finalFractures,
                       std::vector<Poly> &acceptedPoly,
                       std::vector<IntPoints> &intPts,
                       std::string &output) {
    std::string fileName = output + "/connectivity.dat";
    std::ofstream file(fileName);
    checkIfOpen(file, fileName);
    logger.writeLogFile(INFO, "Writing Connectivity Data (connectivity.dat)\n");
    for (auto idx : finalFractures) {
        for (auto intIdx : acceptedPoly[idx].intersectionIndex) {
            if (-intPts[intIdx].fract1 == (int)(idx+1))
                file << -intPts[intIdx].fract2 << " ";
            else
                file << -intPts[intIdx].fract1 << " ";
        }
        file << "\n";
    }
}

/*!
 * \brief Writes poly_info.dat containing rotation info for each fracture.
 *
 * \param acceptedPoly Vector of all accepted polygons.
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param shapeFamilies Vector of all fracture shape families.
 * \param output Path to output folder.
 */
void writeRotationData(std::vector<Poly> &acceptedPoly,
                       std::vector<unsigned int> &finalFractures,
                       std::vector<Shape> &shapeFamilies,
                       std::string output) {
    std::string fileOutputFile = output + "/../poly_info.dat";
    std::ofstream file(fileOutputFile);
    checkIfOpen(file, fileOutputFile);
    logger.writeLogFile(INFO, "Writing Rotation Data File (poly_info.dat)\n");
    double maxDomainSize = std::max({domainSize[0], domainSize[1], domainSize[2]}) * 10.0;
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        double normal[3] = {
            acceptedPoly[finalFractures[i]].normal[0],
            acceptedPoly[finalFractures[i]].normal[1],
            acceptedPoly[finalFractures[i]].normal[2]
        };
        double e3[3] = {0,0,1};
        double theta = std::acos(dotProduct(normal,e3)) * (180.0/M_PI);
        double *v = crossProduct(e3, normal);
        if (!(std::abs(v[0])<eps && std::abs(v[1])<eps && std::abs(v[2])<eps))
            normalize(v);
        double x0 = -1.1*maxDomainSize*v[0];
        double y0 = -1.1*maxDomainSize*v[1];
        double z0 = -1.1*maxDomainSize*v[2];
        double x1 =  1.1*maxDomainSize*v[0];
        double y1 =  1.1*maxDomainSize*v[1];
        double z1 =  1.1*maxDomainSize*v[2];
        int famNum = acceptedPoly[finalFractures[i]].familyNum;
        if (famNum < 0) famNum = shapeFamilies.size() + (famNum==-1?1:2);
        file << i+1 << " " << famNum << std::setprecision(15)
             << " " << theta << " " << x0 << " " << y0 << " " << z0
             << " " << x1 << " " << y1 << " " << z1 << "\n";
        delete[] v;
    }
}

/*!
 * \brief Writes normal_vectors.dat containing each fracture’s normal vector.
 *
 * \param acceptedPoly Vector of all accepted polygons.
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param shapeFamilies Vector of all fracture shape families.
 * \param output Path to output folder.
 */
void writeNormalVectors(std::vector<Poly> &acceptedPoly,
                        std::vector<unsigned int> &finalFractures,
                        std::vector<Shape> &shapeFamilies,
                        std::string output) {
    std::string fileOutputFile = output + "/normal_vectors.dat";
    std::ofstream file(fileOutputFile);
    checkIfOpen(file, fileOutputFile);
    logger.writeLogFile(INFO, "Writing Normal Vectors into File (normal_vectors.dat)\n");
    for (auto idx : finalFractures) {
        file << std::setprecision(15)
             << acceptedPoly[idx].normal[0] << " "
             << acceptedPoly[idx].normal[1] << " "
             << acceptedPoly[idx].normal[2] << "\n";
    }
}

/*!
 * \brief Writes rejectsPerAttempt.dat listing insertion attempts per fracture.
 *
 * \param pstats Stats structure containing reject attempt counts.
 * \param output Path to output folder.
 */
void writeRejectsPerAttempt(Stats &pstats, std::string &output) {
    std::string fileOutputFile = output + "/rejectsPerAttempt.dat";
    std::ofstream file(fileOutputFile);
    checkIfOpen(file, fileOutputFile);
    logger.writeLogFile(INFO, "Writing Rotation Data File (rejectsPerAttempt.dat)\n");
    for (auto r : pstats.rejectsPerAttempt) {
        file << r << "\n";
    }
}

/*!
 * \brief Writes graph data files: intersection_list.dat and fracture_info.dat.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 * \param intPts Vector of all intersection structures.
 */
void writeGraphData(std::vector<unsigned int> &finalFractures,
                    std::vector<Poly> &acceptedPoly,
                    std::vector<IntPoints> &intPts) {
    double domainX = domainSize[0]*.5, domainY = domainSize[1]*.5, domainZ = domainSize[2]*.5;
    std::string intFileName   = "dfnGen_output/intersection_list.dat";
    std::string fractFileName = "dfnGen_output/fracture_info.dat";
    std::ofstream intFile(intFileName), fractFile(fractFileName);
    checkIfOpen(intFile,   intFileName);
    checkIfOpen(fractFile, fractFileName);
    logger.writeLogFile(INFO, "Writing Graph Data Files\n");
    intFile << "f1 f2 x y z length\n";
    fractFile << "num_connections perm aperture\n";
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        int num_conn = 0;
        for (auto intIdx : acceptedPoly[finalFractures[i]].intersectionIndex) {
            unsigned int fract1 = -intPts[intIdx].fract1 == i+1 ? -intPts[intIdx].fract1 : -intPts[intIdx].fract2;
            unsigned int fract2 = -intPts[intIdx].fract1 == i+1 ? -intPts[intIdx].fract2 : -intPts[intIdx].fract1;
            if (fract1 < fract2) {
                writeMidPoint(intFile, fract1, fract2,
                              intPts[intIdx].x1, intPts[intIdx].y1, intPts[intIdx].z1,
                              intPts[intIdx].x2, intPts[intIdx].y2, intPts[intIdx].z2);
                num_conn++;
            }
        }
        fractFile << num_conn << " 0 0\n";
    }
}

/*!
 * \brief Writes a single midpoint and line length entry to a file.
 *
 * \param fp Output file stream.
 * \param fract1 First fracture ID.
 * \param fract2 Second fracture ID.
 * \param x1 X coordinate of first endpoint.
 * \param y1 Y coordinate of first endpoint.
 * \param z1 Z coordinate of first endpoint.
 * \param x2 X coordinate of second endpoint.
 * \param y2 Y coordinate of second endpoint.
 * \param z2 Z coordinate of second endpoint.
 */
void writeMidPoint(std::ofstream &fp,
                   int fract1,
                   int fract2,
                   double x1, double y1, double z1,
                   double x2, double y2, double z2) {
    Point p1{x1,y1,z1}, p2{x2,y2,z2}, pm;
    pm.x = 0.5*(p1.x + p2.x);
    pm.y = 0.5*(p1.y + p2.y);
    pm.z = 0.5*(p1.z + p2.z);
    double curLength = euclideanDistance(p1, p2);
    fp << fract1 << " " << fract2
       << std::setprecision(10) << " "
       << pm.x << " " << pm.y << " " << pm.z << " "
       << curLength << "\n";
}

/*!
 * \brief Writes boundary files listing fractures touching each domain boundary.
 *
 * \param finalFractures Vector of indices of accepted fractures after isolation removal.
 * \param acceptedPoly Vector of all accepted polygons.
 */
void writeBoundaryFiles(std::vector<unsigned int> &finalFractures,
                        std::vector<Poly> &acceptedPoly) {
    logger.writeLogFile(INFO, "Writing Boundary Files\n");
    std::ofstream left("dfnGen_output/left.dat"),
                  right("dfnGen_output/right.dat"),
                  front("dfnGen_output/front.dat"),
                  back("dfnGen_output/back.dat"),
                  top("dfnGen_output/top.dat"),
                  bottom("dfnGen_output/bottom.dat");
    checkIfOpen(left,   "dfnGen_output/left.dat");
    checkIfOpen(right,  "dfnGen_output/right.dat");
    checkIfOpen(front,  "dfnGen_output/front.dat");
    checkIfOpen(back,   "dfnGen_output/back.dat");
    checkIfOpen(top,    "dfnGen_output/top.dat");
    checkIfOpen(bottom, "dfnGen_output/bottom.dat");
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        auto &faces = acceptedPoly[finalFractures[i]].faces;
        if (faces[0]>0) right << i+1 << "\n";
        if (faces[1]>0) left  << i+1 << "\n";
        if (faces[2]>0) front << i+1 << "\n";
        if (faces[3]>0) back  << i+1 << "\n";
        if (faces[4]>0) top   << i+1 << "\n";
        if (faces[5]>0) bottom<< i+1 << "\n";
    }
    left.close(); right.close();
    front.close(); back.close();
    top.close();   bottom.close();
}