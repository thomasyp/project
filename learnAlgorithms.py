# -*- coding: utf-8 -*-
"""
Spyder Editor

This is code for Studying introduction to algorithms

"""
import random


def InsertionSort(lists,reverse=False):
    if reverse is False:
        for j in range(1,len(lists)):
            key = lists[j]
            i = j - 1
            while i >= 0 and lists[i] > key:
                lists[i+1] = lists[i]
                i = i - 1
            lists[i+1] = key
    else:
        for j in range(1,len(lists)):
            key = lists[j]
            i = j - 1
            while i >= 0 and lists[i] < key:
                lists[i+1] = lists[i]
                i = i - 1
            lists[i+1] = key
    
    return lists
        
def addbinary(lists1,lists2):
    c = [0] * (len(lists1) + 1)
    for ii in range(len(lists1),0,-1):
        key = c[ii] + lists1[ii-1] + lists2[ii-1]
        c[ii] = key % 2
        c[ii-1] = key // 2
    
    print(c)
    
def Merge(lists,p,q,r):
    n1 = q - p + 1
    n2 = r - q
    
    lists1 = [0] * (n1 + 1)
    lists2 = [0] * (n2 + 1)
    for ii in range(n1):
        lists1[ii] = lists[p + ii]
    for ii in range(n2):
        lists2[ii] = lists[q + 1 + ii]
    lists1[n1] = float('inf')
    lists2[n2] = float('inf')
    
    ii = 0
    jj = 0
#    print(lists1)
#    print(lists2)
    for k in range(p,r+1):
        if lists1[ii] <= lists2[jj]:
            lists[k] = lists1[ii]
            ii = ii + 1
        else:
#            print('k:',k)
#            print(jj)
            
            lists[k] = lists2[jj]
            jj = jj + 1
#    print(lists)
        
    

def MergeSort(lists,p,r):
    if p < r:
        q = (p + r) // 2
        
#        print(lists)
        MergeSort(lists,p,q)
#        print('{},{}'.format(p,q))
#        print(lists)
        MergeSort(lists,q+1,r)
#        print('{},{}'.format(q+1,r))
#        print(lists)
        Merge(lists,p,q,r) 
   
#        print('{},{}'.format(p,r))
        
def paritition(data,low,high):
    index = random.randint(low,high)
    temp = data[index] 
    data[index] = data[low]
    data[low] = temp
    
    i = low
    j = high
    v = data[low]
    
    while True:
        while i <= high and data[i] <= v:
            i = i + 1
        while j >= low and data[j] > v:
            j = j - 1
        if j > i:
            temp = data[j]
            data[j] = data[i]
            data[i] = temp
        else:
            break
    data[low] = data[j]
    data[j] = v
    return j

def QuickSort(data,low,high):
    if high > low:
        p = paritition(data,low,high)
        QuickSort(data,low,p-1)
        QuickSort(data,p+1,high)

if __name__ == '__main__':
#    lists = [10,0,5,8,1,9,12,1,123,34,2356,3]
#    lists = InsertionSort(lists)
#    print(lists)
#    lists = InsertionSort(lists,reverse=True)
#    print(lists)
#    a = [1,1,1,1,1,0]
#    b = [1,1,1,1,1,0]
#    addbinary(a,b)
    lists = [random.randint(1,10000) for i in range(10)]
    MergeSort(lists,0,len(lists)-1)
#    QuickSort(lists,0,len(lists)-1)
    print(lists)
#    lists = [4]
#    Merge(lists,0,0,0)
#    print(lists)
    