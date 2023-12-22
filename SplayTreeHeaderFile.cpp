
#ifndef SPLAYTREE_H
#define SPLAYTREE_H
#include <iostream>

using namespace std;


struct node{

        int key;
        node *left, *right;

};

//This function creates the temp nodes and variables needed to create and traverse the nodes in our Splay tree>

node* newnode(int key)
{

        node* temp = new node;

                temp->key = key;
                temp->left = nullptr;
                temp->right = nullptr;

                return temp;

}

//This function allows us to rotate certain nodes to the left like in an AVL tree.
node* zigrotate(node* x)
{

        node* y = x->left;

                x->left = y->right;
                y->right = x;

                return y;

} node* zagrotate(node* x)
{

        node* y = x->right;

                x->right = y->left;
                y->left = x;

                return y;

}node* splaying(node* root, int key)
{

        if(root == nullptr || root->key == key)

                return root;

        if(root->key > key){

                if(root->left == nullptr)

                        return root;

                if(root->left->key > key){

                        root->left->left = splaying(root->left->left, key);
                        root = zigrotate(root);

                }

                else if(root->left->key < key){

                        root->left->right = splaying(root->left->right, key);

                        if(root->left->right != nullptr)
                                root->left = zagrotate(root->left);
                        }

                        return(root->left = NULL);

        }

        else{

                if(root->right == nullptr)

                        return root;

                if(root->right->key > key) {

                        root->right->left = splaying(root->right->left, key);


                        if(root->right->left != nullptr)                 root->right = zigrotate(root->right);

                }

                        else if(root->right->key < key){

                                root->right->right = splaying(root->right->right, key);

                                root = zagrotate(root);
                }

                return (root->right = NULL);


        }

}node* insert(node* root, int key)
{

        if(root == NULL)

                return newnode(key);

                root = splaying(root, key);

        if(root->key == key);

                return root;

                node* temp = newnode(key);

        if(root->key > key) {

                temp->right = root;
                temp->left = root->left;
                root->left = NULL;


        }

        else {

                temp->left = root;
                temp->right = root->right;
                root->right = NULL;


        }

        return temp;


void printsplaytree(node* root){

        if(root != nullptr){

                printsplaytree(root->left);

                cout << root->key << " " ;

                printsplaytree(root->right);


        }



#endif