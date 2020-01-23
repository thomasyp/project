# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 21:56:48 2018
power_distribution Version 1.1
用于将mcnp输出文件中的f6卡统计的lattic tally 格式的数据转换成功率或功率密度数据并
存入csv格式文件中。
在v1.0的基础上增加了__add__函数，支持fuel 和 graphte对象相加的操作，可以直接得到总
的功率或者功率密度分布。
@author: yangpu
"""

import csv
import math
from mcnp_reader import McnpTallyReader 

class PowerDesityCreater(object):
    def __init__(self,mode='powD',**kw):
        self.powTallyData = {}
        self.volTallyData = {}
        self.volData = {}
    #        self.sideLenth = kw[sideLenth]
        self.powDesity = {}
        self.mode = mode
        self.coreRadius = 115.2562522
        self.coreHeight = 180.4010904
        self.power = 2e6
        self.corePowDesity = self.power/(math.pi*self.coreRadius**2*self.coreHeight)
        for key in kw:
           
            if key == 'sideLenth':
                self.sideLenth = kw[key]
            if key == 'powerFile':
                powerFile = kw[key]
            if key == 'volFile':
                volFile = kw[key]
            if key == 'cellFlux':
                cellFlux = kw[key]
            if key == 'dataType':
                dataType = kw[key]
            if key == 'radius':
                radius = kw[key]
            
        if len(kw) > 0 :                                
                        
            self.volOfFuelLattice = math.pi*radius**2*self.coreHeight
            #print self.volOfFuelLattice
            self.volOfGraphteLattice = 3**0.5/2.0*self.sideLenth**2*self.coreHeight - math.pi*2**2*self.coreHeight
            #print self.volOfGraphteLattice
            self.powTallyData = self.readLatticeTally(powerFile)
            sums = 0
            for key,v in self.powTallyData.items():
                    sums = sums + v
            print sums
            self.volTallyData = self.readLatticeTally(volFile)
            #print volTallyData
            self.volData = self.latticeVolume(cellFlux,dataType)
            self.createPowerDesity()        
    
    def readLatticeTally(self,filename):
        tallyData = {}
        try:
            fileid = open(filename,'r')
        except IOError as e:
            print "*** file open error: ",e
        else:
            for eachline in fileid:
                lists = eachline.strip().split()
                if '[' in eachline:
                    lattice = eachline[eachline.index('[') + 1:eachline.index(']')]
                    pos = self.createCoordate(lattice)                                    
                if len(lists) == 2: 
                    lists = eachline.strip().split()
                    tallyData[pos] = float(lists[0])
            fileid.close()
#            print tallyData
        return tallyData
        
    def createPowerDesity(self):

        strength = self.power * 2.439  / 200
        # 绝对功率密度
        if self.mode == 'powerD':            
            for key,value in self.volData.items():
                if value != 0:                                    
                    self.powDesity[key] = self.powTallyData[key]/self.volData[key] \
                    * strength
        # 归一化功率密度
        elif self.mode == 'NormPowerD':
            
            for key,value in self.volData.items():
                if value != 0:                                    
                    self.powDesity[key] = self.powTallyData[key]/self.volData[key]/ \
            self.corePowDesity * strength
        #功率
        elif self.mode == 'power':            
            self.powDesity = {key: self.powTallyData[key] * strength for key in self.volData.keys() if self.volData[key] != 0}
        else:
             print "mode error!"
             
    def createCoordate(self,strs):
        lists = strs.strip().split()
        pos = ('%.2f'%(self.sideLenth * (int(lists[0]) + int(lists[1]) / 2.0)),\
                '%.2f'%(self.sideLenth * 3.0 **(0.5) / 2.0 * int(lists[1])),'%.2f'%int(lists[2]))
        return pos
                
    def latticeVolume(self,cellflux,tag):
        
        volData = {}
        if tag == 'f':
            ordinaryLatticeVol = self.volOfFuelLattice
        elif tag == 'g':
            ordinaryLatticeVol = self.volOfGraphteLattice
        else:
            print "tag error!"
            return -1
          
        for key in self.volTallyData:
            volum = self.volTallyData[key] / cellflux
            if abs(1 -  volum / ordinaryLatticeVol) < 0.01:                              
                volData[key] = ordinaryLatticeVol
                #volData[key] = volum
            else:
                volData[key] = volum
        #print volData['0 1 0'], volData['2 0 0'],volData['3 0 0'],volData['4 0 0'],ordinaryLatticeVol
        return volData
        
    def output2csv(self,csvfilename,voldata = False):
       
#        strength = 1
        csvfile = open(csvfilename,'wb')
        writer = csv.writer(csvfile)
#        print self.powDesity
        sort1 = sorted(self.powDesity.items(),key=lambda item:float(item[0][0]),reverse=False)
        
        sort2 = sorted(sort1,key=lambda item:float(item[0][1]),reverse=False) 
#        print sort2
        # 不输出体积
        if voldata == False:
            if self.mode == 'powerD':
                writer.writerow(['Coordinates','Power desity (W/cm3)'])
            elif self.mode == 'NormPowerD':
                writer.writerow(['Coordinates','Normalized Power desity '])
            elif self.mode == 'power':
                writer.writerow(['Coordinates','Power  (W)'])
            else:
                 print "mode error!"
                 
            for item in sort2:                                              
                
                if item[1] > 0:
                    row = [item[0] , item[1]]
                    #print strs
                    writer.writerow(row)
        #输出体积            
        else:
            if self.mode == 'powerD':
                writer.writerow(['Coordinates','Power desity (W/cm3)','Volum (cm3)'])
            elif self.mode == 'NormPowerD':
                writer.writerow(['Coordinates','Normalized Power desity ','Volum (cm3)'])
            elif self.mode == 'power':
                writer.writerow(['Coordinates','Power  (W)','Volum (cm3)'])
            else:
                 print "mode error!"
            
            for item in sort2:
                if item[1] > 0:
#                    print item 
                    strs = [item[0], item[1],self.volData[item[0]]]
                    writer.writerow(strs)
        csvfile.close()
    
    def __add__(self,other):
        if not isinstance(other,PowerDesityCreater):
            return NotImplemented
        
        if self.mode == other.mode:
            result = PowerDesityCreater()
            result.mode = self.mode
            for key,v in self.powTallyData.items():
                    result.powTallyData[key] = self.powTallyData[key] + other.powTallyData[key]
            for key,v in self.volData.items():
                    result.volData[key] = self.volData[key] + other.volData[key]
            result.createPowerDesity()
            return result
        else:
            print"Error: the mode of two object are inconsistent!"
            return None

if __name__== '__main__':
    sideLen = 10.0222828 #正六边形对边距
    r = 2.0044566 #熔盐流道半径
    cellflux = 2.2878E-05
    mtr = McnpTallyReader()
    mtr.readLatticeData2dat('pow.log',fuel=36,graphte=66)
    mtr.readLatticeData2dat('vol.log',volfuel=34,volgraphte=64)
    fuel = PowerDesityCreater('powerD',powerFile='fuel.dat',volFile='volfuel.dat',\
    sideLenth=sideLen,cellFlux=cellflux,radius=r,dataType = 'f')
    graphte = PowerDesityCreater('powerD',powerFile='graphte.dat',volFile='volgraphte.dat',\
    sideLenth=sideLen,cellFlux=cellflux,radius=r,dataType = 'g')
    fuel.output2csv('fuel.csv',voldata = True)
    graphte.output2csv('graphte.csv',voldata = True)

#    tot = fuel + graphte
#    tot.output2csv('tot.csv',voldata = True)
    
"""
[a*(i+j/2.0),a*3**(0.5)/2*j]
"""    