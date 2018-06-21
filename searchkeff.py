# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 15:18:40 2018

@author: yang
"""
import os
from mcnp_reader import McnpTallyReader 

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
            strs = '      {}.{}  {:.7e}\n'.format(*element)
            
            outstrs = outstrs + strs
            
        return outstrs
        
    
        
def modifyMcnpInput(inputfile, modifedfile, startU233):
    m1fractionOfUTh = 6.35e-3 
    m2fractionOfUTh = 7.45e-3    
    m1 = Material("m1")
    m1.insertElement('8016', '62c', 1.27e-2)
    m1.insertElement('26000', '50c', 8.10e-3)
    m1.insertElement('24000', '50c', 1.12e-3)
    m1.insertElement('25055', '62c', 4.60e-5)
    m1.insertElement('74000', '55c', 4.60e-5)
    m1.insertElement('82000', '50c', 1.77e-2)
    
    m2 = Material("m2")
    m2.insertElement('8016', '62c', 1.49e-2)
    m2.insertElement('26000', '50c', 8.87e-3)
    m2.insertElement('24000', '50c', 1.06e-3)
    m2.insertElement('25055', '62c', 5.10e-5)
    m2.insertElement('74000', '55c', 5.10e-5)
    m2.insertElement('82000', '50c', 1.56e-2)
    
    m3 = Material("m3")
    m3.insertElement('90232', '60c', 7.45e-3)
    m3.insertElement('8016', '62c', 1.49e-2)
    m3.insertElement('26000', '50c', 8.87e-3)
    m3.insertElement('24000', '50c', 1.06e-3)
    m3.insertElement('25055', '62c', 5.10e-5)
    m3.insertElement('74000', '55c', 5.10e-5)
    m3.insertElement('82000', '50c', 1.56e-2)
    
    m4 = Material("m4")
    m4.insertElement('82000', '50c', 3.05e-2)
    
    m5 = Material("m5")
    m5.insertElement('26000', '50c', 6.63e-3 )
    m5.insertElement('24000', '50c', 8.00e-4)
    m5.insertElement('25055', '62c', 3.80e-5)
    m5.insertElement('74000', '55c', 3.80e-5)
    m5.insertElement('82000', '50c', 2.41e-2)
    
    restoffile = 'mode   n\nkcode   20000 1 50 250\nksrc    0 0 0\nprint'
    
    with open(inputfile,'r') as fid2, open(modifedfile,'w') as fid1:    
        for eachline in fid2:
            fid1.write(eachline)
            if 'c data card' in eachline:
                break
        m1.insertElement('92233', '60c', m1fractionOfUTh*startU233)
        m1.insertElement('90232', '60c', m1fractionOfUTh*(1-startU233))
        m2.insertElement('92233', '60c', m2fractionOfUTh*startU233)
        m2.insertElement('90232', '60c', m2fractionOfUTh*(1-startU233))
        fid1.write(m1.convertMcard())
        fid1.write(m2.convertMcard())
        fid1.write(m3.convertMcard())
        fid1.write(m4.convertMcard())
        fid1.write(m5.convertMcard())
        fid1.write(restoffile)
        
def cleandir(*files):
    for f in files:
        if os.path.exists(f):
            os.remove(f)
        
def searchKeff(inputfile, modifedfile, objectkeff, startU233=0.097, steplenth=0.00005, eps=5e-4):
    outfile = 'out'
    mtr = McnpTallyReader()
    cleandir(outfile, 'runtpe', 'srctp')
    modifyMcnpInput(inputfile, modifedfile, startU233)
    cmd = 'mcnpx i={} o={}'.format(modifedfile, outfile)
    os.system(cmd)
    resluts = mtr.readKeff(outfile)
    with open("keff.txt", 'w') as fid:
        fid.write('E = {:.4%}  keff = {resluts[keff]}  error = {resluts[error]}\n'.format(startU233, resluts=resluts))
        ii = 1
        while(abs(abs(float(resluts['keff'])-objectkeff)-eps) > 0):
            cleandir(outfile, 'runtpe', 'srctp')
            if ii > 100:
                return
            startU233 = startU233 - steplenth
            modifyMcnpInput(inputfile, modifedfile, startU233)
            os.system(cmd)
            resluts = mtr.readKeff(outfile)
            fid.write('E = {:.4%}  keff = {resluts[keff]}  error = {resluts[error]}\n'.format(startU233, resluts=resluts))
            ii = ii + 1 
    
    
searchKeff('crit.txt', 'inp.txt', 0.9400, 0.094)    
            
