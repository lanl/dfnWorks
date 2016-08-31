#include "linkedList.h"
#include <iostream>

LinkedList::LinkedList() {
    head = nullptr;
    tail = nullptr;
}

LinkedList::~LinkedList() {
    Node *current = head;
    while (current != nullptr) {
        Node *next = current->next;
        delete current;
        current = next;
    }
}



void LinkedList::append(Node* node) {
    if (head == nullptr) {
        head = node;
        tail = node;
    }    
    else {
        tail->next = node;
        tail = node;
    }
}

Node* LinkedList::find(int id) {
    Node* curNode = head;
    while (curNode != nullptr) {
        if (curNode->id == id) {
            break;
        }
        curNode = curNode->next;
    }
    return curNode;
}
