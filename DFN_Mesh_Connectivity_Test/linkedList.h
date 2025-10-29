#ifndef _LINKEDLIST_H_
#define _LINKEDLIST_H_

#include "node.h"

class LinkedList {

  private:
    Node* head;
    Node* tail;
    
  public:
    LinkedList();
    ~LinkedList();
    void append(Node* node);
    Node* find(int id);
    void printList();
};

#endif

