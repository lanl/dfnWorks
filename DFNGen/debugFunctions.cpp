#include <iostream>
#include <vector>
#include "debugFunctions.h"
#include "input.h"
#include "insertShape.h"
#include "logFile.h"

using std::string;

/*! Print all polygon Poly variables to screen.
    Arg 1: std vector array of Poly */
void printAllPolys(std::vector<Poly> &acceptedPoly) {
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        std::string logString = "Poly " + to_string(i) + "\n";
        logger.writeLogFile(INFO,  logString);
        printPolyData(acceptedPoly[i]);
    }
}

/*! Print all triple intersection points to screen.
    Arg 1: std vector array of Point, triple intersection points */
void printAllTriplePts(std::vector<Point> &triplePoints) {
    std::string logString = "Triple Points:\n";
    logger.writeLogFile(INFO,  logString);
    
    for (unsigned int i = 0; i < triplePoints.size(); i++) {
        logString = "{" + to_string(triplePoints[i].x) + "," + to_string(triplePoints[i].y) + "," + to_string(triplePoints[i].z) + "}\n";
        logger.writeLogFile(INFO,  logString);
    }
    
    logString = "\n";
    logger.writeLogFile(INFO,  logString);
}


/*! Print all intersection structure IntPoint data.
    Arg 1: std vector array of IntPoint */
void printIntersectionData(std::vector<IntPoints> &intPts) {
    std::string logString = "Intersections:\n";
    logger.writeLogFile(INFO,  logString);
    
    for (unsigned int i = 0; i < intPts.size(); i++) {
        logString = "Fractures: " + to_string(intPts[i].fract1 + 1) + ", " + to_string(intPts[i].fract2 + 1)+ "\n";
        logger.writeLogFile(INFO,  logString);
        logString = "Line: {" + to_string(intPts[i].x1) + "," + to_string(intPts[i].y1) + "," + to_string(intPts[i].z1) + "} {" + to_string(intPts[i].x2) + "," + to_string(intPts[i].y2) + "," + to_string(intPts[i].z2) + "}\n";
        logger.writeLogFile(INFO,  logString);
        logString = "Trip pts size = " + to_string(intPts[i].triplePointsIdx.size())+ "\n";
        logger.writeLogFile(INFO,  logString);
        logString = "Triple Pts Index: ";
        logger.writeLogFile(INFO,  logString);
        
        for (unsigned int k = 0; k < intPts[i].triplePointsIdx.size(); k++) {
            logString = to_string(intPts[i].triplePointsIdx[k]) + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        // logString = "\n\n";
        // logger.writeLogFile(INFO,  logString);
    }
}


/*! Print all fracture cluster data to screen.
    Arg 1: Stats statistics structure
    Arg 2: std vector array of Poly, all accepted fractures */
void printGroupData(Stats &pstats, std::vector<Poly> &fractList) {
    std::string logString;
    
    //group number debug
    for (unsigned int i = 0; i < pstats.fractGroup.size(); i++) {
        logString = "fracture group[" + to_string(i) + "]:\n";
        logger.writeLogFile(INFO,  logString);
        logString = "Group number = " + to_string(pstats.fractGroup[i].groupNum)+ "\n";
        logger.writeLogFile(INFO,  logString);
        logString = "List of Polys:\n";
        logger.writeLogFile(INFO,  logString);
        
        for(unsigned int k = 0; k < pstats.fractGroup[i].polyList.size(); k++) {
            logString = to_string(pstats.fractGroup[i].polyList[k])+ "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        logString = "intersections on polygon:\n";
        logger.writeLogFile(INFO,  logString);
        
        for (unsigned int k = 0; k < pstats.fractGroup[i].polyList.size(); k++) {
            logString = to_string(fractList[pstats.fractGroup[i].polyList[k]].intersectionIndex.size()) + ", " + "\n";
            logger.writeLogFile(INFO,  logString);
        }
    }
    
    for (unsigned int i = 0; i < pstats.groupData.size(); i++) {
        logString = "groupData[" + to_string(i) + "]: {" + to_string(pstats.groupData[i].faces[0]) + "," + to_string(pstats.groupData[i].faces[1]) + "," + to_string(pstats.groupData[i].faces[2]) + "," + to_string(pstats.groupData[i].faces[3]) + "," + to_string(pstats.groupData[i].faces[4]) + "," + to_string(pstats.groupData[i].faces[5]) + "}\n";
        logger.writeLogFile(INFO,  logString);
        logString = "size: " + to_string(pstats.groupData[i].size) + "\n";
        logger.writeLogFile(INFO,  logString);
        logString = "valid: " + to_string(pstats.groupData[i].valid) + "\n";
        logger.writeLogFile(INFO,  logString);
    }
    
    logString = "\n";
    logger.writeLogFile(INFO,  logString);
}

/*! Print Poly variables to screen.
    Arg 1: Poly structure to print to screen */
void printPolyData(struct Poly &poly) {
    std::string logString;
    logString = "numberOfNodes = " + to_string(poly.numberOfNodes)  ;
    logger.writeLogFile(INFO,  logString);
    logString = "intersectionCount = " + to_string(poly.intersectionIndex.size())  ;
    logger.writeLogFile(INFO,  logString);
    logString = "Truncated = " + to_string(poly.truncated) + "\n";
    logger.writeLogFile(INFO,  logString);
    logString = "groupNum = " + to_string(poly.groupNum)  ;
    logger.writeLogFile(INFO,  logString);
    logString = "familyNum = " + to_string(poly.familyNum)  ;
    logger.writeLogFile(INFO,  logString);
    logString = "Faces = {" + to_string(poly.faces[0]) + "," + to_string(poly.faces[1]) + "," + to_string(poly.faces[2] ) + "," + to_string(poly.faces[3]) + "," + to_string(poly.faces[4]) + "," + to_string(poly.faces[5]) + "}\n";
    logger.writeLogFile(INFO,  logString);
    logString = "area = " + to_string(poly.area)  ;
    logger.writeLogFile(INFO,  logString);
    // logString = "aperture = " + poly.aperture  ;
    logString = "xradius = " + to_string(poly.xradius)  ;
    logger.writeLogFile(INFO,  logString);
    logString = "yradius = " + to_string(poly.yradius)  ;
    logger.writeLogFile(INFO,  logString);
    logString = "aspectRatio = " + to_string(poly.aspectRatio)  ;
    logger.writeLogFile(INFO,  logString);
    logString = "normal = {" + to_string(poly.normal[0]) + "," + to_string(poly.normal[1]) + "," + to_string(poly.normal[2]) + "}\n";
    logger.writeLogFile(INFO,  logString);
    logString = "translation = {" + to_string(poly.translation[0]) + "," + to_string(poly.translation[1]) + "," + to_string(poly.translation[2]) + "}\n";
    logger.writeLogFile(INFO,  logString);
    // logString = "permeability = " + poly.permeability + "\n";
    // logger.writeLogFile(INFO,  logString);
    logString = "boundingBox:\nxMin = " + to_string(poly.boundingBox[0]) + " xMax = " + to_string(poly.boundingBox[1]) + "\n";
    logger.writeLogFile(INFO,  logString);
    logString = "yMin = " + to_string(poly.boundingBox[2]) + " yMax = " + to_string(poly.boundingBox[3])  ;
    logger.writeLogFile(INFO,  logString);
    logString = "zMin = " + to_string(poly.boundingBox[4]) + " zMax = " + to_string(poly.boundingBox[5])  ;
    logger.writeLogFile(INFO,  logString);
    logString = "IntPts indices: ";
    logger.writeLogFile(INFO,  logString);
    
    for (unsigned int i = 0; i < poly.intersectionIndex.size(); i++) {
        logString = to_string(poly.intersectionIndex[i]) + ", ";
        logger.writeLogFile(INFO,  logString);
    }
    
    logString = "\n";
    logger.writeLogFile(INFO,  logString);
    logString = "Vertices:\n";
    logger.writeLogFile(INFO,  logString);
    
    for (int i = 0; i < poly.numberOfNodes; i++) {
        int idx = i * 3;
        logString = "{" + to_string(poly.vertices[idx]) + "," + to_string(poly.vertices[idx + 1]) + "," + to_string(poly.vertices[idx + 2]) + "}\n";
        logger.writeLogFile(INFO,  logString);
    }
}


/*****************************************************************************/
/*! Print all fracture Shape families and  variables to screen.
    Arg 1: std vector array of Shape  */
void printShapeFams(std::vector<Shape> &shapeFamilies) {
    using namespace std;
    double radToDeg = 180 / M_PI;
    std::string logString = "Shape Families:\n";
    logger.writeLogFile(INFO,  logString);
    
    for(unsigned int i = 0; i < shapeFamilies.size(); i++) {
        //name(rect or ell) and number of family
        logString = shapeType(shapeFamilies[i]) + " Family " + to_string(getFamilyNumber(i, shapeFamilies[i].shapeFamily)) + ":\n";
        logger.writeLogFile(INFO,  logString);
        
        // Print vertice number
        if (shapeFamilies[i].shapeFamily == 0) {  // If ellipse family
            logString = "Number of Vertices: " + to_string(shapeFamilies[i].numPoints)  + "\n";
            logger.writeLogFile(INFO,  logString);
        } else {
            logString = "Number of Vertices: 4\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        // aspect ratio
        logString = "Aspect Ratio: " + to_string(shapeFamilies[i].aspectRatio )  + "\n";
        logger.writeLogFile(INFO,  logString);
        
        // p32 target
        if (stopCondition == 1) {
            logString = "P32 (Fracture Intensity) Target: " + to_string(shapeFamilies[i].p32Target)   + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        // beta distribution, rotation around normal vector
        if (shapeFamilies[i].betaDistribution == 0) {
            logString = "Beta Distribution (Rotation Around Normal Vector): [0, 2PI)\n";
            logger.writeLogFile(INFO,  logString);
        } else {
            logString = "Beta (Rotation Around Normal Vector): " + to_string(shapeFamilies[i].beta) + " rad, " + to_string(shapeFamilies[i].beta * radToDeg ) + " deg"   + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        if (orientationOption == 0) {
            logString = "Theta: " + to_string(shapeFamilies[i].angleOne) + " rad, " + to_string(shapeFamilies[i].angleOne * radToDeg) + " deg"   + "\n";
            logger.writeLogFile(INFO,  logString);
            // Phi (angle the projection of normal onto x-y plane  makes with +x axis
            logString = "Phi: " + to_string(shapeFamilies[i].angleTwo) + " rad, " + to_string(shapeFamilies[i].angleTwo * radToDeg) + " deg "   + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        // Theta (angle normal makes with z axis
        else if (orientationOption == 1) {
            logString = "Trend: " + to_string(shapeFamilies[i].angleOne) + " rad, " + to_string(shapeFamilies[i].angleOne * radToDeg) + " deg"   + "\n";
            logger.writeLogFile(INFO,  logString);
            // Phi (angle the projection of normal onto x-y plane  makes with +x axis
            logString = "Plunge: " + to_string(shapeFamilies[i].angleTwo) + " rad, " + to_string(shapeFamilies[i].angleTwo * radToDeg) + " deg "   + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        // kappa
        logString = "Kappa: " + to_string(shapeFamilies[i].kappa )  + "\n";
        logger.writeLogFile(INFO,  logString);
        
        // Print layer family belongs to
        if (shapeFamilies[i].layer == 0) {
            logString = "Layer: Entire domain\n";
            logger.writeLogFile(INFO,  logString);
        } else {
            int idx = (shapeFamilies[i].layer - 1) * 2;
            logString = "Layer: " + to_string(shapeFamilies[i].layer) + " {" + to_string(layers[idx]) + ", " + to_string(layers[idx + 1]) + "}"   + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        // Print layer family belongs to
        if (shapeFamilies[i].region == 0) {
            logString = "Region: Entire domain\n";
            logger.writeLogFile(INFO,  logString);
        } else {
            int idx = (shapeFamilies[i].region - 1) * 6;
            logString = "Region Number " + to_string(shapeFamilies[i].region) + ": {-x,+x,-y,+y,-z,+z}: {" + to_string(regions[idx]) + "," + to_string(regions[idx + 1]) + "," + to_string(regions[idx + 2])  + "," + to_string(regions[idx + 3]) + "," + to_string(regions[idx + 4]) + "," + to_string(regions[idx + 5]) + "}\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        if (shapeFamilies[i].layer  > 0 && shapeFamilies[i].region > 0) {
            logString = "ERROR Layer and Region both defined for this Family.\nExiting Program\n"  ;
            logger.writeLogFile(INFO,  logString);
            exit(1);
        }
        
        // Print distribution data
        switch (shapeFamilies[i].distributionType) {
        case 1: // lognormal
            logString = "Distrubution: Lognormal\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Mean: " + to_string(shapeFamilies[i].mean)   + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Standard Deviation: " + to_string(shapeFamilies[i].sd) + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Minimum Radius: " + to_string(shapeFamilies[i].logMin) + "m"   + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Maximum Radius: " + to_string(shapeFamilies[i].logMax ) + "m"   + "\n";
            logger.writeLogFile(INFO,  logString);
            break;
            
        case 2: // power-law
            logString = "Distribution: Truncated Power-Law\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Alpha: " + to_string(shapeFamilies[i].alpha)  + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Minimum Radius: " + to_string(shapeFamilies[i].min) + "m"  + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Maximum Radius: " + to_string(shapeFamilies[i].max) + "m"  + "\n";
            logger.writeLogFile(INFO,  logString);
            break;
            
        case 3: // exponential
            logString = "Distribution: Exponential\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Mean: " + to_string(shapeFamilies[i].expMean)   + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Lambda: " + to_string(shapeFamilies[i].expLambda )  + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Minimum Radius: " + to_string(shapeFamilies[i].expMin ) + "m"   + "\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Maximum Radius: " + to_string(shapeFamilies[i].expMax ) + "m"   + "\n";
            logger.writeLogFile(INFO,  logString);
            break;
            
        case 4: // constant
            logString = "Distribution: Constant\n";
            logger.writeLogFile(INFO,  logString);
            logString = "Radius: " +  to_string(shapeFamilies[i].constRadi) + "m"   + "\n";
            logger.writeLogFile(INFO,  logString);
        }
        
        logString = "Family Insertion Probability: " + to_string(famProb[i]) + "\n";
        logger.writeLogFile(INFO,  logString);
    }
}


