#include <iostream>
#include <ctime>
#include <random>
#include <algorithm>
#include <iterator> // std::copy
#include <iomanip>
#include "structures.h"
#include "insertShape.h"
#include <vector>
#include "input.h"
#include "output.h"
#include "readInputFunctions.h"
#include "clusterGroups.h"
#include "mathFunctions.h"
#include "domain.h"
#include "computationalGeometry.h"
#include "generatingPoints.h"
#include "distributions.h"
#include "fractureEstimating.h"
#include "debugFunctions.h"
#include "removeFractures.h"

// Used for automated python testing
#include "testing.h"

// Below includes are used for hotkey,
// Stops inserting fractures and goes directly to output
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/select.h>
#include <termios.h>
#include "hotkey.h"


// DO NOT CHANGE VAR NAME
struct termios orig_termios; //used for custom console and hotkey

// Global eps
double eps;

// SEE STRUCTURES.H FOR ALL STRUCTURE DEFINITIONS
int main (int argc, char **argv) {
    std::cout << "\n";
    
    // Error check on cmd line input:
    // 1st argument = input file path
    // 2nd argument = output folder path
    if (argc != 3) {
        if (argc == 1 ) {
            std::cout << "ERROR: DFNWorks input and output file "
                      << "paths were not included on command line.\n";
            return 1;
        } else if (argc == 2) {
            std::cout << "ERROR: DFNWorks output file path "
                      << "was not included on command line.\n";
            return 1;
        }
    }
    
    /************* Initialize Arrays/Vectors and Structures **************/
    // Vector to store accepted polygons/fractures
    std::vector<Poly> acceptedPoly;
    acceptedPoly.reserve(500);
    // Vector for storing intersections
    std::vector<IntPoints> intPts;
    intPts.reserve(250);
    // Vector for storing triple intersection points
    std::vector<Point> triplePoints;
    // Vector for shape families/ stochastic families
    std::vector<Shape> shapeFamilies;
    // Statistics structure:
    // Keeps track of DFN statistics (see definition in structures.h)
    Stats pstats;
    /*********************************************************************/
    // Read Input File
    // Initialize input variables. Most input variables are global
    getInput(argv[1], shapeFamilies);
    // Set epsilon
    eps = h * 1e-8;
    std::cout << "\nh: " << h << "\n";
    int totalFamilies = nFamEll + nFamRect;
    
    // Print shape families to screen
    if (totalFamilies > 0) {
        printShapeFams(shapeFamilies);
    }
    
    // Initialize random generator with seed ( see c++ <random> )
    // Mersene Twister 19937 generator (64 bit)
    if (seed == 0) {
        seed = getTimeBasedSeed();
    }
    
    std::mt19937_64 generator(seed);
    // Init distributions class
    // Currenlty used only for exponential distribution
    Distributions distributions(generator, shapeFamilies);
    float domVol = domainSize[0] * domainSize[1] * domainSize[2];
    
    if (totalFamilies > 0 ) {
        if (stopCondition == 0) { // Npoly Option
            // Estimate fractures, generate radii lists for nPoly option
            generateRadiiLists_nPolyOption(shapeFamilies, famProb, generator, distributions);
        } else { // P32 Option
            // ESTIMATE # FRACTURES NEEDED
            if (disableFram == false) {
                std::cout << "\nEstimating number of fractures needed...\n";
                dryRun(shapeFamilies, famProb, generator, distributions);
            }
        }
        
        // Add a percentage more radii to each radii
        // list using families' distribution.
        // First arg is percentage, eg: 0.1 will add 10% more fractures
        // to the radii list for each family
        if (disableFram == false) {
            addRadiiToLists(radiiListIncrease, shapeFamilies, generator, distributions);
            
            for (unsigned int j = 0; j < shapeFamilies.size(); j++) {
                if (shapeFamilies[j].distributionType == 4) {
                    // Constant size
                    std::cout << shapeType(shapeFamilies[j])
                              << " family " << getFamilyNumber(j, shapeFamilies[j].shapeFamily)
                              << " using constant size\n";
                } else {
                    std::cout << "Estimated " << shapeFamilies[j].radiiList.size()
                              << " fractures for " <<  shapeType(shapeFamilies[j])
                              << " family " << getFamilyNumber(j, shapeFamilies[j].shapeFamily)
                              << "\n";
                }
            }
            
            sortRadii(shapeFamilies);
        }
        
        // Keep count of accepted & rejected fractures by family
        pstats.acceptedFromFam = new int[totalFamilies];
        pstats.rejectedFromFam = new int[totalFamilies];
        // Save sizes of pre-generated radii lists per family.
        // Print as part of statistics to user
        pstats.expectedFromFam = new int[totalFamilies];
        
        // Zero arrays, init expectedFromFam array
        for (int i = 0; i < totalFamilies; i++) {
            pstats.acceptedFromFam[i] = 0;
            pstats.rejectedFromFam[i] = 0;
            pstats.expectedFromFam[i] = shapeFamilies[i].radiiList.size();
        }
        
        // Init first rejects per insertion attempt counter
        pstats.rejectsPerAttempt.push_back(0);
    }
    
    /*********** SETUP HOT KEY *************/
    char key = 0;
#ifndef TESTING
    // Set custom terminal settings for hotkey functionality
    set_conio_terminal_mode();
    atexit(reset_terminal_mode);
#endif
    /*********  END SETUP HOT KEY **********/
    
    /********************* User Defined Shapes Insertion ************************/
    // User Polygons are always inserted first
    if (userPolygonByCoord != 0) {
        insertUserPolygonByCoord(acceptedPoly, intPts, pstats, triplePoints);
    }
    
    if (insertUserRectanglesFirst == 1) {
        // Insert user rects first
        if (userRectanglesOnOff != 0) {
            insertUserRects(acceptedPoly, intPts, pstats, triplePoints);
        }
        
        // Insert all user rectangles by coordinates
        if (userRecByCoord != 0 ) {
            insertUserRectsByCoord(acceptedPoly, intPts, pstats, triplePoints);
        }
        
        // Insert all user ellipses
        if (userEllipsesOnOff != 0) {
            insertUserEll(acceptedPoly, intPts, pstats, triplePoints);
        }
        
        // Insert all user ellipses by coordinates
        if (userEllByCoord != 0) {
            insertUserEllByCoord(acceptedPoly, intPts, pstats, triplePoints);
        }
    } else {
        // Insert all user ellipses first
        if (userEllipsesOnOff != 0) {
            insertUserEll(acceptedPoly, intPts, pstats, triplePoints);
        }
        
        // Insert all user ellipses by coordinates
        if (userEllByCoord != 0) {
            insertUserEllByCoord(acceptedPoly, intPts, pstats, triplePoints);
        }
        
        // Insert user rects
        if (userRectanglesOnOff != 0) {
            insertUserRects(acceptedPoly, intPts, pstats, triplePoints);
        }
        
        // Insert all user rectangles by coordinates
        if (userRecByCoord != 0 ) {
            insertUserRectsByCoord(acceptedPoly, intPts, pstats, triplePoints);
        }
    }
    
    /*********  Probabilities (famProb) setup, CDF init  *****************/
    // 'CDF' size will shrink along when used with fracture intensity (P32) option
    float *CDF;
    int cdfSize = totalFamilies;
    
    if (totalFamilies > 0) {
        // Convert famProb to CDF
        CDF = createCDF(famProb, cdfSize);
    }
    
    std::ofstream radiiAll;
    std::string output = argv[2];
    std::string radiiFolder = output + "/radii";
    // Create output folder if not already created
    //makeDIR(argv[2]);
    // Create radii folder
    //makeDIR(radiiFolder.c_str());
    // Create polys folder
    std::string  polyFolder = output + "/polys";
    //makeDIR(polyFolder.c_str());
    
    if (outputAllRadii == 1) {
        // Option to include all radii in output (accepted and rejected)
        std::string file = radiiFolder + "/radii_All.dat";
        radiiAll.open(file.c_str(), std::ofstream::out | std::ofstream::trunc);
        radiiAll << "Format: xRadius yRadius Family# (-1 = userRectangle, 0 = userEllipse, > 0 is family in order of famProb)\n";
    }
    
    // Initialize uniform distribution on [0,1]
    std::uniform_real_distribution<double> uniformDist(0, 1);
    
    if (totalFamilies > 0) {
        // Holds index to current 'shapeFamily' being inserted
        int familyIndex;
        
        /******************************************************************************************/
        /**************************             MAIN LOOP            ******************************/
        
        // NOTE: p32Complete() works on global array 'p32Status'
        // p32Complete() only needs argument of the number of defined shape families
        // ********* Begin stochastic fracture insertion ***********
        while (((stopCondition == 0 && pstats.acceptedPolyCount < nPoly) || (stopCondition == 1 && p32Complete(totalFamilies) == 0)) && key != '~' ) {
            // cdfIdx holds the index to the CDF array for the current shape family being inserted
            int cdfIdx;
            
            if (stopCondition == 0 ) { // nPoly Option
                // Choose a family based purely on famProb probabilities
                familyIndex = indexFromProb(CDF, uniformDist(generator), totalFamilies);
            }
            // Choose a family based on probabiliyis AND their target p32 completion status.
            // If a family has already met is fracture intinisty req. (p32) don't choose that family anymore
            else { // P32 Option
                familyIndex = indexFromProb_and_P32Status(CDF, uniformDist(generator), totalFamilies, cdfSize, cdfIdx);
            }
            
            struct Poly newPoly = generatePoly(shapeFamilies[familyIndex], generator, distributions, familyIndex, true);
            
            if (outputAllRadii == 1) {
                // Output all radii
                radiiAll << std::setprecision(8) <<  newPoly.xradius << " " << newPoly.yradius
                         << " " << newPoly.familyNum + 1 << "\n";
            }
            
            int rejectCode = 1;
            int rejectCounter = 0;
            
            while (rejectCode != 0) { // Loop used to reinsert same poly with different translation
            
                // HOT KEY: check for keyboard input
                if (kbhit()) {
                    key = getch();
                }
                
                // Truncate poly if needed
                // 1 if poly is outside of domain or has less than 3 vertices
                if ( domainTruncation(newPoly, domainSize) == 1) {
                    // Poly was completely outside domain, or was truncated to less than
                    // 3 vertices due to vertices being too close together
                    pstats.rejectionReasons.outside++;
                    
                    // Test if newPoly has reached its limit of insertion attempts
                    if (rejectCounter >= rejectsPerFracture) {
                        delete[] newPoly.vertices; // Created with new, delete manually
                        rejectCounter++;
                        break; // Reject poly, generate new polygon
                    } else { // Retranslate poly and try again, preserving normal, size, and shape
                        reTranslatePoly(newPoly, shapeFamilies[familyIndex], generator);
                        continue; // Go to next iteration of while loop, test new translation
                    }
                }
                
                // Create/assign bounding box
                createBoundingBox(newPoly);
                // Find line of intersection and FRAM check
                rejectCode = intersectionChecking(newPoly, acceptedPoly, intPts, pstats, triplePoints);
                // Find line of intersection and FRAM check
                // if (disableFram == false) {
                //     rejectCode = intersectionChecking(newPoly, acceptedPoly, intPts, pstats, triplePoints);
                // }
                // else{
                //     rejectCode = 0;
                // }
#ifdef TESTING
                
                if (rejectCode != 0) {
                    return 1;
                }
                
#endif
                
                // IF POLY ACCEPTED:
                if(rejectCode == 0) { // Intersections are ok
                    // Incriment counter of accepted polys
                    pstats.acceptedPolyCount++;
                    pstats.acceptedFromFam[familyIndex]++;
                    // Make new rejection counter for next fracture attempt
                    pstats.rejectsPerAttempt.push_back(0);
                    
                    if (newPoly.truncated == 1) {
                        pstats.truncated++;
                    }
                    
                    // Calculate poly's area
                    newPoly.area = getArea(newPoly);
                    
                    // Update P32
                    if (shapeFamilies[familyIndex].layer == 0 && shapeFamilies[familyIndex].region == 0) { // Whole domain
                        shapeFamilies[familyIndex].currentP32 += newPoly.area * 2 / domVol;
                    } else if (shapeFamilies[familyIndex].layer > 0 && shapeFamilies[familyIndex].region == 0) { // Layer
                        shapeFamilies[familyIndex].currentP32 += newPoly.area * 2 / layerVol[shapeFamilies[familyIndex].layer - 1];
                    } else if (shapeFamilies[familyIndex].layer == 0 && shapeFamilies[familyIndex].region > 0) { // Region
                        shapeFamilies[familyIndex].currentP32 += newPoly.area * 2 / regionVol[shapeFamilies[familyIndex].region - 1];
                    }
                    
                    if (stopCondition == 1) {
                        // If the last inserted pologon met the p32 reqirement, set that familiy to no longer
                        // insert any more fractures. ajust the CDF and familiy probabilites to account for this
                        if (shapeFamilies[familyIndex].currentP32 >= shapeFamilies[familyIndex].p32Target ) {
                            p32Status[familyIndex] = 1; // Mark family as having its p32 requirement met
                            std::cout << "\nP32 For Family " << familyIndex + 1 << " Completed\n\n";
                            
                            // Adjust CDF, PDF. Reduce their size by 1.
                            // Remove the completed family's element in 'CDF[]' and 'famProb[]'
                            // Distribute the removed family probability evenly among the others and rebuild the CDF
                            // familyIndex = index of family's probability
                            // cdfIdx = index of the completed family's correspongding CDF index
                            if (cdfSize > 1 ) { // If there are still more families to insert
                                // Remove completed family from CDF and famProb
                                adjustCDF_and_famProb(CDF, famProb, cdfSize, cdfIdx);
                            }
                        }
                    }
                    
                    // Output to user: print running program status to user
                    if (pstats.acceptedPolyCount % 200 == 0) {
                        std::cout << "\nAccepted " << pstats.acceptedPolyCount << " fractures\n";
                        std::cout << "Rejected " << pstats.rejectedPolyCount << " fractures\n";
                        std::cout << "Re-translated " << pstats.retranslatedPolyCount << " fractures\n\n";
                        std::cout << "Current p32 values per family:\n";
                        
                        for (int i = 0; i < totalFamilies; i++) {
                            if (stopCondition == 0) {
                                std::cout << shapeType(shapeFamilies[i]) << " family "
                                          << getFamilyNumber(i, shapeFamilies[i].shapeFamily)
                                          << " Current P32 = " << std::setprecision(8)
                                          << shapeFamilies[i].currentP32;
                            } else {
                                std::cout << shapeType(shapeFamilies[i]) << " family "
                                          << getFamilyNumber(i, shapeFamilies[i].shapeFamily)
                                          << " target P32 = " << std::setprecision(8)
                                          << shapeFamilies[i].p32Target
                                          << ", " << "Current P32 = " << shapeFamilies[i].currentP32;
                            }
                            
                            if (stopCondition == 1 && shapeFamilies[i].p32Target <= shapeFamilies[i].currentP32) {
                                std::cout << "...Done\n";
                            } else {
                                std::cout << "\n";
                            }
                        }
                    }
                    
                    // SAVING POLYGON (intersection and triple points saved witchin intersectionChecking())
                    acceptedPoly.push_back(newPoly); // SAVE newPoly to accepted polys list
                } else { // Poly rejected
                    // Inc reject counter for current poly
                    rejectCounter++;
                    // Inc reject counter for current attempt
                    // (number of rejects until next fracture accepted)
                    pstats.rejectsPerAttempt[pstats.acceptedPolyCount]++;
                    
                    if (printRejectReasons != 0) {
                        printRejectReason(rejectCode, newPoly);
                    }
                    
                    if (rejectCounter >= rejectsPerFracture) {
                        delete[] newPoly.vertices; // Delete manually, created with new[]
                        pstats.rejectedPolyCount++;
                        pstats.rejectedFromFam[familyIndex]++;
                        // Stop retranslating polygon if its reached its reject limit
                        break; // Break will cause code to go to next poly
                    } else {
                        // Translate poly to new position
                        if (printRejectReasons != 0) {
                            std::cout << "Translating rejected fracture to new position\n";
                        }
                        
                        pstats.retranslatedPolyCount++;
                        reTranslatePoly(newPoly, shapeFamilies[familyIndex], generator);
                    }
                } // End else poly rejected
            } // End loop while for re-translating polys option (reject == 1)
        } // !!!!  END MAIN LOOP !!!! end while loop for inserting polyons
        
        /************************** DFN GENERATION IS COMPLETE ***************************/
        
        // Remove last element off the rejects per attempt counter.
        // It will have one extra item due to how eachelement is initialized.
        if (!pstats.rejectsPerAttempt.empty()) {
            pstats.rejectsPerAttempt.pop_back();
        }
    } // End if totalFamilies != 0
    
//    printIntersectionData(intPts);
//    printGroupData(pstats,acceptedPoly);
    // The close to node check is inside of the close to edge check function
    // for optimization (only need do intersection close to node on one condition)
    // On close to node rejections, close to edge is counted as well.
    // To get the correct number we must subtract the close to node count
    // (they were counted in closeToEdge AND closeToNode)
    pstats.rejectionReasons.closeToEdge -= pstats.rejectionReasons.closeToNode;
#ifndef TESTING
    reset_terminal_mode();
#endif
    
    if (outputAllRadii == 1) {
        radiiAll.close();
    }
    
    // Assign apertures and permiability to accepted polygons
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        assignAperture(acceptedPoly[i], generator);
        // NOTE: must assign aperture before permeability
        assignPermeability(acceptedPoly[i]);
    }
    
    // Copy end of DFN generation stats to file, as well as print to screen
    std::ofstream file;
    std::string fileName = output + "/DFN_output.txt";
    file.open(fileName.c_str(), std::ofstream::out | std::ofstream::trunc);
    file << "\n========================================================\n";
    file << "            Network Generation Complete\n";
    file << "========================================================\n";
    file << "Version of DFNGen: 2.2\n";
    std::time_t result = std::time(nullptr);
    file << "Time Stamp: " << std::asctime(std::localtime(&result)) << "\n";
    std::cout << "\n========================================================\n";
    std::cout << "            Network Generation Complete\n";
    std::cout << "========================================================\n";
    std::cout << "Version of DFNGen: 2.2\n";
    std::cout << "Time Stamp: " << std::asctime(std::localtime(&result)) << "\n";
    
    if (stopCondition == 1 ) {
        std::cout << "\nFinal p32 values per family:\n";
        
        for (int i = 0; i < totalFamilies; i++) {
            std::cout << "Family " << i + 1 << " target P32 = " << shapeFamilies[i].p32Target
                      << ", " << "Final P32 = " << shapeFamilies[i].currentP32 << "\n";
            file << "Family " << i + 1 << " target P32 = " << shapeFamilies[i].p32Target
                 << ", " << "Final P32 = " << shapeFamilies[i].currentP32 << "\n";
        }
    }
    
    std::cout << "\n________________________________________________________\n";
    file << "\n________________________________________________________\n";
    // Calculate total area, volume
    double userDefinedShapesArea = 0;
    double userDefinedVol = 0;
    double *familyArea = nullptr;
    double *familyVol = nullptr;
    
    if (totalFamilies > 0 ) {
        familyArea = new double[totalFamilies]; // Holds fracture area per family
        familyVol = new double[totalFamilies];
        
        // Zero array
        for (int i = 0; i < totalFamilies; i++) {
            familyArea[i] = 0;
            familyVol[i] = 0;
        }
    }
    
    std::cout << "\nStatistics Before Isolated Fractures Removed:\n\n";
    std::cout << "Fractures: " << acceptedPoly.size() << "\n";
    std::cout << "Truncated: " << pstats.truncated << "\n\n";
    file << "\nStatistics Before Isolated Fractures Removed:\n\n";
    file << "Fractures: " << acceptedPoly.size() << "\n";
    file << "Truncated: " << pstats.truncated << "\n\n";
    
    // Calculate total fracture area, and area per family
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        double area = acceptedPoly[i].area;
        double vol = area * acceptedPoly[i].aperture;
        pstats.areaBeforeRemoval += area;
        pstats.volBeforeRemoval += vol;
        
        if (acceptedPoly[i].familyNum >= 0) {
            familyArea[acceptedPoly[i].familyNum] += area;
            familyVol[acceptedPoly[i].familyNum] += vol;
        } else { // User-defined polygon
            userDefinedShapesArea += area;
            userDefinedVol += vol;
        }
    }
    
    std::cout << "Total Surface Area:     " << pstats.areaBeforeRemoval * 2 << " m^2\n";
    std::cout << "Total Fractures Volume: " << pstats.volBeforeRemoval << " m^3\n";
    std::cout << "Total Fracture Density   (P30): " << acceptedPoly.size() / domVol << "\n";
    std::cout << "Total Fracture Intensity (P32): " << (pstats.areaBeforeRemoval * 2) / domVol << "\n";
    std::cout << "Total Fracture Porosity  (P33): " << pstats.volBeforeRemoval / domVol << "\n\n";
    file << "Total Surface Area:     " << pstats.areaBeforeRemoval * 2 << " m^2\n";
    file << "Total Fractures Volume: " << pstats.volBeforeRemoval << " m^3\n";
    file << "Total Fracture Density   (P30): " << acceptedPoly.size() / domVol << "\n";
    file << "Total Fracture Intensity (P32): " << (pstats.areaBeforeRemoval * 2) / domVol << "\n";
    file << "Total Fracture Porosity  (P33): " << pstats.volBeforeRemoval / domVol << "\n\n";
    
    // Print family stats to user
    for (int i = 0; i < totalFamilies; i++) {
        std::cout << "Family: " << i + 1 << "\n";
        std::cout << "    Accepted: " << pstats.acceptedFromFam[i] << "\n";
        std::cout << "    Rejected: " << pstats.rejectedFromFam[i] << "\n";
        file << "Family: " << i + 1 << "\n";
        file << "    Accepted: " << pstats.acceptedFromFam[i] << "\n";
        file << "    Rejected: " << pstats.rejectedFromFam[i] << "\n";
        
        if ( shapeFamilies[i].layer > 0) {
            int idx = (shapeFamilies[i].layer - 1) * 2;
            std::cout << "    Layer: " << shapeFamilies[i].layer << "\n";
            std::cout << "    Layer {-z, +z}: {" << layers[idx] << ", " << layers[idx + 1] << "}\n";
            file << "    Layer: " << shapeFamilies[i].layer << "\n";
            file << "    Layer {-z, +z}: {" << layers[idx] << ", " << layers[idx + 1] << "}\n";
        } else {
            std::cout << "    Layer: Whole Domain \n";
            file << "    Layer: Whole Domain \n";
        }
        
        if ( shapeFamilies[i].region > 0) {
            int idx = (shapeFamilies[i].region - 1) * 6;
            std::cout << "    Region: " << shapeFamilies[i].region << "\n";
            std::cout << "    {-x,+x,-y,+y,-z,+z}: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
            file << "    Region: " << shapeFamilies[i].region << "\n";
            file << "    {-x,+x,-y,+y,-z,+z}: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
        } else {
            std::cout << "    Region: Whole Domain \n";
            file << "    Region: Whole Domain \n";
        }
        
        std::cout << "    Surface Area: " << familyArea[i] * 2 << " m^2\n";
        std::cout << "    Volume: " << familyVol[i] << " m^3\n";
        std::cout << "    Fracture Intensity (P32): " << shapeFamilies[i].currentP32 << "\n\n";
        file << "    Surface Area: " << familyArea[i] * 2 << " m^2\n";
        file << "    Volume: " << familyVol[i] << " m^3\n";
        file << "    Fracture Intensity (P32): " << shapeFamilies[i].currentP32 << "\n\n";
    }
    
    if (userDefinedShapesArea > 0) {
        std::cout << "User Defined: \n";
        std::cout << "    Surface Area: " << userDefinedShapesArea * 2 << " m^2\n";
        std::cout << "    Volume: " << userDefinedVol << " m^3\n";
        std::cout << "    Fracture Intensity (P32): " << userDefinedShapesArea * 2 / domVol << "\n\n";
        file << "User Defined: \n";
        file << "    Surface Area: " << userDefinedShapesArea * 2 << " m^2\n";
        file << "    Volume: " << userDefinedVol << " m^3\n";
        file << "    Fracture Intensity (P32): " << userDefinedShapesArea * 2 / domVol << "\n\n";
    }
    
    if (removeFracturesLessThan > 0) {
        std::cout << "\nRemoving fractures with radius less than " << removeFracturesLessThan << " and rebuilding DFN\n";
        file      << "\nRemoving fractures with radius less than " << removeFracturesLessThan << " and rebuilding DFN\n";
        int size = acceptedPoly.size();
        removeFractures(removeFracturesLessThan, acceptedPoly, intPts, triplePoints, pstats);
        std::cout << "Removed " << size - acceptedPoly.size() << " fractures with radius less than " << removeFracturesLessThan << "\n\n";
        file      << "Removed " << size - acceptedPoly.size() << " fractures with radius less than " << removeFracturesLessThan << "\n\n";
    }
    
    /*  Remove any isolated fractures and return
        a list of polygon indices matching the users
        boundaryFaces option. If input option
        keepOnlyLargestCluster = 1, return largest
        cluster matching users boundaryFaces option
        If ignoreBoundaryFaces input option is on,
        DFN will keep all fractures with intersections.
    */
    std::vector<unsigned int> finalFractures =  getCluster(pstats);
    // Sort fracture indecies to retain order by acceptance
    std::sort (finalFractures.begin(), finalFractures.end());
    // Error check for no boundary connection
    bool printConnectivityError = 0;
    
    if (finalFractures.size() == 0 && ignoreBoundaryFaces == 0 ) {
        printConnectivityError = 1;
        //if there is no fracture network connected users defined boundary faces
        //switch to ignore boundary faces option with notice to user that there is no connectivity
        finalFractures =  getCluster(pstats);
        //if still no fractures, there is no fracture network
    }
    
    if (finalFractures.size() == 0) {
        std::cout << "\nERROR: DFN Generation has finished, however"
                  << " there are no intersecting fractures."
                  << " Please adjust input parameters.\n";
        std::cout << "Try increasing the fracture density, or shrinking the domain.\n";
        file << "\nERROR: DFN Generation has finished, however"
             << " there are no intersecting fractures."
             << " Please adjust input parameters.\n";
        file << "Try increasing the fracture density, or shrinking the domain.\n";
        file.close();
        exit(1);
    }
    
    /************************* Print Statistics to User ***********************************/
    std::cout << "\n________________________________________________________\n\n";
    std::cout << "Statistics After Isolated Fractures Removed:\n";
    std::cout << "Final Number of Fractures: " << finalFractures.size() << "\n";
    std::cout << "Isolated Fractures Removed: " << acceptedPoly.size() - finalFractures.size() << "\n";
    std::cout << "Fractures before isolated fractures removed:: " << acceptedPoly.size() << "\n\n";
    file << "\n________________________________________________________\n\n";
    file << "Statistics After Isolated Fractures Removed:\n";
    file << "Final Number of Fractures: " << finalFractures.size() << "\n";
    file << "Isolated Fractures Removed: " << acceptedPoly.size() - finalFractures.size() << "\n";
    file << "Fractures before isolated fractures removed:: " << acceptedPoly.size() << "\n\n";
    // Reset totalVolume and totalArea to 0
    userDefinedShapesArea = 0;
    userDefinedVol = 0;
    
    if (totalFamilies > 0 ) {
        //zero out array.
        for (int i = 0; i < totalFamilies; i++) {
            familyArea[i] = 0;
            familyVol[i] = 0;
        }
    }
    
    // Calculate total fracture area, and area per family
    for (unsigned int i = 0; i < finalFractures.size(); i++) {
        double area = acceptedPoly[finalFractures[i]].area;
        double vol = area * acceptedPoly[finalFractures[i]].aperture;
        pstats.areaAfterRemoval += area;
        pstats.volAfterRemoval += vol;
        
        if (acceptedPoly[finalFractures[i]].familyNum >= 0) {
            familyArea[acceptedPoly[finalFractures[i]].familyNum] += area;
            familyVol[acceptedPoly[finalFractures[i]].familyNum] += vol;
        } else { // User-defined polygon
            userDefinedShapesArea += area;
            userDefinedVol += vol;
        }
    }
    
    // Re-count number of accepted fracture per family after isloated fractures were removed
    int *acceptedFromFamCounters = nullptr;
    
    if (totalFamilies > 0) {
        acceptedFromFamCounters = new int[totalFamilies];
        
        for (int i = 0; i < totalFamilies; i++) {
            // zero counters
            acceptedFromFamCounters[i] = 0;
        }
        
        int size = finalFractures.size();
        
        for (int i = 0; i < size; i++) {
            if (acceptedPoly[finalFractures[i]].familyNum >= 0) {
                acceptedFromFamCounters[acceptedPoly[finalFractures[i]].familyNum]++;
            }
        }
    }
    
    std::cout << "Total Surface Area:     " << pstats.areaAfterRemoval * 2 << " m^2\n";
    std::cout << "Total Fractures Volume: " << pstats.volAfterRemoval << " m^3\n";
    std::cout << "Total Fracture Density   (P30): " << finalFractures.size() / domVol << "\n";
    std::cout << "Total Fracture Intensity (P32): " << (pstats.areaAfterRemoval * 2) / domVol << "\n";
    std::cout << "Total Fracture Porosity  (P33): " << pstats.volAfterRemoval / domVol << "\n\n";
    file << "Total Surface Area:     " << pstats.areaAfterRemoval * 2 << " m^2\n";
    file << "Total Fractures Volume: " << pstats.volAfterRemoval << " m^3\n";
    file << "Total Fracture Density   (P30): " << finalFractures.size() / domVol << "\n";
    file << "Total Fracture Intensity (P32): " << (pstats.areaAfterRemoval * 2) / domVol << "\n";
    file << "Total Fracture Porosity  (P33): " << pstats.volAfterRemoval / domVol << "\n\n";
    
    // Print family stats to user
    for (int i = 0; i < totalFamilies; i++) {
        std::cout << "Family: " << i + 1 << "\n";
        std::cout << "    Fractures After Isolated Fracture Removal: " << acceptedFromFamCounters[i] << "\n";
        std::cout << "    Isolated Fractures Removed: " << pstats.acceptedFromFam[i] - acceptedFromFamCounters[i] << "\n";
        std::cout << "    Accepted: " << pstats.acceptedFromFam[i] << "\n";
        std::cout << "    Rejected: " << pstats.rejectedFromFam[i] << "\n";
        file << "Family: " << i + 1 << "\n";
        file << "    Fractures After Isolated Fracture Removal: " << acceptedFromFamCounters[i] << "\n";
        file << "    Isolated Fractures Removed: " << pstats.acceptedFromFam[i] - acceptedFromFamCounters[i] << "\n";
        file << "    Accepted: " << pstats.acceptedFromFam[i] << "\n";
        file << "    Rejected: " << pstats.rejectedFromFam[i] << "\n";
        
        if ( shapeFamilies[i].layer > 0) {
            int idx = (shapeFamilies[i].layer - 1) * 2;
            std::cout << "    Layer: " << shapeFamilies[i].layer << "\n";
            std::cout << "    Layer {-z, +z}: {" << layers[idx] << "," << layers[idx + 1] << "}\n";
            file << "    Layer: " << shapeFamilies[i].layer << "\n";
            file << "    Layer {-z, +z}: {" << layers[idx] << "," << layers[idx + 1] << "}\n";
        } else {
            std::cout << "    Layer: Whole Domain \n";
            file << "    Layer: Whole Domain \n";
        }
        
        if ( shapeFamilies[i].region > 0) {
            int idx = (shapeFamilies[i].region - 1) * 6;
            std::cout << "    Region: " << shapeFamilies[i].region << "\n";
            std::cout << "    {-x,+x,-y,+y,-z,+z}: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
            file << "    Region: " << shapeFamilies[i].region << "\n";
            file << "    {-x,+x,-y,+y,-z,+z}: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
        } else {
            std::cout << "    Region: Whole Domain \n";
            file << "    Region: Whole Domain \n";
        }
        
        std::cout << "    Surface Area: " << familyArea[i] * 2 << " m^2\n";
        std::cout << "    Volume: " << familyVol[i] << " m^3\n";
        std::cout << "    Fracture Intensity (P32): " << familyArea[i] * 2 / domVol << "\n\n";
        file << "    Surface Area: " << familyArea[i] * 2 << " m^2\n";
        file << "    Volume: " << familyVol[i] << " m^3\n";
        file << "    Fracture Intensity (P32): " << familyArea[i] * 2 / domVol << "\n\n";
    }
    
    if (userDefinedShapesArea > 0) {
        std::cout << "User Defined Shapes: \n";
        std::cout << "    Surface Area: " << userDefinedShapesArea * 2 << " m^2\n";
        std::cout << "    Volume: " << userDefinedVol << " m^3\n";
        std::cout << "    Fracture Intensity (P32): " << userDefinedShapesArea * 2 / domVol << "\n\n";
        file << "User Defined Shapes: \n";
        file << "    Surface Area: " << userDefinedShapesArea * 2 << " m^2\n";
        file << "    Volume: " << userDefinedVol << " m^3\n";
        file << "    Fracture Intensity (P32): " << userDefinedShapesArea * 2 / domVol << "\n\n";
    }
    
    if (acceptedFromFamCounters != nullptr) {
        delete[] acceptedFromFamCounters;
    }
    
    std::cout << "\n________________________________________________________\n\n";
    file << "\n________________________________________________________\n\n";
    std::cout << "\n" << acceptedPoly.size() << " Fractures Accepted (Before Isolated Fracture Removal)\n";
    std::cout << finalFractures.size() << " Final Fractures (After Isolated Fracture Removal)\n\n";
    std::cout << "Total Fractures Rejected: " << pstats.rejectedPolyCount << "\n";
    std::cout << "Total Fractures Re-translated: " << pstats.retranslatedPolyCount << "\n";
    file << "\n" << acceptedPoly.size() << " Fractures Accepted (Before Isolated Fracture Removal)\n";
    file << finalFractures.size() << " Final Fractures (After Isolated Fracture Removal)\n\n";
    file << "Total Fractures Rejected: " << pstats.rejectedPolyCount << "\n";
    file << "Total Fractures Re-translated: " << pstats.retranslatedPolyCount << "\n";
    
    if (printConnectivityError == 1) {
        std::cout << "\nERROR: DFN generation has finished but the formed\n"
                  << "fracture network does not make a connection between\n"
                  << "the user's specified boundary faces.\n";
        std::cout << "Try increasing the fracture density, shrinking the domain\n"
                  << "or consider using the 'ignoreBoundaryFaces' option.\n";
        file << "\nERROR: DFN generation has finished but the formed\n"
             << "fracture network does not make a connection between\n"
             << "the user's specified boundary faces.\n";
        file << "Try increasing the fracture density, shrinking the domain\n"
             << "or consider using the 'ignoreBoundaryFaces' option.\n";
        file.close();
        exit(1);
    }
    
    //************ Intersection Stats ***************
    std::cout << "\nNumber of Triple Intersection Points (Before Isolated Fracture Removal): " << triplePoints.size() << "\n";
    file << "\nNumber of Triple Intersection Points (Before Isolated Fracture Removal): " << triplePoints.size() << "\n";
    // Shrink intersection stats
    std::cout << "\nIntersection Statistics:\n";
    std::cout << "    Number of Intersections: " << intPts.size() << " \n";
    std::cout << "    Intersections Shortened: " << pstats.intersectionsShortened << " \n";
    std::cout << "    Original Intersection (Before Intersection Shrinking) Length: " << pstats.originalLength << " m\n";
    std::cout << "    Intersection Length Discarded: " << pstats.discardedLength << " m\n";
    std::cout << "    Final Intersection Length: " << pstats.originalLength - pstats.discardedLength << " m\n";
    file << "\nIntersection Statistics:\n";
    file << "    Number of Intersections: " << intPts.size() << " \n";
    file << "    Intersections Shortened: " << pstats.intersectionsShortened << " \n";
    file << "    Original Intersection (Before Intersection Shrinking) Length: " << pstats.originalLength << " m\n";
    file << "    Intersection Length Discarded: " << pstats.discardedLength << " m\n";
    file << "    Final Intersection Length: " << pstats.originalLength - pstats.discardedLength << " m\n";
    //*********** Rejection Stats *******************
    std::cout << "\nRejection Statistics: \n";
    std::cout << "    " << pstats.rejectionReasons.shortIntersection << " Short Intersections \n";
    std::cout << "    " << pstats.rejectionReasons.closeToNode << " Close to Node\n";
    std::cout << "    " << pstats.rejectionReasons.closeToEdge << " Close to Edge\n";
    std::cout << "    " << pstats.rejectionReasons.closePointToEdge << " Vertex Close to Edge\n";
    std::cout << "    " << pstats.rejectionReasons.outside << " Outside of Domain\n";
    std::cout << "    " << pstats.rejectionReasons.triple << " Triple intersection Rejections\n";
    std::cout << "    " << pstats.rejectionReasons.interCloseToInter << " Intersections Close to Other Intersections\n\n";
    file << "\nRejection Statistics: \n";
    file << "    " << pstats.rejectionReasons.shortIntersection << " Short Intersections \n";
    file << "    " << pstats.rejectionReasons.closeToNode << " Close to Node\n";
    file << "    " << pstats.rejectionReasons.closeToEdge << " Close to Edge\n";
    file << "    " << pstats.rejectionReasons.closePointToEdge << " Vertice Close to Edge\n";
    file << "    " << pstats.rejectionReasons.outside << " Outside of Domain\n";
    file << "    " << pstats.rejectionReasons.triple << " Triple intersection Rejections\n";
    file << "    " << pstats.rejectionReasons.interCloseToInter << " Intersections Close to Other Intersections\n\n";
    std::cout << "\n________________________________________________________\n\n";
    file << "\n________________________________________________________\n\n";
    
    if (totalFamilies > 0) {
        std::cout << "Fracture Estimation statistics:\n";
        file << "Fracture Estimation statistics:\n";
        std::cout << "NOTE: If estimation and actual are very different, \nexpected family distributions might "
                  << "not be accurate. \nIf this is the case, try increasing or decreasing \nthe 'radiiListIncrease' option "
                  << "in the input file.\n\n";
        file << "NOTE: If estimation and actual are very different, \nexpected family distributions might "
             << "not be accurate. \nIf this is the case, try increasing or decreasing \nthe 'radiiListIncrease' option "
             << "in the input file.\n\n";
             
        // Compare expected radii/poly size and actual
        for (int i = 0; i < totalFamilies; i++) {
            if (shapeFamilies[i].distributionType == 4) { // Constant
                std::cout << shapeType(shapeFamilies[i]) << " Family "
                          << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << "\n"
                          << "Using constant size\n\n";
                file << shapeType(shapeFamilies[i]) << " Family "
                     << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << "\n"
                     << "Using constant size\n\n";
            } else {
                std::cout << shapeType(shapeFamilies[i]) << " Family "
                          << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << "\n"
                          << "Estimated: " << pstats.expectedFromFam[i] << "\n";
                std::cout << "Actual:    " << pstats.acceptedFromFam[i] + pstats.rejectedFromFam[i] << "\n\n";
                file << shapeType(shapeFamilies[i]) << " Family "
                     << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << "\n"
                     << "Estimated: " << pstats.expectedFromFam[i] << "\n";
                file << "Actual:    " << pstats.acceptedFromFam[i] + pstats.rejectedFromFam[i] << "\n\n";
            }
        }
        
        std::cout << "\n________________________________________________________\n\n";
        file << "\n________________________________________________________\n\n";
    }
    
    std::cout << "Seed: " << seed << "\n";
    file << "Seed: " << seed << "\n";
    // Write all output files
    writeOutput(argv[2], acceptedPoly, intPts, triplePoints, pstats, finalFractures, shapeFamilies);
    // Duplicate node counters are set in writeOutput(). Write output must happen before
    // duplicate node prints
    // Print number of duplicate nodes (pstats.intersectionsNodeCount is set in writeOutpu() )
    std::cout << "\nLagrit Should Remove "
              << pstats.intersectionNodeCount / 2 - pstats.tripleNodeCount
              << " Nodes (" << pstats.intersectionNodeCount << "/2 - "
              << pstats.tripleNodeCount << ")\n";
    file << "\nLagrit Should Remove "
         << pstats.intersectionNodeCount / 2 - pstats.tripleNodeCount
         << " Nodes (" << pstats.intersectionNodeCount << "/2 - "
         << pstats.tripleNodeCount << ")\n";
    file.close();
    return 0;
}

/******************************** END MAIN ***********************************/
/*****************************************************************************/


