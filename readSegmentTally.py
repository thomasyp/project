# -*- coding: utf-8 -*-
"""
Created on Wed May 02 16:36:05 2018

@author: yang
"""
import numpy as np
import pandas as pd
import re
import math
import matplotlib.pyplot as plt


class ReadTally(object):
    
    def __init__(self):
        pass
    
    def getSegmentCoordate(self,**kw):
        positiveSurfaces = {}
        negativeSurfaces = {}        
        for key in kw.keys():
            if(int(key) >0):            
                positiveSurfaces[key] = float(kw[key])
            else:
                negativeSurfaces[key] = float(kw[key])
        sortedPosSurfaces = sorted(positiveSurfaces.items(), key=lambda item:item[1])
        sortedNegSurfaces = sorted(negativeSurfaces.items(), key=lambda item:item[1])
       
        if len(sortedPosSurfaces) == 0 or len(sortedNegSurfaces) == 0:
            print "Error: surfaces lists is empty!"
            return None
        if sortedPosSurfaces[-1][1] > sortedNegSurfaces[0][1]:
            print "Error: positive surface and negative surface set error! "
            return None
        
        return sortedPosSurfaces[-1][1] + (sortedNegSurfaces[0][1] - sortedPosSurfaces[-1][1]) / 2.
        
    def write2dat(self, filename, **kw):
        readTag = {}
        data = np.array([])
        reString = '^\d\.\d{4}E[+-]\d{2}\s+\d\.\d{5}E[+-]\d{2}\s+\d\.\d+$'
        
        for key, v in kw.items():
            self.keyName.append(key)
            readTag[key] = False
            
        

        with open(filename, 'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 3:
                    
                    if lists[0] == '1tally' and lists[2] == 'nps':
                            for key, tallyNum in kw.items():
                                if lists[1] == str(tallyNum):
                                    readTag[key] = True
                                    datadict[key] = []
                                else:
                                    readTag[key] = False                                    
                
                    for key, tallyNum in kw.items():
                        if readTag[key] is True:
                            if re.match(reString, eachline.strip()) is not None:
                                datadict[key].append(eachline.strip())
                                data
        #        print (datadict)
        for key, tallyNum in kw.items():
            datafilename = key + '.dat'  # type: str
            with open(datafilename, 'w') as f:
                for row in datadict[key]:
                    f.write('{}\n'.format(row))


if __name__ == '__main__':
    rt = ReadTally();
    dicts = {'-2000':'175','-2001':'170','-2002':'165','-2003':'160','-2004':'155','2005 ':'150'}
    print rt.getSegmentCoordate(**dicts)
    
 