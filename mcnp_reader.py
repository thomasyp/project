# -*- coding: utf-8 -*-
"""
Created on Mon Apr 09 14:56:21 2018

@author: yang
"""
import re

class McnpTallyReader(object):
    def __init__(self):
        self.keyName = []
    
    def readSingleTally(self,filename,**kw):
        """
            Function: read results(spectrum format data) from mcnp output file 
            Parameters: 1.mcnp output file
                        2.关键字参数
            Return: tally results. 
        """
        readTag = {}
        datadict = {}
        for key in kw.keys():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []     
        
        with open(filename,'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == '1tally' and lists[2] == 'nps':
                            for key, tallyNum in kw.items():
                                if lists[1] == str(tallyNum):
                                    readTag[key] = True                                   
                                else:
                                    readTag[key] = False  
                    if len(lists) == 2:               
                        for key ,tallyNum in kw.items():                
                            if readTag[key] is True:
                                if re.match('\d\.\d{5}E[+-]\d{2}',lists[0]) is not None:                                    
                                    datadict[key] = lists       
                             
        return datadict
        
    def readSpectrum2dat(self,filename,**kw):
        """
            Function: read results(spectrum format data) from mcnp output file and write the data to
            a .dat file.
            Parameters: 1.mcnp output file
                        2.关键字参数
        """
        readTag = {}
        datadict = {}
        for key in kw.keys():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []
            
        with open(filename,'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == 'total':
                        for key in readTag.keys():
                            readTag[key] = False
                        
                    if len(lists) > 3:
                        if lists[0] == '1tally' and lists[2] == 'nps': 
                            for key ,tallyNum in kw.items():
                                if lists[1] == str(tallyNum):
                                    readTag[key] = True                        
                                    datadict[key] = []
                    for key ,tallyNum in kw.items():                
                        if readTag[key] is True:
                            if re.match('\d\.\d{4}E[+-]\d{2}',lists[0]) is not None:            
                                datadict[key].append(eachline.strip())
#        print (datadict)
        for  key ,tallyNum in kw.items(): 
            datfilename = key + '.dat'                  
            with open(datfilename,'w') as f:
                for row in datadict[key]:
                    f.write('{}\n'.format(row))
    
    def readLatticeData2dat(self,filename,**kw):
        """
            Function: read results(lattice format data) from mcnp output file and write the data to
            a .dat file.
            Parameters: 1.mcnp output file
                        2.关键字参数
        """
        readTag = {}
        datadict = {}
        for key in kw.keys():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []
            
        with open(filename,'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == 'there':
                        for key in readTag.keys():
                            readTag[key] = False
                            
                if len(lists) > 3:
                        if lists[0] == '1tally' and lists[2] == 'nps':                        
                            for key ,tallyNum in kw.items():
                                if lists[1] == str(tallyNum):
                                    readTag[key] = True                        
                                    datadict[key] = []
                                    
                for key ,tallyNum in kw.items():                
                        if readTag[key] is True:
                            if self.isLatticeTag(eachline):
                                datadict[key].append(eachline.strip())
                            if self.isLatticeData(eachline):
                                datadict[key].append(eachline.strip())
        
        for  key ,tallyNum in kw.items(): 
            datfilename = key + '.dat'                  
            with open(datfilename,'w') as f:
                for row in datadict[key]:
                    f.write('{}\n'.format(row))
    
    def isLatticeData(self,strs):
        lists = strs.strip().split()
        if len(lists) > 1:
            if re.match('\d\.\d{4,5}E[+-]\d{2}',lists[0]) is not None:
                if re.match('\d.\d{4,5}$',lists[1]) is not None:
                    return True
        return False
                    
    def isLatticeTag(self,strs):
        lists = strs.strip().split()
        if len(lists) > 0:
            if ('cell (' in strs) and ('[' and ']' in strs):
                return True
        return False
                          
if __name__ == '__main__':
    mtr = McnpTallyReader()
#    mtr.readLatticeData2dat('pow.log',fuel=36)
    tallys = {'fuel in active region':6, "grapht in active region":16, \
    'bypass':26, "primary container":36, "top plenum":46, "top support plate":56,\
    'top cap':66, 'bottom plenum':76, 'top support plate':86, 'bottom cap':96, \
    'top reflector':116, 'bottom reflector':126, 'pump sump':136, 'rod':146,\
    'tube':156, 'heat exchanger':166}
    
    print mtr.readSingleTally('dept.log', **tallys)
    
    