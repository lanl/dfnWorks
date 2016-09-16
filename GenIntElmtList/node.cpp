#include "node.h"
#include <iostream>

Node::Node(int ID, Tri* _tri) {
    id = ID;
    tri = _tri; //Tri Element which this belongs to 
    next = nullptr;
}

