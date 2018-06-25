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
    
    def readLatticeData2dat(self, filename,**kw):
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
    
    def isLatticeData(self, strs):
        lists = strs.strip().split()
        if len(lists) > 1:
            if re.match('\d\.\d{4,5}E[+-]\d{2}',lists[0]) is not None:
                if re.match('\d.\d{4,5}$',lists[1]) is not None:
                    return True
        return False
                    
    def isLatticeTag(self, strs):
        lists = strs.strip().split()
        if len(lists) > 0:
            if ('cell (' in strs) and ('[' and ']' in strs):
                return True
        return False
        
    def readKeff(self, filename):
        results = {}
        with open(filename,'r') as fileid:
            for eachline in fileid:
                if "the final estimated combined collision" in eachline:
                    data = []
                    lists = eachline.strip().split()
                    for ii in lists:
                        if re.match('\d.\d{4,5}$',ii) is not None:
                            data.append(ii)
                if "the average number of neutrons produced per fission" in eachline:
                    print 'dsfs'
                    lists = eachline.strip().split()
                    for ii in lists:
                        if re.match('\d.\d{2,3}$',ii) is not None:
                            results['v'] = ii
        if len(data) == 2:
            results['keff'] = data[0]
            results['error'] = data[1]
        else:
            return None
        return results
        
    def readDataIntoArray(self,meshtalFile,tallyNumber,group,dataType):
        """
        Fuction name: 
            readDataIntoArray           
        Fuction:
            读取原始meshtal 文件中的一个能群的网格体积以及Rslt * Vol数据
        Input parameter:
            文件路径和文件名：meshtalFile
            需要读取的哪部分tally给出tally number：tally_number
            需要读取的哪个能群的数据：group
            需要读取哪一列数据：dataType
        Return:   
            文件中的数据 list：dataArray
        """
        readtag = False
        dataArray = []
        namelists = []
        nx = 0
        ny = 0
        nz = 0
        ngroup = 0
        nline = 0
        totRow = 0 # 选择读取数据的列号
        numMesh = 0
        startline = 0
                
        
        try:
            meshFid = open(meshtalFile,'r')
        except IOError as e:
            print "Error 11004: meshtal file open error: ",e
            return -1
        else:
            print "Comment: Reading meshtal file..."
            for eachline in meshFid:                
                if "Mesh Tally Number" in eachline:
                        lists = eachline.strip().split()
                        if lists[3] == tallyNumber:
                            readtag = True
                        else:
                            readtag = False
                if readtag:
                    lists = eachline.strip().split()
                    if nx*ny*nz*ngroup*totRow == 0:                       
                        if "X direction" in eachline or "R direction" in eachline:
                            nx =  len(eachline[eachline.find(':')+1 :].strip().split()) - 1
                            
                        if "Y direction" in eachline or "Theta direction" in eachline:
                            ny =  len(eachline[eachline.find(':')+1 :].strip().split()) - 1
                            
                        if "Z direction" in eachline:
                            nz =  len(eachline[eachline.find(':')+1 :].strip().split()) - 1
                            
                            startline = (group - 1) * numMesh + 1
                        if "Energy bin boundaries" in eachline:
                            ngroup = len(lists) - 4
                            if group > ngroup:
                                print "Error 11015: Input group number is out of range!"
                                return -1
                        if "Rel Error" in eachline:                           
                            indx = lists.index("Rel")
                            del lists[indx]
                            lists[indx] = "Rel Error"
                            indx = lists.index("Rslt")
                            del lists[indx:indx+2]
                            lists[indx] = "Rslt * Vol" 
                            namelists.extend(lists)
                            totRow = len(lists)
                            if dataType not in namelists:
                                print "Error 11010: The meshtal file have not the data type: %s"%dataType
                                return -1                                              
                    else:
                        nRow = namelists.index(dataType)
                        
                        nline = nline + 1
                        if lists and nline >= startline: 
                            #print lists, readtag
                            dataArray.append(lists[nRow])
                            numMesh = nx * ny * nz
                            
                            if len(dataArray) == numMesh:
                                return dataArray
                                                                                                       
            return -1
                         
if __name__ == '__main__':
    mtr = McnpTallyReader()
#    mtr.readLatticeData2dat('pow.log',fuel=36)
#    tallys = {'fuel in active region':6, "grapht in active region":16, \
#    'bypass':26, "primary container":36, "top plenum":46, "top support plate":56,\
#    'top cap':66, 'bottom plenum':76, 'top support plate':86, 'bottom cap':96, \
#    'top reflector':116, 'bottom reflector':126, 'pump sump':136, 'rod':146,\
#    'tube':156, 'heat exchanger':166}
#    
#    print mtr.readSingleTally('dept.log', **tallys)
    
    data = mtr.readDataIntoArray("meshtal",'24',1,"Rslt * Vol")
    print data
    
    
    