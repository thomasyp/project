//
//  jacobi.h
//  jacobi
//
//  Created by 杨璞 on 15/8/23.
//  Copyright (c) 2015年 yangpu. All rights reserved.
//

#ifndef jacobi_jacobi_h
#define jacobi_jacobi_h
class jacobi
{
public:
    jacobi(int n,double *a,double *b ,double *x0,double e = 1e-5, int m = 5000)
    {
        N = n;
        A = new double*[N];
        for(int ii=0;ii<N;ii++)
        {
            A[ii] = new double[N];
            
        }
        for (int ii=0;ii<N;ii++)
        {
            for(int jj=0;jj<N;jj++)
            {
                A[ii][jj] = a[jj+ii*N];
            }
        }
        B = new double[N];
        B = b;
        X0 = new double[N];
        X0 = x0;
        E = e;
        M = m;
    }
    ~jacobi()
    {
//        delete [] B;
//        delete [] X0;
 //       for(int jj=0;jj<N;jj++){delete []A[jj];}
 //       delete [] A;
        
    }
    double * do_jacobi();
    double Max_e(double * );
private:
    int N;
    double **A;
    double *B;
    int M;
    double * X0;
    double E;
};

#endif
