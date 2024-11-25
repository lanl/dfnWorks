#include <iostream>
#include "structures.h"

// Constructor
/*! Initializes fract1 and fract2 to -1.
    Sets intersectionShortened to false;
*/
IntPoints::IntPoints() {
    fract1 = -1;
    fract2 = -1;
    intersectionShortened = false;
}

// Constructor
/*! Zeros id & User Frature Type */
RejectedUserFracture::RejectedUserFracture() {
    id = 0;
    userFractureType = 0;
}

// Constructor
/*! Zeros all rejection counters. */
RejectionReasons::RejectionReasons() {
    shortIntersection = 0;
    closeToNode = 0;
    closeToEdge = 0;
    closePointToEdge = 0;
    outside = 0;
    triple = 0;
    interCloseToInter = 0;
}

// Constructor
/*! Initializes many values to zero. (See implementation for details).*/
Poly::Poly() {
    groupNum = 0;
    area = 0;
    // aperture = 0;
    familyNum = 0;
    xradius = yradius = 0;
    faces[0] = 0;
    faces[1] = 0;
    faces[2] = 0;
    faces[3] = 0;
    faces[4] = 0;
    faces[5] = 0;
    // permeability = 0;
    XYPlane = 0;
    truncated = 0;
}

// Constructor
/*! Initializes x, y, and z to zero.*/
Point::Point() {
    x = 0;
    y = 0;
    z = 0;
}

// Constructor
/*! Initializes x, y, and z with arguments
    passed to the constructor. */
Point::Point(double _x, double _y, double _z) {
    x = _x;
    y = _y;
    z = _z;
}

// Constructor
/*! Initializes polyList vector to reserve enough memory
    for 100 floats.*/
FractureGroups::FractureGroups() {
    polyList.reserve(100);
}

// Constructor
/*! Initializes size to zero, valid to true,
    and zeros (set to false) the faces array. */
GroupData::GroupData() {
    size = 0;
    valid = 1;
    faces[0] = 0;
    faces[1] = 0;
    faces[2] = 0;
    faces[3] = 0;
    faces[4] = 0;
    faces[5] = 0;
}

// Constructor
/*! Initializes all counters to zero. Initializes
    nextGroupNum to 1. (See implementation for details)*/
Stats::Stats() {
    acceptedPolyCount = 0;
    rejectedPolyCount = 0;
    retranslatedPolyCount = 0;
    truncated = 0;
    intersectionsShortened = 0;
    nextGroupNum = 1;
    fractGroup.reserve(16);
    originalLength = 0;
    discardedLength = 0;
    intersectionNodeCount = 0;
    tripleNodeCount = 0;
    areaBeforeRemoval = 0;
    areaAfterRemoval = 0;
}

// Constructor
/*! Initializes p32Target, currentP32, and radiiIdx to zero.*/
Shape::Shape() {
    p32Target = 0;
    currentP32 = 0;
    radiiIdx = 0;
}


