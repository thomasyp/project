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
    m1.insertElement('8016',  '30c',  1.27e-2       )
    m1.insertElement('26054', '30c', 4.90142404E-04 )
    m1.insertElement('26056', '30c', 7.41950303E-03 )
    m1.insertElement('26057', '30c', 1.68337778E-04 )
    m1.insertElement('26058', '30c', 2.20167896E-05 )
    m1.insertElement('24050', '30c', 5.06546821E-05 )
    m1.insertElement('24052', '30c', 9.39316048E-04 )
    m1.insertElement('24053', '30c', 1.04498722E-04 )
    m1.insertElement('24054', '30c', 2.55305483E-05 )
    m1.insertElement('25055', '30c', 4.60e-5        )
    m1.insertElement('74182', '30c', 1.237239792E-05)
    m1.insertElement('74183', '30c', 6.6142183E-06  )
    m1.insertElement('74184', '30c', 1.4085057E-05  )
    m1.insertElement('74186', '30c', 1.2928327E-05  )
    m1.insertElement('82204', '30c', 2.5173595E-04  )
    m1.insertElement('82206', '30c', 4.2913470E-03  )
    m1.insertElement('82207', '30c', 3.9161785E-03  )
    m1.insertElement('82208', '30c', 9.2407385E-03  )
     
    
    m2 = Material("m2")
    m2.insertElement('8016' ,  '30c',  1.49e-2         )
    m2.insertElement('26054', '30c',  5.36736188E-04  )
    m2.insertElement('26056', '30c',  8.12481381E-03  )
    m2.insertElement('26057', '30c',  1.84340258E-04  )
    m2.insertElement('26058', '30c',  2.41097437E-05  )
    m2.insertElement('24050', '30c',  4.79410385E-05  )
    m2.insertElement('24052', '30c',  8.88995545E-04  )
    m2.insertElement('24053', '30c',  9.89005758E-05  )
    m2.insertElement('24054', '30c',  2.41628403E-05  )
    m2.insertElement('25055', '30c',  5.10e-5         )    
    m2.insertElement('74182', '30c',  1.371722437E-05 )
    m2.insertElement('74183', '30c',  7.3331551E-06   )
    m2.insertElement('74184', '30c',  1.5616041E-05   )
    m2.insertElement('74186', '30c',  1.4333580E-05   )
    m2.insertElement('82204', '30c',  2.2186897E-04   )
    m2.insertElement('82206', '30c',  3.7822042E-03   )
    m2.insertElement('82207', '30c',  3.4515471E-03   )
    m2.insertElement('82208', '30c',  8.1443797E-03   )
      
    
    m3 = Material("m3")
    m3.insertElement('90232' ,  '30c',   7.45e-3         )
    m3.insertElement('8016' ,  '30c', 1.49e-2         )
    m3.insertElement('26054', '30c', 5.36736188E-04  )
    m3.insertElement('26056', '30c', 8.12481381E-03  )
    m3.insertElement('26057', '30c', 1.84340258E-04  )
    m3.insertElement('26058', '30c', 2.41097437E-05  )
    m3.insertElement('24050', '30c', 4.79410385E-05  )
    m3.insertElement('24052', '30c', 8.88995545E-04  )
    m3.insertElement('24053', '30c', 9.89005758E-05  )
    m3.insertElement('24054', '30c', 2.41628403E-05  )
    m3.insertElement('25055', '30c', 5.10e-5         )    
    m3.insertElement('74182', '30c', 1.371722437E-05 )
    m3.insertElement('74183', '30c', 7.3331551E-06   )
    m3.insertElement('74184', '30c', 1.5616041E-05   )
    m3.insertElement('74186', '30c', 1.4333580E-05   )
    m3.insertElement('82204', '30c', 2.2186897E-04   )
    m3.insertElement('82206', '30c', 3.7822042E-03   )
    m3.insertElement('82207', '30c', 3.4515471E-03   )
    m3.insertElement('82208', '30c', 8.1443797E-03   )
    
    
    m4 = Material("m4")
    m4.insertElement('82204', '30c', 4.3378228E-04)
    m4.insertElement('82206', '30c', 7.3946940E-03)
    m4.insertElement('82207', '30c', 6.7482172E-03)
    m4.insertElement('82208', '30c', 1.5923307E-02)
      
    
    m5 = Material("m5")
    m3.insertElement('26054', '30c', 4.01190634E-04)
    m5.insertElement('26056', '30c', 6.07300063E-03)
    m5.insertElement('26057', '30c', 1.37787589E-04)
    m5.insertElement('26058', '30c', 1.80211500E-05)
    m5.insertElement('24050', '30c', 3.61819158E-05)
    m5.insertElement('24052', '30c', 6.70940034E-04)
    m5.insertElement('24053', '30c', 7.46419440E-05)
    m5.insertElement('24054', '30c', 1.82361059E-05)
    m5.insertElement('25055', '30c', 3.80e-5       )    
    m5.insertElement('74182', '30c', 1.02206768E-05)
    m5.insertElement('74183', '30c', 5.4639195E-06 )
    m5.insertElement('74184', '30c', 1.1635482E-05 )
    m5.insertElement('74186', '30c', 1.0679922E-05 )
    m5.insertElement('82204', '30c', 3.4275911E-04 )
    m5.insertElement('82206', '30c', 5.8430205E-03 )
    m5.insertElement('82207', '30c', 5.3321978E-03 )
    m5.insertElement('82208', '30c', 1.2582023E-02 )
     
    
    restoffile = 'mode   n\nkcode   50000 1 50 250\nksrc    0 0 0\nprint'
    
    with open(inputfile,'r') as fid2, open(modifedfile,'w') as fid1:    
        for eachline in fid2:
            fid1.write(eachline)
            if 'c data card' in eachline:
                break
        m1.insertElement('92233', '30c', m1fractionOfUTh*startU233)
        m1.insertElement('90232', '30c', m1fractionOfUTh*(1-startU233))
        m2.insertElement('92233', '30c', m2fractionOfUTh*startU233)
        m2.insertElement('90232', '30c', m2fractionOfUTh*(1-startU233))
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
        
def searchKeff(inputfile, modifedfile, objectkeff, startU233=0.09965, steplenth=0.0005, eps=5e-4):
    outfile = 'out'
    mtr = McnpTallyReader()
    cleandir(outfile, 'runtpe', 'srctp')
    modifyMcnpInput(inputfile, modifedfile, startU233)
    cmd = 'mpirun -np 12 /home/daiye/bin/mcnp5.mpi inp={} outp={}>>out.log'.format(modifedfile, outfile)
    os.system(cmd)
    resluts = mtr.readKeff(outfile)
    with open("keff.txt", 'w') as fid:
        fid.write('E = {:.4%}  keff = {resluts[keff]}  error = {resluts[error]}\n'.format(startU233, resluts=resluts))
        ii = 1
        while(abs(float(resluts['keff'])-objectkeff) > eps):
            cleandir(outfile, 'runtpe', 'srctp')
            if ii > 100:
                return
            startU233 = startU233 - steplenth
            modifyMcnpInput(inputfile, modifedfile, startU233)
            os.system(cmd)
            resluts = mtr.readKeff(outfile)
            fid.write('E = {:.4%}  keff = {resluts[keff]}  error = {resluts[error]}\n'.format(startU233, resluts=resluts))
            ii = ii + 1 
    
    
searchKeff('crit.txt', 'inp.txt', 0.9800)    
            
