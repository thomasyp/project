# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 21:56:48 2018
power_distribution Version 1.0
用于将mcnp输出文件中的f6卡统计的lattic tally 格式的数据转换成功率或功率密度数据并
存入csv格式文件中。

@author: yangpu
"""

import csv
import math
from mcnp_reader import McnpTallyReader 

class PowerDesityCreater(object):
    def __init__(self,powerFile,volFile,sideLenth,cellflux,r,graghOrFuel,mode = 'powerD'):
        powTallyData = {}
        volTallyData = {}
        self.volData = {}
        self.sideLenth = sideLenth
        self.powDesity = {}
        self.coreRadius = 115.2562522
        self.coreHeight = 180.4010904
        self.power = 2e6
        self.mode = mode
        self.corePowDesity = self.power/(math.pi*self.coreRadius**2*self.coreHeight)
        self.volOfFuelLattice = math.pi*r**2*self.coreHeight
        #print self.volOfFuelLattice
        self.volOfGraphteLattice = 3**0.5/2.0*self.sideLenth**2*self.coreHeight - math.pi*2**2*self.coreHeight
        #print self.volOfGraphteLattice
        powTallyData = self.readLatticeTally(powerFile)
        sums = 0
        for key,v in powTallyData.items():
                sums = sums + v
        print sums
        volTallyData = self.readLatticeTally(volFile)
        #print volTallyData
        self.volData = self.latticeVolume(volTallyData,cellflux,graghOrFuel)
        self.createPowerDesity(powTallyData)
    
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
                if len(lists) == 2: 
                    lists = eachline.strip().split()
                    tallyData[lattice] = float(lists[0])
            fileid.close()
            
        return tallyData
        
    def createPowerDesity(self,powerData):

        # 绝对功率密度
        if self.mode == 'powerD':
            self.powDesity = {key : powerData[key]/self.volData[key] for key in \
            self.volData.keys() if self.volData[key] != 0 }
        # 归一化功率密度
        elif self.mode == 'NormPowerD':
            self.powDesity = {key : powerData[key]/ self.volData[key] / \
            self.corePowDesity for key in self.volData.keys() if self.volData[key] != 0 }
        #功率
        elif self.mode == 'power':
            self.powDesity = {key : powerData[key] for key in self.volData.keys() if self.volData[key] != 0 }
        else:
             print "mode error!"
                
    def latticeVolume(self,volTallyData,cellflux,tag):
        
        volData = {}
        if tag == 'f':
            ordinaryLatticeVol = self.volOfFuelLattice
        elif tag == 'g':
            ordinaryLatticeVol = self.volOfGraphteLattice
        else:
            print "tag error!"
            return -1
          
        for key in volTallyData:
            volum = volTallyData[key] / cellflux
            if abs(1 -  volum / ordinaryLatticeVol) < 0.01:                              
                volData[key] = ordinaryLatticeVol
                #volData[key] = volum
            else:
                volData[key] = volum
        #print volData['0 1 0'], volData['2 0 0'],volData['3 0 0'],volData['4 0 0'],ordinaryLatticeVol
        return volData
        
    def output2csv(self,csvfilename,voldata = False):
        strength = self.power * 2.439  / 200 
#        strength = 1
        csvfile = open(csvfilename,'wb')
        writer = csv.writer(csvfile)
        sort1 = sorted(self.powDesity.items(),key=lambda e:int(e[0].strip().split()[0]),reverse=False)
        sort2 = sorted(sort1,key=lambda e:int(e[0].strip().split()[1]),reverse=False) 
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
                lists = item[0].strip().split()                
                pos = ['%.2f'%(self.sideLenth * (int(lists[0]) + int(lists[1]) / 2.0)),\
                '%.2f'%(self.sideLenth * 3.0 **(0.5) / 2.0 * int(lists[1])),'%.2f'%int(lists[2])]
                if item[1] > 0:
                    strs = [pos , item[1]*strength]
                    #print strs
                    writer.writerow(strs)
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
                lists = item[0].strip().split()
                pos = ('%.2f'%(self.sideLenth * (int(lists[0]) + int(lists[1]) / 2.0)),\
                '%.2f'%(self.sideLenth * 3.0 **(0.5) / 2.0 * int(lists[1])),'%.2f'%int(lists[2]))
                if item[1] > 0:
                    strs = [pos , item[1]*strength,self.volData[item[0]]]
                    writer.writerow(strs)
        csvfile.close()

if __name__== '__main__':
    sideLenth = 10.0222828 #正六边形对边距
    r = 2.0044566 #熔盐流道半径
    cellflux = 2.28775E-05
    mtr = McnpTallyReader()
    mtr.readLatticeData2dat('pow.log',fuel=36,graphte=66)
    mtr.readLatticeData2dat('vol.log',volfuel=34,volgraphte=64)
    fuel = PowerDesityCreater('fuel.dat','volfuel.dat',sideLenth,cellflux,r,'f',mode = 'NormPowerD')
    fuel.output2csv('fuel1.csv',voldata = True)
    graphte = PowerDesityCreater('graphte.dat','volgraphte.dat',sideLenth,cellflux,r,'g',mode = 'NormPowerD')
    graphte.output2csv('graphte1.csv',voldata = True)
    
"""
[a*(i+j/2.0),a*3**(0.5)/2*j]
"""    