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


class ParameterProcesser(object):
    def __init__(self, parameters):
        self.parameters = parameters

    def getMcardContent(self):
        return self.parameters['mcardcontent']

    def getElementContent(self):
        elementcontent = {}
        for key, paralist in self.parameters.items():
            if len(key) < 3:
                elementcontent[key] = paralist
        return elementcontent
    
    def getCoresizeSets(self):
        return self.parameters['coresizesets']

    def getReflectorSets(self):
        return self.parameters['reflectorsets']
    
    def getCompoundSets(self, compoundname):
        for key in self.parameters.keys():
            if re.match(compoundname, key, re.I):
                return self.parameters[key]
        raise KeyError("No such compound sets: {:}".format(compoundname))



class MaterialProcesser(object):
    def __init__(self, parameters):
        self._nuclide_mass = {'U235': 235.043923, 'U238': 238.050783, 'Th232': 232.03805,
        'F19': 18.998403, 'Be9': 9.012182, 'li6': 9.012182, 'li7': 9.012182,
        'cl37': 36.965903, 'na23': 22.989770}
        self._atomnumber = {'Na': 11, 'U': 92, 'Pu': 94, 'Th': 90, 'F': 9, 'Be': 4,
        'Cl': 17, 'Li': 3}
        self._paraprocess = ParameterProcesser(parameters)
    
    def _getNuclideMass(self, nuclide):
        for nuclidename, mass in self._nuclide_mass.items():
            if re.fullmatch(nuclidename, nuclide, re.I):
                return mass
        mass, = re.findall('\d+', nuclide)
        return float(mass)

    def _getAtomNumber(self, elementname):
        for elementnamekey, atomnumber in self._atomnumber.items():
            if re.fullmatch(elementnamekey, elementname, re.I):
                return atomnumber
        raise ValueError("No such element: {:}!".format(elementname))

    def _createNuclide(self, elementname, massnumber):
        nuclidename = ''.join([elementname, str(massnumber)])
        return Nuclide(nuclidename, self._getAtomNumber(elementname),
         self._getNuclideMass(nuclidename))
    
    def _getCompoundRatio(self, elementration):
        
        ratiolist = re.findall('\d+', elementration)
        if ratiolist:
            ratio, = ratiolist
            return float(ratio)          
        return 1

    def _getElementName(self, elementration):
        ratiolist = re.findall('\d+', elementration)
        if ratiolist:
            return elementration[:-1]          
        return elementration
            
    def getNuclideDict(self, elementname, nuclidelist):
        nuclidedic = {}
        for ii in range(0, len(nuclidelist), 2):
            nuclidedic[self._createNuclide(elementname, nuclidelist[ii])] = nuclidelist[ii+1]
        return nuclidedic


    def createElement(self, elementname):
        elementcontent = self._paraprocess.getElementContent()
        for element, nuclidecompositon in elementcontent.items():
            if re.fullmatch(elementname, element, re.I):
                nuclidedic = self.getNuclideDict(elementname, nuclidecompositon)
        element = Element(elementname, nuclidedic)
        return element

    def getElementDict(self, elementlist):
        elementdic = {}
        for ii in range(len(elementlist)):
            elementdic[self.createElement(self._getElementName(elementlist[ii]))] \
                = self._getCompoundRatio(elementlist[ii])
        return elementdic

    def createCompound(self, compoundname):
        mcard = self._paraprocess.getMcardContent()
        for ii in range(1, len(mcard[1:]), 3):
            elementlist = mcard[ii].split('_')
            if re.fullmatch(compoundname, ''.join(elementlist), re.I):
                para_a = float(mcard[ii+1])
                para_b = float(mcard[ii+2])
                compound = Compound(compoundname, self.getElementDict(elementlist), para_a, para_b)
        return compound

    def getCompoundDict(self):
        mcard = self._paraprocess.getMcardContent()
        compounddic = {}
        for ii in range(1, len(mcard[1:]), 3):
            elementlist = mcard[ii].split('_')
            para_a = float(mcard[ii+1])
            para_b = float(mcard[ii+2])
            compoundname = ''.join(elementlist)
            compounddic[Compound(compoundname, 
            self.getElementDict(elementlist), para_a, para_b)] = 1
        return compounddic

    def setCompoundDict(self, compounddic, compoundname, ratio):
        for key in compounddic:
            if re.fullmatch(key.getLabel(), compoundname, re.I):
                compounddic[key] = ratio
                return compounddic
        raise KeyError("No such compound: {:}".format(compoundname))
        

class Preprocesser(object):
    def __init__(self):
        self._cardlist=['Naclsets', 'Pucl3sets', 'coresizesets', 'reflectorsets', 
        'Thcl4sets', 'Ucl3sets', 'Ucl4sets', 'Na', 'Cl', 'U', 'Th']
        self.mcnpinphandler = McnpinpHandler()

    def getParameter(self, mcnpinp, materialcard):
        
        paralists = []
        newcardlist = []
        for card in self._cardlist:
            line = self.mcnpinphandler.readContent(mcnpinp, card, section='data')
            if line:
                lists = line.strip().split()
                newcardlist.append(card)
                paralists.append([int(x) if type(eval(x))==int else float(x) for x in lists[1:]])

        parameter = {card: para for card, para in zip(newcardlist, paralists)}
        line = self.mcnpinphandler.readContent(mcnpinp, materialcard, section='data')
        linelist = line.strip().split()
        parameter['mcardcontent'] = linelist
        return parameter
    
    def copyInitalMcnpinp(self, initalinp, mcnpinp):
        with open(initalinp, 'r') as fid1, open(mcnpinp, 'w') as fid2:
            for line in fid1:
                fid2.write(line)
   
    def deleteNonMcnpCard(self, mcnpinp):
        shadow = False
        with open(mcnpinp, 'r') as fid, open(mcnpinp+'bp', 'w') as fid2:
            for line in fid:
                shadow = False
                lists = line.strip().split()
                if bool(lists):
                    for card in self._cardlist:
                        if re.fullmatch(card, lists[0], re.I) is not None:
                            shadow = True
                            break
                if not shadow:
                    fid2.write(line)
        os.remove(mcnpinp)
        os.rename(mcnpinp+'bp', mcnpinp)

    def cleanupFolder(self, mcnpinp):
        self.mcnpinphandler.cleanup(mcnpinp)

    def modfiyMaterial(self, mcnpinp, cellnum, newdensity, mcard, newmcardcontent):
        line = self.mcnpinphandler.readContent(mcnpinp, cellnum)
        newline = line.replace(line.strip().split()[2], '-{:.5f}'.format(newdensity))
        self.mcnpinphandler.modifyinp(mcnpinp, cellnum, newline)
        self.mcnpinphandler.modifyinp(mcnpinp, mcard, newmcardcontent, 'data')

    def changeMode(self, mcnpinp, mode, test=False):
        with open(mcnpinp, 'r', encoding="utf-8") as fid:
            content = fid.readlines()
        if test:
            fixedSource = 'sdef  axs=0 0 1 pos=0 0 0 ext=d1 rad=d2  erg=d3 par=1\
                \nsi1    -10 10\nsp1   0   1\nsi2    0  10\nsp2    -21 1\nSI3   L  \
                0.151 0.248 0.410 0.675 1.11 1.84 3.03 4.99 19.64\nSP3      \
            0.0 5.45e-2 5.0e-2 8.0e-2 0.122 0.165 0.178 0.157 0.1985\nnps 50\n'    
            kcodeSource = 'kcode    200 1.0 5 50\nksrc   50. 0. 0. -50 0 0  -0 \
                    0 0  0 0 20\n'
        else:
            fixedSource = 'sdef  axs=0 0 1 pos=0 0 0 ext=d1 rad=d2  erg=d3 par=1\
                    \nsi1    -10 10\nsp1   0   1\nsi2    0  10\nsp2    -21 1\nSI3   L  \
                    0.151 0.248 0.410 0.675 1.11 1.84 3.03 4.99 19.64\nSP3      \
                0.0 5.45e-2 5.0e-2 8.0e-2 0.122 0.165 0.178 0.157 0.1985\nnps 50000\n'
            kcodeSource = 'kcode    20000 1.0 30 250\nksrc   50. 0. 0. -50 0 0  -0 \
                    0 0  0 0 20\n'

        if re.fullmatch('fixed', mode, re.I):
            
            with open(mcnpinp, 'w', encoding="utf-8") as f:
                for line in content:
                    lists = line.strip().split()
                    if lists and re.fullmatch('kcode', lists[0], re.I) is not None:
                        f.write(fixedSource)
                    elif lists and re.fullmatch('ksrc', lists[0], re.I) is not None:
                        pass
                    else:
                        f.write(line)
        elif re.fullmatch('kcode', mode, re.I):
            with open(mcnpinp, 'w', encoding="utf-8") as f:
                for line in content:
                    lists = line.strip().split()
                    if lists and re.fullmatch('sdef', lists[0], re.I) is not None:
                        f.write(kcodeSource)
                    elif lists and re.fullmatch('si|sp|sc|ds[0-9]{1,3}', lists[0], \
                                            re.I) is not None:
                        pass
                    elif lists and re.fullmatch('nps', lists[0], re.I) is not None:
                        pass
                    else:
                        f.write(line) 
        else:
            raise NameError('No such mode!')

    def changeMcnpLine(self, inp, increment, designator, section='cell'):
        line = self.mcnpinphandler.readContent(inp, designator, section)
        data = line.strip().split()[2]
        if float(data) > 0:
            replacedata = str(float(data)+increment)
        else:
            replacedata = str(float(data)-increment)
        newline = line.replace(data, replacedata)
        self.mcnpinphandler.modifyinp(inp, designator, newline, section)


class Postprocesser(object):
    def __init__(self):
        self.mcnptallyreader = McnpTallyReader()
        self.mcnpinphandler = McnpinpHandler()

    def outputResults(self, filename, content, writeingmode='a'):
        with open(filename, writeingmode) as fid:
            fid.write(content)

    def renameFile(self, oldfilename, newfilename):
        self.mcnpinphandler.deleteFiles(newfilename)
        os.rename(oldfilename, newfilename)

    def readVolume(self, filename):
        volume = None
        with open(filename, 'r') as fid:
            context = fid.readlines()
        context = [line for line in context if len(line.strip().split())==1]
        line = re.findall("                         \d\.\d{5}E[+-]\d{2}", ''.join(context))[0]
        volume = float(line)
        return volume

    def getKeff(self, mcnpout):
        if os.path.isfile(mcnpout):
            print('MCNP5 run finished!')
            return self.mcnptallyreader.readKeff(mcnpout)['keff']
        else:
            raise FileNotFoundError('No such file: {:}!'.format(mcnpout))

    def getEscape(self, mcnpout, mode='fixed'):
        if os.path.isfile(mcnpout):
            print('MCNP5 run finished!')
            if re.fullmatch('kcode', mode, re.I):
                k_totrate = self.mcnptallyreader.readNeutronActivity(mcnpout)
                escaperate = k_totrate['escape']/(k_totrate['escape']\
                        +k_totrate['lossfission']+k_totrate['capture'])
            elif re.fullmatch('fixed', mode, re.I):
                f_totrate = self.mcnptallyreader.readNeutronActivity(mcnpout)
                escaperate = f_totrate['escape']/(f_totrate['escape']
                                                  +f_totrate['lossfission']
                                                  +f_totrate['capture'])
            else:
                raise NameError('No such mode: {:}'.format(mode))
            return escaperate# escape of kcode mode
    
        else:
            raise FileNotFoundError('No such file: {:}'.format(mcnpout))

    def getCR(self, mcnpout, mode='kcode', tallydic=None, cell=None, matnum=None):
        if os.path.isfile(mcnpout):
            print('MCNP5 run finished!')
            if re.fullmatch('kcode', mode, re.I):
                cr = self.mcnptallyreader.getCR(mcnpout)
            elif re.fullmatch('fixed', mode, re.I):
                cr = self.mcnptallyreader.getCR(
                    PurePath.joinpath(Path(os.getcwd()), mcnpout),
                    mode='fixed', tallydic=tallydic, cell=cell, 
                    matnum=matnum, volume=self.readVolume(mcnpout))
            else:
                raise NameError('No such mode: {:}'.format(mode))
            return cr# escape of kcode mode
    
        else:
            raise FileNotFoundError('No such file: {:}'.format(mcnpout))

    

class Calculator(object):
    def __init__(self, mcnpinp):
        self.mcnpinp = mcnpinp

    def run(self, environment='server', node=16, ppn=1):
        if environment == 'server':
            os.system('mpirun -r ssh -np '+ str(int(node*ppn)) +' /home/daiye/bin/mcnp5.mpi n=' + self.mcnpinp)
        else:
            os.system('mcnp5'+ ' n=' + self.mcnpinp)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='input file name, node and ppn')
    parser.add_argument('-n',action="store",dest="node",type=int,default=1)
    parser.add_argument('-p',action="store",dest="ppn",type=int,default=1)
    parser.add_argument('inp',action="store",type=str)
    args=parser.parse_args()
    print('inputfile=%s' %args.inp,'ppn=%s' %args.ppn)
    initalMcnpinp = args.inp
    node = args.node
    ppn = args.ppn
    tallydic = {'1004':'94240', '1003':'94239', '1005':'94241', '1007':'90232', 
                '1016':'91233', '1018':'92233', '1020':'92235', '1019':'92234', 
                '1023':'92238'}
    cell = 4
    matnum = 1
    # perprossing************************
    perpross = Preprocesser()
    # initalMcnpinp = 'r150'
    mcnpinp = 'r150r'
    ## read parameters in mcnpinp
    parameters = perpross.getParameter(initalMcnpinp, 'm1')
    print(parameters)
    ## material processing
    matproc = MaterialProcesser(parameters)
    compounddic = matproc.getCompoundDict()

    paraprocess = ParameterProcesser(parameters)
    endreflectorThickness = paraprocess.getReflectorSets()[0]
    thicknessStep = paraprocess.getReflectorSets()[1]
    endCoreSize = paraprocess.getCoresizeSets()[0]
    coreSizeStep = paraprocess.getCoresizeSets()[1]

    compoundsets = {}
    for compound in compounddic:
        compoundname = compound.getLabel()
        try:
            compoundsets[compoundname] = (paraprocess.getCompoundSets(compoundname))
        except KeyError as e:
            print('Warning: {:}'.format(e.args))
    print(compoundsets)

    for key in compoundsets:
        if re.fullmatch('nacl', key, re.I):
            startmolnacl = compoundsets[key][0]
            endmolnacl = compoundsets[key][1]
            stepmolnacl = compoundsets[key][2]
        else:
            startmolchloridefuel = compoundsets[key][0]
            endmolchloridefuel = compoundsets[key][1]
            stepmolchloridefuel = compoundsets[key][2]
            chloridefuelname = key

    resultfile = mcnpinp + 'results.out'
    seachoutfile = mcnpinp + 'search.out'

    postpross = Postprocesser()
    content = "{:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^20} {:^20} {:^20} {:^20}\n"\
        .format('Core size', 'Thickness', 'Nacl', 'fuel compd', 'ThCl4', 'Keff',\
                                'CR of kcode', 'Escape of kcode', 'CR of fixed',\
                                'Escape of fixed')
    postpross.outputResults(resultfile, content, 'w')
    postpross.outputResults(seachoutfile, content, 'w')

    results = {}
    for coreincrement in range(0, endCoreSize, coreSizeStep):
        for reflectorincrement in range(0, endreflectorThickness, thicknessStep):
            for ii in np.arange(startmolnacl, endmolnacl, stepmolnacl):
                compounddic = matproc.setCompoundDict(compounddic, 'nacl', ii)
            # loop for pucl
                for jj in np.arange(startmolchloridefuel, endmolchloridefuel, stepmolchloridefuel):
                    # if jj > startmolchloridefuel:
                    #     continue 
                    compounddic = matproc.setCompoundDict(compounddic, chloridefuelname, jj)
                    compounddic = matproc.setCompoundDict(compounddic, 'thcl4', 100 - ii - jj)
                    mat = Material('mat1', compounddic, 900)

                    perpross.copyInitalMcnpinp(initalMcnpinp, mcnpinp)
                    perpross.deleteNonMcnpCard(mcnpinp)
                    perpross.changeMode(mcnpinp, 'kcode', True)
                    perpross.cleanupFolder(mcnpinp)
                    perpross.modfiyMaterial(mcnpinp, '4', mat.getDensity(), 
                    'm1', 'm1     '+mat.toMcnpCard())

                    perpross.changeMcnpLine(mcnpinp, coreincrement, '2', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '13', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '14', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '15', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '16', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '17', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '18', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '19', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '20', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '21', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '22', 'surface')
                    perpross.changeMcnpLine(mcnpinp, coreincrement, '23', 'surface')

                    perpross.changeMcnpLine(mcnpinp, reflectorincrement, '18', 'surface')
                    perpross.changeMcnpLine(mcnpinp, reflectorincrement, '19', 'surface')
                    perpross.changeMcnpLine(mcnpinp, reflectorincrement, '20', 'surface')
                    perpross.changeMcnpLine(mcnpinp, reflectorincrement, '21', 'surface')
                    perpross.changeMcnpLine(mcnpinp, reflectorincrement, '22', 'surface')
                    perpross.changeMcnpLine(mcnpinp, reflectorincrement, '23', 'surface')

                    results['kCR'] = 0  # CR of kcode mode
                    results['fCR'] = 0  # CR of fixed mode
                    results['kescape'] = 0 # escape of kcode mode
                    results['fescape'] = 0 # escape of fixed mode

                    calculater = Calculator(mcnpinp)
                    calculater.run()
                    results['keff'] = postpross.getKeff(mcnpinp+'o')
                    results['kCR'] = postpross.getCR(mcnpinp+'o')
                    results['kescape'] = postpross.getEscape(mcnpinp+'o', mode='kcode')
                    newfilename = mcnpinp+'ko_'+str(coreincrement)+'_'+str(reflectorincrement)+'_'+'{:.4f}'.format(ii)\
                             +'_'+'{:.4f}'.format(jj)+'_'+'{:.4f}'.format(100-ii-jj)
                    postpross.renameFile(mcnpinp+'o', newfilename)

                    perpross.cleanupFolder(mcnpinp)
                    if results['keff'] < 0.998:
                        perpross.changeMode(mcnpinp, 'fixed', True)
                        calculater.run()
                        results['fCR'] = postpross.getCR(mcnpinp+'o', mode='fixed', 
                        tallydic=tallydic, cell=cell, matnum=matnum)
                        results['fescape'] = postpross.getEscape(mcnpinp+'o', mode='fixed')
                        newfilename = mcnpinp+'fo_'+str(coreincrement)+'_'+str(reflectorincrement)+'_'+'{:.4f}'.format(ii)\
                             +'_'+'{:.4f}'.format(jj)+'_'+'{:.4f}'.format(100-ii-jj)
                        postpross.renameFile(mcnpinp+'o', newfilename)

                    results['nacl'] = ii # molar of nacl
                    results['fuel'] = jj
                    results['thcl4'] = 100-ii-jj
                    results['thickness'] = reflectorincrement
                    results['coresize'] = coreincrement
                    outputcontent = "{coresize:^10} {thickness:^10} {nacl:^10.4f} {fuel:^10.4f} {thcl4:^10.4f} {keff:^10} {kCR:^20.4f} {kescape:^20.4f} {fCR:^20.4f} {fescape:^20.4f}\n"\
                        .format(**results)
                    postpross.outputResults(resultfile, outputcontent, 'a')
                    if float(results['keff']) > 0.97 and float(results['keff'])<0.99:
                        postpross.outputResults(seachoutfile, outputcontent, 'a')

