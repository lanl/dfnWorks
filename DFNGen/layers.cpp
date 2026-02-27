#include <cmath>
#include <vector>
#include "layers.h"
#include "input.h"
#include "logFile.h"
#include "structures.h"
#include "vectorFunctions.h"

/******************************************************************************
 * \file layers.cpp
 * \brief Truncates fracture polygons to their assigned layer's Z boundaries.
 *
 * Implements the same Sutherland-Hodgman half-space clipping algorithm used
 * in domainTruncation() (domain.cpp), but clips only against the two
 * horizontal (Z-normal) planes that define a layer's upper and lower bounds.
 *
 * The domain's X and Y boundaries are still enforced by domainTruncation(),
 * so this function deliberately omits those planes.
 ******************************************************************************/

/******************************************************************************
 * \brief Clips a polygon against a single infinite plane using
 *        Sutherland-Hodgman half-space clipping.
 *
 * Vertices on the "inside" side of the plane (dot product <= 0 with the
 * outward normal) are kept. Edge-boundary intersections are computed and
 * inserted wherever an edge crosses the plane.
 *
 * This is a direct analogue of the per-face inner loop in domainTruncation().
 *
 * \param newPoly  Polygon whose vertices are clipped in place.
 * \param normal   Outward unit normal of the clipping plane {nx, ny, nz}.
 * \param point    A point lying on the clipping plane {px, py, pz}.
 * \return Number of vertices remaining after clipping. 0 means fully outside.
 ******************************************************************************/
static int clipAgainstPlane(Poly &newPoly, double normal[3], double point[3]) {
    int nVertices = newPoly.numberOfNodes;

    if (nVertices <= 0) {
        return 0;
    }

    std::vector<double> points;
    points.reserve(nVertices * 3 + 6); // Extra room for intersection vertices
    int nNodes = 0;

    int last = (nVertices - 1) * 3;
    double temp[3];
    temp[0] = newPoly.vertices[last]     - point[0];
    temp[1] = newPoly.vertices[last + 1] - point[1];
    temp[2] = newPoly.vertices[last + 2] - point[2];
    double prevdist = dotProduct(temp, normal);

    for (int i = 0; i < nVertices; i++) {
        int index = i * 3;
        temp[0] = newPoly.vertices[index]     - point[0];
        temp[1] = newPoly.vertices[index + 1] - point[1];
        temp[2] = newPoly.vertices[index + 2] - point[2];
        double currdist = dotProduct(temp, normal);

        if (currdist <= 0) {
            // Vertex is on the inside of (or on) the plane — keep it
            points.push_back(newPoly.vertices[index]);
            points.push_back(newPoly.vertices[index + 1]);
            points.push_back(newPoly.vertices[index + 2]);
            nNodes++;
        }

        if (currdist * prevdist < 0) {
            // Edge crosses the clipping plane — compute and insert intersection point
            nNodes++;
            double t = std::abs(prevdist) / (std::abs(currdist) + std::abs(prevdist));

            if (i == 0) {
                // Edge from last vertex to vertex 0
                temp[0] = newPoly.vertices[last]
                          + (newPoly.vertices[0] - newPoly.vertices[last]) * t;
                temp[1] = newPoly.vertices[last + 1]
                          + (newPoly.vertices[1] - newPoly.vertices[last + 1]) * t;
                temp[2] = newPoly.vertices[last + 2]
                          + (newPoly.vertices[2] - newPoly.vertices[last + 2]) * t;
            } else {
                // Edge from vertex (i-1) to vertex i
                temp[0] = newPoly.vertices[index - 3]
                          + (newPoly.vertices[index]     - newPoly.vertices[index - 3]) * t;
                temp[1] = newPoly.vertices[index - 2]
                          + (newPoly.vertices[index + 1] - newPoly.vertices[index - 2]) * t;
                temp[2] = newPoly.vertices[index - 1]
                          + (newPoly.vertices[index + 2] - newPoly.vertices[index - 1]) * t;
            }

            points.push_back(temp[0]);
            points.push_back(temp[1]);
            points.push_back(temp[2]);

            if (currdist < 0) {
                // Transition from outside to inside: swap the intersection point
                // and the just-saved inside vertex so winding order is preserved
                int lastIdx = (nNodes - 1) * 3;
                // The inside vertex was pushed immediately before the intersection point
                double savedX = points[lastIdx - 3];
                double savedY = points[lastIdx - 2];
                double savedZ = points[lastIdx - 1];
                points[lastIdx - 3] = temp[0];
                points[lastIdx - 2] = temp[1];
                points[lastIdx - 1] = temp[2];
                points[lastIdx]     = savedX;
                points[lastIdx + 1] = savedY;
                points[lastIdx + 2] = savedZ;
            }
        }

        prevdist = currdist;
    }

    // Write clipped vertices back into the polygon
    newPoly.numberOfNodes = nNodes;

    if (nNodes > 0) {
        delete[] newPoly.vertices;
        newPoly.vertices = new double[3 * nNodes];

        for (int k = 0; k < nNodes; k++) {
            int idxx = k * 3;
            newPoly.vertices[idxx]     = points[idxx];
            newPoly.vertices[idxx + 1] = points[idxx + 1];
            newPoly.vertices[idxx + 2] = points[idxx + 2];
        }
    }

    return nNodes;
}


/******************************************************************************
 * bool layerTruncation()
 * See layers.h for full documentation.
 ******************************************************************************/
bool layerTruncation(Poly &newPoly, int layerIndex) {

    // No-op: full domain or layer conforming disabled
    if (layerIndex == 0 || !layerConformingFractures || numOfLayers == 0) {
        return false;
    }

    // layers[] is stored as {+z1, -z1, +z2, -z2, ...}
    // layerIndex is 1-based, so layer i -> index (i-1)*2
    int idx   = (layerIndex - 1) * 2;
    double zTop    = static_cast<double>(layers[idx]);     // +Z boundary
    double zBottom = static_cast<double>(layers[idx + 1]); // -Z boundary

    // Ensure zTop >= zBottom regardless of input ordering
    if (zBottom > zTop) {
        double tmp = zTop;
        zTop    = zBottom;
        zBottom = tmp;
    }

    // Quick check: are all vertices already inside the layer?
    bool needsClipping = false;
    for (int k = 0; k < newPoly.numberOfNodes; k++) {
        double z = newPoly.vertices[k * 3 + 2];
        if (z > zTop || z < zBottom) {
            needsClipping = true;
            break;
        }
    }

    if (!needsClipping) {
        return false; // Accept unchanged
    }

    newPoly.truncated = 1;

    // --- Clip against +Z boundary (outward normal points +Z) ---
    // Plane: z = zTop, outward normal = {0, 0, 1}
    // Vertices with z > zTop are outside.
    {
        double normal[3] = {0.0, 0.0,  1.0};
        double point[3]  = {0.0, 0.0,  zTop};
        int remaining = clipAgainstPlane(newPoly, normal, point);

        if (remaining < 3) {
            return true; // Reject
        }
    }

    // --- Clip against -Z boundary (outward normal points -Z) ---
    // Plane: z = zBottom, outward normal = {0, 0, -1}
    // Vertices with z < zBottom are outside.
    {
        double normal[3] = {0.0, 0.0, -1.0};
        double point[3]  = {0.0, 0.0,  zBottom};
        int remaining = clipAgainstPlane(newPoly, normal, point);

        if (remaining < 3) {
            return true; // Reject
        }
    }

    // Remove degenerate vertices (pairs closer than 2*h) that clipping may have introduced.
    // Mirrors the cleanup pass in domainTruncation().
    int nNodes = newPoly.numberOfNodes;
    int i = 0;

    while (i < nNodes) {
        int idx3 = i * 3;
        int next = (i == nNodes - 1) ? 0 : (i + 1) * 3;

        double dx = newPoly.vertices[idx3]     - newPoly.vertices[next];
        double dy = newPoly.vertices[idx3 + 1] - newPoly.vertices[next + 1];
        double dz = newPoly.vertices[idx3 + 2] - newPoly.vertices[next + 2];

        if (magnitude(dx, dy, dz) < (2.0 * h)) {
            // Delete the vertex that is NOT on a layer boundary plane.
            // A vertex is considered on a boundary if its Z is within eps of zTop or zBottom.
            bool currentOnBoundary = (std::abs(newPoly.vertices[idx3 + 2] - zTop)    < eps ||
                                      std::abs(newPoly.vertices[idx3 + 2] - zBottom) < eps);

            if (!currentOnBoundary) {
                // Shift vertices left, removing vertex i
                for (int j = i; j < nNodes - 1; j++) {
                    int jj = j * 3;
                    newPoly.vertices[jj]     = newPoly.vertices[jj + 3];
                    newPoly.vertices[jj + 1] = newPoly.vertices[jj + 4];
                    newPoly.vertices[jj + 2] = newPoly.vertices[jj + 5];
                }
            } else {
                // Remove the next vertex instead
                int end = (nNodes - 1) * 3;
                for (int j = next; j < end; j += 3) {
                    newPoly.vertices[j]     = newPoly.vertices[j + 3];
                    newPoly.vertices[j + 1] = newPoly.vertices[j + 4];
                    newPoly.vertices[j + 2] = newPoly.vertices[j + 5];
                }
            }

            nNodes--;
        } else {
            i++;
        }
    }

    if (nNodes < 3) {
        return true; // Reject
    }

    newPoly.numberOfNodes = nNodes;

    std::string logString = "Layer truncation applied: layer " + to_string(layerIndex)
                            + " z=[" + to_string(zBottom) + ", " + to_string(zTop)
                            + "], vertices after clipping: " + to_string(nNodes) + "\n";
    logger.writeLogFile(DEBUG, logString);

    return false; // Accept
}
