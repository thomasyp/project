#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
from compoundcalculator.compound_density import Isotope, Nuclide, Compound, Material
from tool.handle_mcnpinp import McnpinpHandler
from tool.mcnp_reader import McnpTallyReader
import argparse
import os
import re
import numpy as np


def inital(inp, diff, surflist=None):
    mh = McnpinpHandler()

    for surf in surflist:
        line1 = mh.readContent(inp, surf, section='surface')
        oldsurf = float(line1.strip().split()[2])
        if oldsurf > 0:
            newsurf = oldsurf - diff
        else:
            newsurf = oldsurf + diff

        newline = line1.replace(line1.strip().split()[2], "{:.1f}".format(newsurf))
        mh.modifyinp(inp, surf, newline, section='surface')



def deleteNonMcnpCard(inp, cardlist=None):
    shadow = False
    if not cardlist:
        return -1
    with open(inp, 'r') as fid, open(inp+'bp', 'w') as fid2:
        for line in fid:
            shadow = False
            lists = line.strip().split()
            if bool(lists):
                for card in cardlist:
                    if re.match(card, lists[0], re.I) is not None:
                        shadow = True
                        break
            if not shadow:
                fid2.write(line)
    os.remove(inp)
    os.rename(inp+'bp', inp)
    return 1

def changeMcnpLine(inp, step, designator, section='cell'):
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
pu238 = Isotope('Pu238', 94, 238.0)
pu239 = Isotope('Pu239', 94, 239.0)
pu240 = Isotope('Pu240', 94, 240.0)
pu241 = Isotope('Pu241', 94, 241.0)
pu242 = Isotope('Pu242', 94, 242.0)
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
# Pu from MOX
pudict = {pu238:0.019497, pu239:0.5875682, pu240:0.2371, pu241:0.10133776, pu242:0.05449704}
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
nacl = Compound('NaCl', nacldict, 2.1393, 0.543e-3)
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
inp = 'puth'
cardlist=['naclsets', 'puclsets', 'coresizesets', 'reflectorsets']

mh = McnpinpHandler()
paralists = []
newcardlist = []
for card in cardlist:
    line = mh.readContent(inp, card, section='data')
    if line:
        lists = line.strip().split()
        newcardlist.append(card)
        paralists.append([int(x) if type(eval(x))==int else float(x) for x in lists[1:]])

para = {card: para for card, para in zip(newcardlist, paralists)}

deleteNonMcnpCard(inp, cardlist)
print(para)
initalornot = True

if 'naclsets' in para.keys():    
    startmolnacl = para['naclsets'][0]
    endmolnacl = para['naclsets'][1]
    stepmolnacl = para['naclsets'][2]
    
else:
    startmolnacl = 0
    stepmolnacl = 1
    endmolnacl = 1
if 'puclsets' in para.keys(): 
    startmolpucl = para['puclsets'][0]
    endmolpucl = para['puclsets'][1]
    stepmolpucl = para['puclsets'][2]
else:
    startmolpucl = 0
    stepmolpucl = 1
    endmolpucl = 1

if stepmolnacl > 0:
   stepmolnacl = -1 * stepmolnacl
if stepmolpucl > 0:
   stepmolpucl = -1 * stepmolpucl

if 'coresizesets' in para.keys():
    endCoreSize = para['coresizesets'][0]
    coreSizeStep = para['coresizesets'][1]
else:
    endCoreSize = 1
    coreSizeStep = 1

if 'reflectorsets' in para.keys():
    endreflectorThickness = para['reflectorsets'][0]
    thicknessStep = para['reflectorsets'][1]
    initalornot = True
else:
    endreflectorThickness = 1
    thicknessStep = 1
    initalornot = False


print('startmolnacl:', startmolnacl)
print('stepmolnacl:', stepmolnacl)
print('startmolpucl:', startmolpucl)
print('stepmolpucl:', stepmolpucl)
print('endreflectorThickness:', endreflectorThickness)
print('endCoreSize:', endCoreSize)

results = {}
mh = McnpinpHandler()
mh.cleanup(inp)
# loop for reflector
resultfile = inp + 'results.out'
seachoutfile = inp + 'search.out'
with open(resultfile, 'w') as fid:
   fid.write("{:^10} {:^10} {:^10} {:^10} {:^10} {:^20} {:^20} {:^20} {:^20} {:^20} {:^20} {:^20} {:^20} {:^20} {:^20}\n"\
       .format('Core size', 'Thickness', 'Nacl', 'PuCl3', 'ThCl4', \
        'nucl. inter in 4', '(n,xn) in 4', 'nucl. inter in 5', '(n,xn) in 5', 'nucl. inter in 6', '(n,xn) in 6', \
        'nucl. inter in 7', '(n,xn) in 7', 'Total Neutron production', 'Escape of neutron',))
   
thicknessOfHalloy = 2
for mm in range(0, endCoreSize, coreSizeStep):
    #  set thickness of reflector to 0  
    if initalornot:
        line1 = mh.readContent(inp, '18', section='surface')
        line2 = mh.readContent(inp, '15', section='surface')
        surf1 = float(line1.strip().split()[2])
        surf2 = float(line2.strip().split()[2])
        diff = abs(abs(surf1) - abs(surf2))  
        surflist = ['18', '19', '20', '21', '22', '23']
        inital(inp, diff, surflist)
    
    if mm == 0:
        changeMcnpLine(inp, 0, '2', 'surface')
        changeMcnpLine(inp, 0, '13', 'surface')
        changeMcnpLine(inp, 0, '14', 'surface')
        changeMcnpLine(inp, 0, '15', 'surface')
        changeMcnpLine(inp, 0, '16', 'surface')
        changeMcnpLine(inp, 0, '17', 'surface')
        changeMcnpLine(inp, 0, '18', 'surface')
        changeMcnpLine(inp, 0, '19', 'surface')
        changeMcnpLine(inp, 0, '20', 'surface')
        changeMcnpLine(inp, 0, '21', 'surface')
        changeMcnpLine(inp, 0, '22', 'surface')
        changeMcnpLine(inp, 0, '23', 'surface')
    else:
        changeMcnpLine(inp, coreSizeStep, '2', 'surface')
        changeMcnpLine(inp, coreSizeStep, '13', 'surface')
        changeMcnpLine(inp, coreSizeStep, '14', 'surface')
        changeMcnpLine(inp, coreSizeStep, '15', 'surface')
        changeMcnpLine(inp, coreSizeStep, '16', 'surface')
        changeMcnpLine(inp, coreSizeStep, '17', 'surface')
        changeMcnpLine(inp, coreSizeStep, '18', 'surface')
        changeMcnpLine(inp, coreSizeStep, '19', 'surface')
        changeMcnpLine(inp, coreSizeStep, '20', 'surface')
        changeMcnpLine(inp, coreSizeStep, '21', 'surface')
        changeMcnpLine(inp, coreSizeStep, '22', 'surface')
        changeMcnpLine(inp, coreSizeStep, '23', 'surface')
    for kk in range(0, endreflectorThickness, thicknessStep):
        if kk == 0:
            
            changeMcnpLine(inp, 0, '18', 'surface')
            changeMcnpLine(inp, 0, '19', 'surface')
            changeMcnpLine(inp, 0, '20', 'surface')
            changeMcnpLine(inp, 0, '21', 'surface')
            changeMcnpLine(inp, 0, '22', 'surface')
            changeMcnpLine(inp, 0, '23', 'surface')
        else:
            
            changeMcnpLine(inp, thicknessStep, '18', 'surface')
            changeMcnpLine(inp, thicknessStep, '19', 'surface')
            changeMcnpLine(inp, thicknessStep, '20', 'surface')
            changeMcnpLine(inp, thicknessStep, '21', 'surface')
            changeMcnpLine(inp, thicknessStep, '22', 'surface')
            changeMcnpLine(inp, thicknessStep, '23', 'surface')
        # loop for nacl
        for ii in np.arange(startmolnacl, endmolnacl, stepmolnacl):
            matdict[nacl] = ii
            # loop for pucl
            for jj in np.arange(100-ii, endmolpucl, stepmolpucl):
                if jj > startmolpucl:
                    continue
                ## set initials
               
                results['escape'] = 0 # escape of kcode mode
                
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
                
                os.system('mcnpx'+ ' n=' + inp)
                # os.system('mpirun -r ssh -np '+ str(int(node*ppn)) +' /home/daiye/bin/mcnpx n=' + inp)
                if os.path.isfile(inp+'o'):
                    print('MCNP5 run finished!')
                    datadic = mtr.getNeutronWeightBalance(inp+'o')
                    
                    results['nucl_interaction4'] = datadic['physical events']['4']['nucl. interaction']
                    results['n_xn4'] = datadic['physical events']['4']['(n,xn)'] + datadic['physical events']['4']['loss to (n,xn)']
                    results['nucl_interaction5'] = datadic['physical events']['5']['nucl. interaction']
                    results['n_xn5'] = datadic['physical events']['5']['(n,xn)'] + datadic['physical events']['5']['loss to (n,xn)']
                    results['nucl_interaction6'] = datadic['physical events']['6']['nucl. interaction']
                    results['n_xn6'] = datadic['physical events']['6']['(n,xn)'] + datadic['physical events']['6']['loss to (n,xn)']
                    results['nucl_interaction7'] = datadic['physical events']['7']['nucl. interaction']
                    results['n_xn7'] = datadic['physical events']['7']['(n,xn)'] + datadic['physical events']['7']['loss to (n,xn)']
                    results['neutronyield'] = mtr.getNeutronYield(inp+'o')
                    
                    k_totrate = mtr.readNeutronActivity(inp+'o')
                    results['escape'] = k_totrate['escape'] # escape of kcode mode
                    if os.path.isfile(inp+'o'):
                        oldfilename = inp+'o'
                        newfilename = inp+'o_'+str(mm)+'_'+str(kk)+'_'+'{:.4f}'.format(matdict[nacl])\
                            +'_'+'{:.4f}'.format(matdict[pucl3])+'_'+'{:.4f}'.format(matdict[thcl4])
                        mh.deleteFiles(newfilename)
                        os.rename(oldfilename, newfilename)
                    mh.cleanup(inp)
                else:
                    print('error!!!,MCNP5 run failed!')
                    exit(0)
                

                results['nacl'] = matdict[nacl] # molar of nacl
                results['pucl3'] = matdict[pucl3]
                results['thcl4'] = matdict[thcl4]
                results['thickness'] = kk
                results['coresize'] = mm

                with open(resultfile, 'a') as fid:
                    fid.write("{coresize:^10} {thickness:^10} {nacl:^10.4f} {pucl3:^10.4f} {thcl4:^10.4f} {nucl_interaction4:^20.4f} {n_xn4:^20.4f} {nucl_interaction5:^20.4f} {n_xn5:^20.4f} {nucl_interaction6:^20.4f} {n_xn6:^20.4f} {nucl_interaction7:^20.4f} {n_xn7:^20.4f} {neutronyield:^20.4f} {escape:^20.4f}\n".format(**results))
                    