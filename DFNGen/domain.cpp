#include <cmath>
#include <vector>
#include "domain.h"
#include "input.h"
#include "structures.h"
#include "vectorFunctions.h"

/******************************************************************************/
/***********************  Domain Truncation  **********************************/
// NOTE: domainTruncation() may benefit from rewriting in a more 
//       efficient way which does not reallocate memory as often
// Truncates polygons along the defined domain ('domainSize' in input file)
// Arg 1: Polygon being truncated (if truncation is necessary)
// Arg 2: Point to domain size array, 3 doubles: {x, y, z}
// Return:  0 - If Poly is inside domain and was truncated to more than 2 vertices,
//              of poly truncation was not needed
//          1 - If rejected due to being outside the domain or was truncated to
//              less than 3 vertices
bool domainTruncation(Poly &newPoly, double *domainSize) {
        
    std::vector<double> points; 
    points.reserve(18); // Initialize with enough room for 6 vertices
    int nNodes;    
    
    double domainX = domainSize[0]*.5; 
    double domainY = domainSize[1]*.5; 
    double domainZ = domainSize[2]*.5;
    
    int stop = newPoly.numberOfNodes;
    
    // Check if truncation is necessay:
    for (int k = 0; k < stop; k++) {
        int idx = k*3;
        if (newPoly.vertices[idx]   > domainX || newPoly.vertices[idx]   < -domainX) break;
        if (newPoly.vertices[idx+1] > domainY || newPoly.vertices[idx+1] < -domainY) break;
        if (newPoly.vertices[idx+2] > domainZ || newPoly.vertices[idx+2] < -domainZ) break;
            
        // If finished checking last node and code still hasn't broke 
        // from the for loop, then all nodes are inside domain
        if (k + 1 == stop) {
            return 0;
        }    
    }
    
    // If code does not return above, truncation is needed/
    newPoly.truncated = 1; // Mark poly as truncated    
    
    int nVertices;   // Same as newPoly.numberOfNodes;
    double ntmp[3];  // Normal of domain side
    double pttmp[3]; // Center point on domain side

    // Check against the all the walls of the domain
    for ( int j = 0; j < 6; j++) {        
        
        switch(j) {
            case 0: 
                ntmp[0]  = 0;  ntmp[1] = 0;  ntmp[2] = 1;
                pttmp[0] = 0; pttmp[1] = 0; pttmp[2] = domainZ;
                break;
            case 1:
                ntmp[0]  = 0;  ntmp[1] = 0;  ntmp[2] = -1;
                pttmp[0] = 0; pttmp[1] = 0; pttmp[2] = -domainZ;
                break;
            case 2:
                ntmp[0]  = 0;  ntmp[1] = 1;        ntmp[2] = 0;
                pttmp[0] = 0; pttmp[1] = domainY; pttmp[2] = 0;            
                break;
            case 3:
                ntmp[0]  = 0;  ntmp[1] = -1;        ntmp[2] = 0;
                pttmp[0] = 0; pttmp[1] = -domainY; pttmp[2] = 0;
                break;
            case 4:
                ntmp[0]  = 1;        ntmp[1] = 0;  ntmp[2] = 0;
                pttmp[0] = domainX; pttmp[1] = 0; pttmp[2] = 0;
                break;
            case 5:
                ntmp[0]  = -1;        ntmp[1] = 0;  ntmp[2] = 0;
                pttmp[0] = -domainX; pttmp[1] = 0; pttmp[2] = 0;
                break;
        }
        
        nVertices = newPoly.numberOfNodes;
        if(nVertices <= 0) {
            return 1; // Reject
        }
    
        nNodes = 0;     // Counter for final number of nodes
        points.clear(); // Clear any points from last iteration

        
        int last = (nVertices-1)*3; // Index to last node starting position in array
        double temp[3];
        temp[0] = newPoly.vertices[last]   - pttmp[0]; //x
        temp[1] = newPoly.vertices[last+1] - pttmp[1]; //y    
        temp[2] = newPoly.vertices[last+2] - pttmp[2]; //z
    
        // Previous distance - the dot product of the domain side normal
        // and the distance between vertex number nVertices and the temp point on the
        // domain side.                         
        double prevdist = dotProduct(temp, ntmp);

        for (int i = 0; i < nVertices; i++) {
        int index = i*3; 
        temp[0] = newPoly.vertices[index]   - pttmp[0];
        temp[1] = newPoly.vertices[index+1] - pttmp[1];
        temp[2] = newPoly.vertices[index+2] - pttmp[2]; 
        
        // Current distance, the dot product of domain side normal and 
        // the distance between the ii'th vertex and the temporary point
        double currdist = dotProduct(temp, ntmp);

        if (currdist <= 0) { // if vertex is towards the domain relative to the domain side
            // Save vertex
            points.push_back(newPoly.vertices[index]);   // x
            points.push_back(newPoly.vertices[index+1]); // y
            points.push_back(newPoly.vertices[index+2]); // z
            nNodes++;
        }

        if (currdist * prevdist < 0) { //if crosses boundary

            nNodes++;
            
            if (i == 0) { // Store point on boundary
                // 'last' is index to last vertice
                temp[0] = newPoly.vertices[last]  
                        + (newPoly.vertices[0] - newPoly.vertices[last])  
                        * std::abs(prevdist)/(std::abs(currdist)+std::abs(prevdist));
                temp[1] = newPoly.vertices[last+1] 
                        + (newPoly.vertices[1] - newPoly.vertices[last+1])
                        * std::abs(prevdist)/(std::abs(currdist)+std::abs(prevdist));
                temp[2] = newPoly.vertices[last+2] 
                        + (newPoly.vertices[2] - newPoly.vertices[last+2])
                        * std::abs(prevdist)/(std::abs(currdist)+std::abs(prevdist));
                points.push_back(temp[0]);
                points.push_back(temp[1]);
                points.push_back(temp[2]);
            }
            else { 
            
                // If from outside to inside    
                temp[0] = newPoly.vertices[index-3] 
                        + (newPoly.vertices[index] - newPoly.vertices[index-3]) 
                        * std::abs(prevdist) / (std::abs(currdist)+std::abs(prevdist));
                temp[1] = newPoly.vertices[index-2] 
                        + (newPoly.vertices[index+1] - newPoly.vertices[index-2]) 
                        * std::abs(prevdist) / (std::abs(currdist)+std::abs(prevdist));
                temp[2] = newPoly.vertices[index-1] 
                        + (newPoly.vertices[index+2] - newPoly.vertices[index-1]) 
                        * std::abs(prevdist) / (std::abs(currdist)+std::abs(prevdist));
                points.reserve(points.size()+3); // Resize vector if needed

                points.push_back(temp[0]);
                points.push_back(temp[1]);
                points.push_back(temp[2]);
            }
            if (currdist < 0) { // If from outside to inside - swap order
    
                int tmpIndex = (nNodes-1)*3; // Index to last saved point
                points[tmpIndex] = points[tmpIndex - 3];                
                points[tmpIndex+1] = points[tmpIndex - 2];    
                points[tmpIndex+2] = points[tmpIndex - 1];
                points[tmpIndex-3] = temp[0]; 
                points[tmpIndex-2] = temp[1];
                points[tmpIndex-1] = temp[2];        
            }
        }
        
        prevdist = currdist;
        
        } // End vertice loops
    
        newPoly.numberOfNodes = nNodes;

        if (nNodes > 0) {
    
            delete[] newPoly.vertices;

            newPoly.vertices = new double[3*nNodes];
        
            // Copy new nodes back to newPoly 
            for (int k = 0; k < nNodes; k++) {
                int idxx = k*3;
                newPoly.vertices[idxx]   = points[idxx];
                newPoly.vertices[idxx+1] = points[idxx+1];
                newPoly.vertices[idxx+2] = points[idxx+2];
            }
        }
    } // End main loop
    
    int i = 0;

    while (i < nNodes) {
        int next;
        double temp[3];
        int idx = i*3;
    
        if(i == nNodes-1){ // If last node
            next = 0;
        }
        else {
            next = (i+1)*3;
        }
        
        temp[0] = newPoly.vertices[idx]   - newPoly.vertices[next];
        temp[1] = newPoly.vertices[idx+1] - newPoly.vertices[next+1];
        temp[2] = newPoly.vertices[idx+2] - newPoly.vertices[next+2];
        
        if (magnitude(temp[0], temp[1], temp[2]) < (2*h)) { // If distance between current and next vertex < h
            // If point is NOT on a boundary, delete current indexed point, ELSE delete next point
            if ( std::abs(std::abs(newPoly.vertices[idx])-domainX) > eps &&  std::abs(std::abs(newPoly.vertices[idx+1])-domainY) > eps && std::abs(std::abs(newPoly.vertices[idx+2])-domainZ) > eps ) {                
                
                // Loop deletes a vertice by shifting elements to the right of the element, to the left 
                for (int j = i; j < nNodes-1 ; j++) {
                    int idx = j*3;
                    newPoly.vertices[idx] = newPoly.vertices[idx+3]; // Shift x coordinate left
                    newPoly.vertices[idx+1] = newPoly.vertices[idx+4]; // Shift y coordinate left
                    newPoly.vertices[idx+2] = newPoly.vertices[idx+5]; // Shift z coordinate left
                }
            }    
            else {
                // Loop deletes a vertice by shifting elements to the right of the element to the left 
                int end = (nNodes-1)*3;
                for (int j = next; j < end; j += 3){
                    newPoly.vertices[j] = newPoly.vertices[j+3]; // Shift x coordinate left
                    newPoly.vertices[j+1] = newPoly.vertices[j+4]; // Shift y coordinate left
                    newPoly.vertices[j+2] = newPoly.vertices[j+5]; // Shift z coordinate left
                }
            }
            nNodes--; // Update node counter
        }
        else {
            i++;
        }
    } // End while loop
    
   
    if(nNodes < 3) {
        return 1; // Reject
    }
    
    newPoly.numberOfNodes = nNodes;
    
    int temp = newPoly.numberOfNodes;
    for (int k = 0; k < temp; k++){
        // Check boundary faces
        // Update which boundaries newPoly touches        

        int idx = k*3;
        if (newPoly.vertices[idx] >= domainX-eps) {
            newPoly.faces[0] = 1;
        }
        else if (newPoly.vertices[idx] <= -domainX+eps) {
            newPoly.faces[1] = 1;
        }

        if (newPoly.vertices[idx+1] >= domainY-eps) {
            newPoly.faces[2] = 1;
        }
        else if (newPoly.vertices[idx+1] <= -domainY+eps) {
            newPoly.faces[3] = 1;
        }

        if (newPoly.vertices[idx+2] >= domainZ-eps) {
            newPoly.faces[4] = 1;
        }
        else if (newPoly.vertices[idx+2] <= -domainZ+eps) {
            newPoly.faces[5] = 1;
        }
    }
    return 0;
}
    

/******************************************************************/
/*****************  Debug Print Function  *************************/
// Prints a vector<Point> array to screen
// Arg 1: Vector<Point> array
void printPoints(std::vector<double> &point){

    for (unsigned int i = 0; i < point.size(); i++) {
        if (i != 0 && i % 3 == 0){
            std::cout<<"\n";
        }
        std::cout<<point[i]<<" ";
    }
    std::cout<<std::endl;
}


