//
//  main.cpp
//  jacobi
//
//  Created by 杨璞 on 15/8/23.
//  Copyright (c) 2015年 yangpu. All rights reserved.
//

#include <iostream>
#include "jacobi.h"
using namespace std;

int main(int argc, const char * argv[]) {
    double a[3][3] = {1.11,-0.55,0,-0.55,2.44,-0.66,0,0,1};
    double b[3] = {-93.33,213.34,-25};
    double x0[3] = {1,1,1};
    double * x;
 
    jacobi jac(3,(double* )a,b,x0);
    x = jac.do_jacobi();
    for(int ii =0;ii<3;ii++)
    {
        cout<<x[ii]<<endl;
    }
  
   
        return 0;
}
