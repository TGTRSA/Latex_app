#include <iostream>
#include <string.h> 
#include <vector>  
#include <algorithm>
//typedef struct diff {
  //  std::string data;
//};

struct cache {
    std::string data;       
};

struct similarities {
    char* data;
};

struct Edit{
    enum Type { INSERT , DELETE, KEEP };
    Type type;
    char ch;
    int pos;
};

int compare_lengths(int len1, int len2){
    if (len1 > len2){
        return len1;

