#ifndef _NODE_H_
#define _NODE_H_
#include "tri.h"
class Node {

public: 
    Node* next;
    int id; // Vertice ID
    Tri * tri;
    Node(int ID, Tri* _tri);
};

#endif
