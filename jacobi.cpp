//
//  jacobi.cpp
//  jacobi
//
//  Created by 杨璞 on 15/8/23.
//  Copyright (c) 2015年 yangpu. All rights reserved.
//

#include <iostream>
#include "jacobi.h"
using namespace std;
#include <math.h>

double * jacobi::do_jacobi()
{
    int k = 0;
    double sum = 0;
    double * X_k_1 = new double[N];
    double * X_k = new double[N];
    double * diff = new double[N];
    X_k_1 = X0;
    while (k<=M) {
        k++;
        for(int ii = 0;ii<N;ii++)
        {
            sum = 0;
            for(int jj =0;jj<N;jj++)
            {
                sum = A[ii][jj] * X_k_1[jj] + sum;
            }
            X_k[ii] = (B[ii] - (sum-A[ii][ii] * X_k_1[ii]))/A[ii][ii];
        }
        for(int ii = 0;ii<N;ii++)
        {
            diff[ii] = fabs(X_k[ii] - X_k_1[ii]);
            X_k_1[ii] = X_k[ii];
           
        }
        if (Max_e(diff)<E)
        {
            cout<<"times:"<<k<<endl;
            break;
                                }
    }
    
    return X_k;
}

double jacobi::Max_e(double * x)
{
    double * X = new double[N];
    X = x;
    double max = 0;
    for(int ii = 0;ii<N;ii++)
    {
        if (max<X[ii])
        {
            max = X[ii];
  //         cout<<max<<endl;
        }
    }
    delete [] X;
    return max;
}