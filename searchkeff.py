# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 15:18:40 2018

@author: yang
"""
from collections import namedtuple

class Material(object):
    mat = namedtuple('mat', 'elementNo, lib, fraction')
    def __init__(self, name):
        self.name = name
        self.element = []
        
    def insertElement(self, elementNo, lib, fraction):
        self.element.append(self.mat(elementNo, lib, fraction))        
    
    def setDesity(self, density):
        self.density = density
        
    def getDesity(self):
        return self.density
        
    def convertMcard(self):
        outstrs = '{} '.format(self.name)
        
        for element in self.element:
            strs = '      {}.{}  {}\n'.format(*element)
            
            outstrs = outstrs + strs
            
        return outstrs
        
    
        
#def modifyMcnpInput(inputfile, step_length, )
        
m1 = Material("m1")
m1.insertElement('82206', '60c', '6.35635e-4')
m1.insertElement('90232', '60c', '8.10e-3')
m1.insertElement('90232', '60c', '8.10e-3')

m1.insertElement('90232', '60c', '8.10e-3')
m1.insertElement('90232', '60c', '8.10e-3')
srt = m1.convertMcard()
with open("crit.txt",'r') as fid2, open("test.txt",'w') as fid1:    
    for eachline in fid2:
        fid1.write(eachline)
        if 'c data card' in eachline:
            break
       
            
