#include "splaytree.hpp"
#include <iostream>
using namespace std;

int main()
{

        node* root = NULL;

                root = insert(root, 150);
                root = insert(root, 25);
                root = insert(root, 75);
                root = insert(root, 175);
                root = insert(root, 225);


                        printsplaytree(root);



        return 0;
}
