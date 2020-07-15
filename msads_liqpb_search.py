#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
from compoundcalculator.compound_density import Nuclide, Element, Compound, Material
from tool.handle_mcnpinp import McnpinpHandler
from tool.mcnp_reader import McnpTallyReader
import argparse
import os
import re
import numpy as np
from pathlib import Path, PurePath
import tool.polt_CR

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


def readVolume(filename):
    
    with open(filename, 'r') as fid:
        context = fid.readlines()
    context = [line for line in context if len(line.strip().split())==1]
    line = re.findall("                         \d\.\d{5}E[+-]\d{2}", ''.join(context))[0]
    volume = float(line)
    return volume


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

def changeMode(inp, mode):
    with open(inp, 'r', encoding="utf-8") as fid:
        content = fid.readlines()
    if mode == 'fixed':
        fixedSource = 'sdef  axs=0 0 1 pos=0 0 0 ext=d1 rad=d2  erg=d3 par=1\
            \nsi1    -10 10\nsp1   0   1\nsi2    0  10\nsp2    -21 1\nSI3   L  \
            0.151 0.248 0.410 0.675 1.11 1.84 3.03 4.99 19.64\nSP3      \
        0.0 5.45e-2 5.0e-2 8.0e-2 0.122 0.165 0.178 0.157 0.1985\nnps 50000\n'

        #for test
        # fixedSource = 'sdef  axs=0 0 1 pos=0 0 0 ext=d1 rad=d2  erg=d3 par=1\
        #     \nsi1    -10 10\nsp1   0   1\nsi2    0  10\nsp2    -21 1\nSI3   L  \
        #     0.151 0.248 0.410 0.675 1.11 1.84 3.03 4.99 19.64\nSP3      \
        # 0.0 5.45e-2 5.0e-2 8.0e-2 0.122 0.165 0.178 0.157 0.1985\nnps 50\n'
        with open(inp, 'w', encoding="utf-8") as f:
            for line in content:
                lists = line.strip().split()
                if lists and re.match('kcode', lists[0], re.I) is not None:
                    f.write(fixedSource)
                elif lists and re.match('ksrc', lists[0], re.I) is not None:
                    pass
                else:
                    f.write(line)
    if mode == 'kcode':
        kcodeSource = 'kcode    20000 1.0 30 250\nksrc   50. 0. 0. -50 0 0  -0 \
            0 0  0 0 20\n'
        #for test 
        # kcodeSource = 'kcode    200 1.0 5 50\nksrc   50. 0. 0. -50 0 0  -0 \
        #     0 0  0 0 20\n'
        with open(inp, 'w', encoding="utf-8") as f:
            for line in content:
                lists = line.strip().split()
                if lists and re.match('sdef', lists[0], re.I) is not None:
                    f.write(kcodeSource)
                elif lists and re.match('si|sp|sc|ds[0-9]{1,3}', lists[0], \
                                        re.I) is not None:
                    pass
                elif lists and re.match('nps', lists[0], re.I) is not None:
                    pass
                else:
                    f.write(line)



u235 = Nuclide('U235', 92, 235.043923)
u238 = Nuclide('U238', 92, 238.050783)
th232 = Nuclide('Th232', 90, 232.03805)
pu238 = Nuclide('Pu238', 94, 238.0)
pu239 = Nuclide('Pu239', 94, 239.0)
pu240 = Nuclide('Pu240', 94, 240.0)
pu241 = Nuclide('Pu241', 94, 241.0)
pu242 = Nuclide('Pu242', 94, 242.0)
f19 = Nuclide('F19', 9, 18.998403)
be9 = Nuclide('Be9', 4, 9.012182)
li6 = Nuclide('li6', 3, 9.012182)
li7 = Nuclide('li7', 3, 9.012182)
cl37 = Nuclide('cl37', 17, 36.965903)
mg24= Nuclide('mg24', 12, 23.985042)
mg25= Nuclide('mg25', 12, 24.985837)
mg26= Nuclide('mg26', 12, 25.982593)
na23 = Nuclide('na23', 11, 22.989770)
udict = {u235:0.1995, u238:0.8005}
fdict = {f19:1}
cldict = {cl37:1}
# Pu from MOX
pudict = {pu238:0.019497, pu239:0.5875682, pu240:0.2371, pu241:0.10133776, pu242:0.05449704}
mgdict = {mg24:0.7899, mg25:0.10, mg26:0.1101}
nadict = {na23:1}
cl = Element('Cl', cldict)
u = Element('U', udict)
f = Element("F", fdict)
th = Element("Th", {th232:1})
be = Element("Be", {be9:1})
pu = Element("Pu", pudict)
mg = Element("Mg", mgdict)
na = Element("Na", nadict)
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
parser=argparse.ArgumentParser(description='input file name, node and ppn')
parser.add_argument('-n',action="store",dest="node",type=int,default=1)
parser.add_argument('-p',action="store",dest="ppn",type=int,default=1)
parser.add_argument('inp',action="store",type=str)
args=parser.parse_args()
print('inputfile=%s' %args.inp,'ppn=%s' %args.ppn)
inp = args.inp
node = args.node
ppn = args.ppn
# inp = 'co25'
cardlist=['naclsets', 'puclsets', 'coresizesets', 'reflectorsets']

tallydic = {'1004':'94240', '1003':'94239', '1005':'94241', '1007':'90232', 
            '1016':'91233','1018':'92233', '1020':'92235', '1019':'92234', 
            '1023':'92238'}
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
with open(resultfile, 'w') as fid, open(seachoutfile, 'w') as fid2:
   fid.write("{:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^20} {:^20} {:^20} {:^20}\n"\
       .format('Core size', 'Thickness', 'Nacl', 'PuCl3', 'ThCl4', 'Keff',\
                              'CR of kcode', 'Escape of kcode', 'CR of fixed',\
                              'Escape of fixed'))
   fid2.write("{:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^20} {:^20} {:^20} {:^20}\n"\
       .format('Core size', 'Thickness', 'Nacl', 'PuCl3', 'ThCl4', 'Keff',\
                               'CR of kcode', 'Escape of kcode', 'CR of fixed',\
                               'Escape of fixed'))

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
                results['kCR'] = 0  # CR of kcode mode
                results['fCR'] = 0  # CR of fixed mode
                results['kescape'] = 0 # escape of kcode mode
                results['fescape'] = 0 # escape of fixed mode

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
                changeMode(inp, mode='kcode')
                # os.system('mcnp5'+ ' n=' + inp)
                os.system('mpirun -r ssh -np '+ str(int(node*ppn)) +' /home/daiye/bin/mcnp5.mpi n=' + inp)
                if os.path.isfile(inp+'o'):
                    print('MCNP5 run finished!')
                    results['keff'] = mtr.readKeff(inp+'o')['keff']
                    results['kCR'] = mtr.getCR(inp+'o')
                    k_totrate = mtr.readNeutronActivity(inp+'o')
                    results['kescape'] = k_totrate['escape']/(k_totrate['escape']\
                            +k_totrate['lossfission']+k_totrate['capture']) # escape of kcode mode
                    if os.path.isfile(inp+'o'):
                        oldfilename = inp+'o'
                        newfilename = inp+'ko_'+str(mm)+'_'+str(kk)+'_'+'{:.4f}'.format(matdict[nacl])\
                            +'_'+'{:.4f}'.format(matdict[pucl3])+'_'+'{:.4f}'.format(matdict[thcl4])
                        mh.deleteFiles(newfilename)
                        os.rename(oldfilename, newfilename)
                    mh.cleanup(inp)
                else:
                    print('error!!!,MCNP5 run failed!')
                    exit(0)
                if results['keff'] < 0.998:
                    changeMode(inp, mode='fixed')
                    # os.system('mcnp5'+ ' n=' + inp)
                    os.system('mpirun -r ssh -np '+ str(int(node*ppn)) +' /home/daiye/bin/mcnp5.mpi n=' + inp)
                    if os.path.isfile(inp+'o'):
                        print('MCNP5 run finished!')
                        volume = readVolume(inp+'o')
                        results['fCR'] = mtr.getCR(PurePath.joinpath(Path(os.getcwd()), inp+'o'),
                                                   mode='fixed', tallydic=tallydic, cell=4, 
                                                   matnum=1, volume=volume)
                        f_totrate = mtr.readNeutronActivity(inp+'o')
                        results['fescape'] = f_totrate['escape']/(f_totrate['escape']+f_totrate['lossfission']+f_totrate['capture'])
                    if os.path.isfile(inp+'o'):
                        oldfilename = inp+'o'
                        newfilename = inp+'fo_'+str(mm)+'_'+str(kk)+'_'+'{:.4f}'.format(matdict[nacl])+'_'+'{:.4f}'.format(matdict[pucl3])+'_'+'{:.4f}'.format(matdict[thcl4])
                        mh.deleteFiles(newfilename)
                        os.rename(oldfilename, newfilename)
                    mh.cleanup(inp)

                results['nacl'] = matdict[nacl] # molar of nacl
                results['pucl3'] = matdict[pucl3]
                results['thcl4'] = matdict[thcl4]
                results['thickness'] = kk
                results['coresize'] = mm

                
                with open(resultfile, 'a') as fid, open(seachoutfile, 'a') as fid2:
                    fid2.write("{coresize:^10} {thickness:^10} {nacl:^10.4f} {pucl3:^10.4f} {thcl4:^10.4f} {keff:^10} {kCR:^20.4f} {kescape:^20.4f} {fCR:^20.4f} {fescape:^20.4f}\n".format(**results))
                    if float(results['keff']) > 0.97 and float(results['keff'])<0.99:
                        fid.write("{coresize:^10} {thickness:^10} {nacl:^10.4f} {pucl3:^10.4f} {thcl4:^10.4f} {keff:^10} {kCR:^20.4f} {kescape:^20.4f} {fCR:^20.4f} {fescape:^20.4f}\n".format(**results))

