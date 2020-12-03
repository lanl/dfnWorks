#include <iostream>
#include <vector>
#include "debugFunctions.h"
#include "input.h"
#include "insertShape.h"

/*! Print all polygon Poly variables to screen.
    Arg 1: std vector array of Poly */
void printAllPolys(std::vector<Poly> &acceptedPoly) {
    for (unsigned int i = 0; i < acceptedPoly.size(); i++) {
        std::cout << "\nPoly " << i << "\n";
        printPolyData(acceptedPoly[i]);
    }
}

/*! Print all triple intersection points to screen.
    Arg 1: std vector array of Point, triple intersection points */
void printAllTriplePts(std::vector<Point> &triplePoints) {
    std::cout << "\nTriple Points:\n";
    
    for (unsigned int i = 0; i < triplePoints.size(); i++) {
        std::cout << "{" << triplePoints[i].x << "," << triplePoints[i].y << "," << triplePoints[i].z << "}\n";
    }
    
    std::cout << "\n";
}


/*! Print all intersection structure IntPoint data.
    Arg 1: std vector array of IntPoint */
void printIntersectionData(std::vector<IntPoints> &intPts) {
    std::cout << "\nIntersections:\n";
    
    for (unsigned int i = 0; i < intPts.size(); i++) {
        std::cout << "Fractures: " << intPts[i].fract1 + 1 << ", " << intPts[i].fract2 + 1 << "\n";
        std::cout << "Line: {" << intPts[i].x1 << "," << intPts[i].y1 << "," << intPts[i].z1
                  << "} {" << intPts[i].x2 << "," << intPts[i].y2 << "," << intPts[i].z2 << "}\n";
        std::cout << "Trip pts size = " << intPts[i].triplePointsIdx.size() << "\n";
        std::cout << "Triple Pts Index: ";
        
        for (unsigned int k = 0; k < intPts[i].triplePointsIdx.size(); k++) {
            std::cout << intPts[i].triplePointsIdx[k] << " ";
        }
        
        std::cout << "\n\n";
    }
}


/*! Print all fracture cluster data to screen.
    Arg 1: Stats statistics structure
    Arg 2: std vector array of Poly, all accepted fractures */
void printGroupData(Stats &pstats, std::vector<Poly> &fractList) {
    //group number debug
    for (unsigned int i = 0; i < pstats.fractGroup.size(); i++) {
        std::cout << "\nfracture group[" << i << "]:\n";
        std::cout << "Group number = " << pstats.fractGroup[i].groupNum << std::endl;
        std::cout << "List of Polys:\n";
        
        for(unsigned int k = 0; k < pstats.fractGroup[i].polyList.size(); k++) {
            std::cout << pstats.fractGroup[i].polyList[k] << " ";
        }
        
        std::cout << "\nintersections on poly:\n";
        
        for (unsigned int k = 0; k < pstats.fractGroup[i].polyList.size(); k++) {
            std::cout << fractList[pstats.fractGroup[i].polyList[k]].intersectionIndex.size() << ", ";
            std::cout << std::endl;
        }
    }
    
    for (unsigned int i = 0; i < pstats.groupData.size(); i++) {
        std::cout << "groupData[" << i << "]: {"
                  << pstats.groupData[i].faces[0] << "," << pstats.groupData[i].faces[1]
                  << "," << pstats.groupData[i].faces[2] << "," << pstats.groupData[i].faces[3]
                  << "," << pstats.groupData[i].faces[4] << "," << pstats.groupData[i].faces[5] << "}\n";
        std::cout << "size: " << pstats.groupData[i].size << "\n";
        std::cout << "valid: " << pstats.groupData[i].valid << "\n";
    }
    
    std::cout << "\n";
}

/*! Print Poly variables to screen.
    Arg 1: Poly structure to print to screen */
void printPolyData(struct Poly &poly) {
    std::cout << "numberOfNodes = " << poly.numberOfNodes << std::endl;
    std::cout << "intersectionCount = " << poly.intersectionIndex.size() << std::endl;
    std::cout << "Truncated = " << poly.truncated << "\n";
    std::cout << "groupNum = " << poly.groupNum << std::endl;
    std::cout << "familyNum = " << poly.familyNum << std::endl;
    std::cout << "Faces = {" << poly.faces[0] << "," << poly.faces[1] << ","
              << poly.faces[2] << "," << poly.faces[3] << ","
              << poly.faces[4] << "," << poly.faces[5] << "}\n";
    std::cout << "area = " << poly.area << std::endl;
    std::cout << "aperture = " << poly.aperture << std::endl;
    std::cout << "xradius = " << poly.xradius << std::endl;
    std::cout << "yradius = " << poly.yradius << std::endl;
    std::cout << "aspectRatio = " << poly.aspectRatio << std::endl;
    std::cout << "aperture = " << poly.aperture << std::endl;
    std::cout << "normal = {" << poly.normal[0] << "," << poly.normal[1] << "," << poly.normal[2] << "}\n";
    std::cout << "translation = {" << poly.translation[0] << "," << poly.translation[1] << "," << poly.translation[2] << "}\n";
    std::cout << "permeability = " << poly.permeability << "\n";
    std::cout << "boundingBox:\nxMin = " << poly.boundingBox[0] << " xMax = " << poly.boundingBox[1] << "\n";
    std::cout << "yMin = " << poly.boundingBox[2] << " yMax = " << poly.boundingBox[3] << std::endl;
    std::cout << "zMin = " << poly.boundingBox[4] << " zMax = " << poly.boundingBox[5] << std::endl;
    std::cout << "IntPts indices: ";
    
    for (unsigned int i = 0; i < poly.intersectionIndex.size(); i++) {
        std::cout << poly.intersectionIndex[i] << ", ";
    }
    
    std::cout << "\n";
    std::cout << "Vertices:\n";
    
    for (int i = 0; i < poly.numberOfNodes; i++) {
        int idx = i * 3;
        std::cout << "{" << poly.vertices[idx] << "," << poly.vertices[idx + 1] << "," << poly.vertices[idx + 2] << "}\n";
    }
}


/*****************************************************************************/
/*! Print all fracture Shape families and  variables to screen.
    Arg 1: std vector array of Shape  */
void printShapeFams(std::vector<Shape> &shapeFamilies) {
    using namespace std;
    double radToDeg = 180 / M_PI;
    cout << "\nShape Families:\n";
    
    for(unsigned int i = 0; i < shapeFamilies.size(); i++) {
        //name(rect or ell) and number of family
        cout << shapeType(shapeFamilies[i]) << " Family "
             << getFamilyNumber(i, shapeFamilies[i].shapeFamily) << ":\n";
             
        // Print vertice number
        if (shapeFamilies[i].shapeFamily == 0) {  // If ellipse family
            cout << "Number of Vertices: " << shapeFamilies[i].numPoints << endl;
        } else {
            cout << "Number of Vertices: 4" << endl;
        }
        
        // aspect ratio
        cout << "Aspect Ratio: " << shapeFamilies[i].aspectRatio << endl;
        
        // p32 target
        if (stopCondition == 1) {
            cout << "P32 (Fracture Intensity) Target: "
                 << shapeFamilies[i].p32Target << endl;
        }
        
        // beta distribution, rotation around normal vector
        if (shapeFamilies[i].betaDistribution == 0) {
            cout << "Beta Distribution (Rotation Around Normal Vector): [0, 2PI)" << endl;
        } else {
            cout << "Beta (Rotation Around Normal Vector): "
                 << shapeFamilies[i].beta << " rad, "
                 << shapeFamilies[i].beta * radToDeg << " deg" << endl;
        }
        
        // Theta (angle normal makes with z axis
        cout << "Theta: " << shapeFamilies[i].theta << " rad, "
             << shapeFamilies[i].theta * radToDeg << " deg" << endl;
        // Phi (angle the projection of normal onto x-y plane  makes with +x axis
        cout << "Phi: " << shapeFamilies[i].phi << " rad, "
             << shapeFamilies[i].phi * radToDeg << " deg " << endl;
        // kappa
        cout << "Kappa: " << shapeFamilies[i].kappa << endl;
        
        // Print layer family belongs to
        if (shapeFamilies[i].layer == 0) {
            cout << "Layer: Entire domain" << endl;
        } else {
            int idx = (shapeFamilies[i].layer - 1) * 2;
            cout << "Layer: " << shapeFamilies[i].layer << " {" << layers[idx]
                 << ", " << layers[idx + 1]
                 << "}" << endl;
        }
        
        // Print layer family belongs to
        if (shapeFamilies[i].region == 0) {
            cout << "Region: Entire domain" << endl;
        } else {
            int idx = (shapeFamilies[i].region - 1) * 6;
            cout << "Region Number " << shapeFamilies[i].region << ": {-x,+x,-y,+y,-z,+z}: {" << regions[idx] << "," << regions[idx + 1] << "," << regions[idx + 2]  << "," << regions[idx + 3] << "," << regions[idx + 4] << "," << regions[idx + 5] << "}\n";
        }
        
        if (shapeFamilies[i].layer  > 0 && shapeFamilies[i].region > 0) {
            cout << "ERROR Layer and Region both defined for this Family.\nExiting Program\n" << endl;
            exit(1);
        }
        
        // Print distribution data
        switch (shapeFamilies[i].distributionType) {
        case 1: // lognormal
            cout << "Distrubution: Lognormal\n";
            cout << "Mean: " << shapeFamilies[i].mean << endl;
            cout << "Standard Deviation: " << shapeFamilies[i].sd <<  endl;
            cout << "Minimum Radius: " << shapeFamilies[i].logMin << "m" << endl;
            cout << "Maximum Radius: " << shapeFamilies[i].logMax << "m" << endl;
            break;
            
        case 2: // power-law
            cout << "Distribution: Truncated Power-Law\n";
            cout << "Alpha: " << shapeFamilies[i].alpha << endl;
            cout << "Minimum Radius: " << shapeFamilies[i].min << "m" << endl;
            cout << "Maximum Radius: " << shapeFamilies[i].max << "m" << endl;
            break;
            
        case 3: // exponential
            cout << "Distribution: Exponential\n";
            cout << "Mean: " << shapeFamilies[i].expMean << endl;
            cout << "Lambda: " << shapeFamilies[i].expLambda << endl;
            cout << "Minimum Radius: " << shapeFamilies[i].expMin << "m" << endl;
            cout << "Maximum Radius: " << shapeFamilies[i].expMax << "m" << endl;
            break;
            
        case 4: // constant
            cout << "Distribution: Constant\n";
            cout << "Radius: " << shapeFamilies[i].constRadi << "m" << endl;
        }
        
        cout << "Family Insertion Probability: " << famProb[i] << "\n\n";
    }
}


