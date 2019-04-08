#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
from tool.handle_mcnpinp import McnpinpHandler 
from compoundcalculator.compound_density import Isotope, Nuclide, Compound, Material
import os
from tool.mcnp_reader import McnpTallyReader
import argparse

def changeReflector(inp, step, designator, section='cell'):
    mh = McnpinpHandler()
    line = mh.readContent(inp, designator, section)
    data = line.strip().split()[2]
    if float(data) > 0:
        replacedata = str(float(data)+step)
    else:
        replacedata = str(float(data)-step)
    newline = line.replace(data, replacedata)
    mh.modifyinp(inp, designator, newline, section)

u235 = Isotope('U235', 92, 235.043923)
u238 = Isotope('U238', 92, 238.050783)
th232 = Isotope('Th232', 90, 232.03805)
pu239 = Isotope('Pu239', 94, 239.0) 
f19 = Isotope('F19', 9, 18.998403)
be9 = Isotope('Be9', 4, 9.012182)
li6 = Isotope('li6', 3, 9.012182)
li7 = Isotope('li7', 3, 9.012182)
cl37 = Isotope('cl37', 17, 36.965903)
mg24= Isotope('mg24', 12, 23.985042)
mg25= Isotope('mg25', 12, 24.985837)
mg26= Isotope('mg26', 12, 25.982593)
na23 = Isotope('na23', 11, 22.989770)
udict = {u235:0.1995, u238:0.8005}
fdict = {f19:1}
cldict = {cl37:1}
pudict = {pu239:1}
mgdict = {mg24:0.7899, mg25:0.10, mg26:0.1101}
nadict = {na23:1}
cl = Nuclide('Cl', cldict)
u = Nuclide('U', udict)
f = Nuclide("F", fdict)
th = Nuclide("Th", {th232:1})
be = Nuclide("Be", {be9:1})
pu = Nuclide("Pu", pudict)
mg = Nuclide("Mg", mgdict)
na = Nuclide("Na", nadict)
nacldict = {na:1, cl:1}
thcl4dict = {th:1, cl:4}
mgcl2dict = {mg:1, cl:2}
pucl3dict = {pu:1, cl:3}
ucl3dic = {u:1, cl:3}
# lifdict = {li:1, f:1}
nacl = Compound('NaCl', nacldict, 2.1359, 0.543e-3)
thcl4 = Compound('ThCl4', thcl4dict, 4.823, 0.0014)

pucl3 = Compound('PuCl3', pucl3dict, 4.809, 0)
ucl3 = Compound('UCl3', pucl3dict, 6.3747, 1.5222e-3)
# thf4 = Compound('ThF4', thf4dict, 6.490933)
# bef2 = Compound('BeF2', bef2dict, 1.9602115)
matdict = {}
mtr = McnpTallyReader()
# parser=argparse.ArgumentParser(description='input file name, node and ppn')
# parser.add_argument('-n',action="store",dest="node",type=int,default=1)
# parser.add_argument('-p',action="store",dest="ppn",type=int,default=1)
# parser.add_argument('inp',action="store",type=str)
# args=parser.parse_args()
# print('inputfile=%s' %args.inp,'ppn=%s' %args.ppn)
# inp = args.inp
# node = args.node
# ppn = args.ppn
inp = 'cor1'
results = {}
# startmolnacl = 80
startmolnacl = 80
endreflectorThickness = 5
thicknessStep = 5
mh = McnpinpHandler()
mh.cleanup(inp)
# loop for reflector
for kk in range(0, endreflectorThickness, thicknessStep):
    if kk == 0:
        changeReflector(inp, 0, '15', 'surface')
        changeReflector(inp, 0, '16', 'surface')
        changeReflector(inp, 0, '17', 'surface')
        changeReflector(inp, 0, '18', 'surface')
        changeReflector(inp, 0, '19', 'surface')
        changeReflector(inp, 0, '20', 'surface')
    else:
        changeReflector(inp, thicknessStep, '15', 'surface')
        changeReflector(inp, thicknessStep, '16', 'surface')
        changeReflector(inp, thicknessStep, '17', 'surface')
        changeReflector(inp, thicknessStep, '18', 'surface')
        changeReflector(inp, thicknessStep, '19', 'surface')
        changeReflector(inp, thicknessStep, '20', 'surface')
    # loop for nacl 
    for ii in range(startmolnacl, 0, -5):
        matdict[nacl] = ii
        # loop for pucl    
        for jj in range(100-ii, 0, -5):     
            matdict[pucl3] = jj        
            matdict[thcl4] = 100 - ii - jj
            mat = Material('mat1', matdict, 900)
            # print(uf4.getActomicMass())
            # print(thf4.getActomicMass())
            density = mat.getDensity()
            print(density)
            # print(mat.toMcnpCard().strip())
            line = mat.toMcnpCard().strip()
            mh.modifyinp(inp, 'm1', 'm1 '+line, 'data')
            line = mh.readContent(inp, '4')
            print(line)
            # print(line.strip().split()[2])
            newline = line.replace(line.strip().split()[2], '-{:.4f}'.format(density))
            print(newline)
            mh.modifyinp(inp, '4', newline)
            os.system('mcnp5'+ ' n=' + inp)
            # os.system('mpirun -r ssh -np '+ str(int(node*ppn)) +' /home/daiye/bin/mcnp5.mpi n=' + inp)
            if os.path.isfile(inp+'o'):
                print('MCNP5 run finished!')
                result = mtr.readKeff(inp+'o')
                if os.path.isfile(inp+'o'):
                    oldfilename = inp+'o'
                    newfilename = inp+'o_'+str(kk)+'_'+str(matdict[nacl])+'_'+str(matdict[pucl3])+'_'+str(matdict[thcl4])
                    mh.deleteFiles(newfilename)
                    os.rename(oldfilename, newfilename)
                mh.cleanup(inp)
            else:
                print('error!!!,MCNP5 run failed!')
                exit(0)
            results[(kk, matdict[nacl], matdict[pucl3], matdict[thcl4])] = result['keff']
            print("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format(kk, matdict[nacl], matdict[pucl3], matdict[thcl4], result['keff']))

with open("results.out", 'w') as fid, open("search.out", 'w') as fid2:
    fid.write("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format('Thickness', 'Nacl', 'PuCl3', 'ThCl4', 'Keff'))
    fid2.write("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format('Thickness', 'Nacl', 'PuCl3', 'ThCl4', 'Keff'))
    for key, value in results.items():
        fid2.write("{0[0]:<10} {0[1]:<10} {0[2]:<10} {0[3]:<10} {1:<10}\n".format(key, value))
        if float(value) > 0.97 and float(value)<0.99:
            fid.write("{0[0]:<10} {0[1]:<10} {0[2]:<10} {0[3]:<10} {1:<10}\n".format(key, value))

