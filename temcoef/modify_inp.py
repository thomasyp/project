'''
Created on 2015/9/29

@author: thomas
'''

from tool.handle_mcnpinp import McnpinpHandler
from tool.mcnp_reader import McnpTallyReader
import mcnp_lib
import operator
import os
import shutil
import sys


class InpChecker(object):
    def __init__(self):

    def hasMtnumIninp(self, inpfile, matnum):
        mh = McnpinpHandler()
        cellcards = mh.readCellCards(inpfile)

        matincellcard = []
        for line in cellcards:
            lists = line.strip().split()
            matincellcard.append(lists[1])
        for mat in matnum:
            if mat not in matincellcard:
                mh.errorMessage(' material number {:} do not exists!\n'.format(mat))
                return False

        return True

    def findTMP(self, inp, designator):
        mh = McnpinpHandler()
        mcnpcontent = mh.readContent(inp, designator)

        if '$' in mcnpcontent:
            mcnpcontent = mcnpcontent[:mcnpcontent.find('$')]
        if mcnpcontent.find('tmp') > 0 or mcnpcontent.find('TMP') > 0:
            return True
        else:
            return False

    def readTMP(self, inp, designator):
        mh = McnpinpHandler()
        mcnpcontent = mh.readContent(inp, designator)
        if '$' in mcnpcontent:
            mcnpcontent = mcnpcontent[:mcnpcontent.find('$')]

        inplist = mcnpcontent.strip().split()
        tmp = None
        for ii, eachstr in enumerate(inplist):
            if 'tmp' in eachstr or 'TMP' in eachstr:
                tmp = float(inplist[ii][4:])

        return tmp

    def isTMPIdentical(self, filename, workpath=None):
        inpfile = filename
        tmpdic = {}
        if workpath:
            inpfile = os.path.join(workpath, filename)
        mh = McnpinpHandler()
        cellcards = mh.readCellCards(inpfile)
        for line in cellcards:
            lists = line.strip().split()
            mat = lists[1]
            if mat not in tmpdic.keys():
                tmpdic[mat] = []
            for ii, eachstr in enumerate(lists):
                if 'tmp' in eachstr or 'TMP' in eachstr:
                    tmp = lists[ii][4:]
                    tmpdic[mat].append(tmp)

        for key, tmps in tmpdic.items():
            if len(set(tmps)) > 1:
                mh.errorMessage('The TMP card of material {:} is inconsistent!\n'.format(key))
                return False

        return True

    def isTemEqMtnum(self, filename, workpath=None):

        inpfile = filename
        if workpath:
            inpfile = os.path.join(workpath, filename)
        mh = McnpinpHandler()
        cellcards = mh.readCellCards(inpfile)
        tmpnum = 0
        matnum = 0

        for cellcard in cellcards:
            if '$' in cellcard:
                cellcard = cellcard[:cellcard.find('$')]
            if cellcard.find('tmp')>0 or cellcard.find('TMP')>0:
                tmpnum += 1
            if cellcard.strip().split()[1] != '0':
                matnum += 1
        if tmpnum == matnum:
            print ('matnum is ', matnum, ' tmpnum is ', tmpnum)
            return True
        else:
            print ('matnum is ', matnum, ' tmpnum is ', tmpnum)
            print ('The number of tmp and the number of  material are not  identical !')
            return False

    def checkInput(self, filename, matnum, workpath=None):

        inpfile = filename
        if workpath:
            inpfile = os.path.join(workpath, filename)

        if self.isTemEqMtnum(inpfile, workpath) is False:
            return False

        if self.hasMtnumIninp(inpfile, matnum) is False:
            return False

        if self.isTMPIdentical(inpfile) is False:
            return False

        return True


class InpModifier(object):
    def __init__(self):
        pass

    def modify(self, inp, matnums, mdinp):



class mkCardofCoeffient(object):
    def __init__(self,filename,workpath,delttemperture,matnum,densmatnum,typeofcoef,expancoeff=0):
        self.delttemp = delttemperture
        self.matnum = matnum
        self.densmatnum = densmatnum
        self.filename = filename
        self.workpath = workpath
        self.typeofcoef = typeofcoef
        self.neednextline = False
        self.findmt = False
        self.expancoeff = expancoeff
        self.temp = {}
        for tt in self.matnum:
            self.temp[tt] = 0
        self.tag = ' '

    def chWorkdir(self):
        if os.path.exists(os.path.join(self.workpath, self.typeofcoef)):
            os.chdir(os.path.join(self.workpath, self.typeofcoef))
        else:
            print ('no ',os.path.join(self.workpath,self.typeofcoef),' can not change directory!')

    def findTMP(self, eachline):
        if eachline.find('tmp')>0 or eachline.find('TMP')>0:
            return True
        else:
            return False

    def tmphasMtnumInLine(self, testlist):
        mm = 0
        while(mm<len(self.matnum)):
            if operator.eq(testlist[1],self.matnum[mm]):
                matnum = self.matnum[mm]
                return True,matnum
            else:
                mm = mm + 1
        return False,0
        mm = 0
        while(mm<len(self.densmatnum)):
            # if not cmp(testlist[1],self.densmatnum[mm]):
            if operator.eq(testlist[1],self.densmatnum[mm]):
                matnum = self.densmatnum[mm]
                return True,matnum
            else:
                mm = mm + 1
        return False,0

    def mthasMtnumInLine(self, matnum, testlist):
        mm = 0
        while(mm<len(self.matnum)):
            if operator.eq(matnum,self.matnum[mm]):
                matnum = self.matnum[mm]
                self.tag = matnum
                return True,matnum
            else:
                mm = mm + 1
        return False,0

    def replacemt(self, temp):

        return mcnp_lib.chooselib(temp)

    def changeTMP(self, eachline):
        inplist = eachline.strip().split()
        if eachline[0].isdigit():
            trueofnot = self.tmphasMtnumInLine(inplist)
            if trueofnot[0] is True:
                self.tag = trueofnot[1]
                if self.findTMP(eachline):
                    for ii,eachstr in enumerate(inplist):
                        if 'tmp' in eachstr or 'TMP' in eachstr:
                            self.temp[self.tag] = float(inplist[ii][4:])/8.617e-11 + self.delttemp
                            new_tmp = 'tmp='+ str(float(inplist[ii][4:]) + 8.617e-11 * self.delttemp)
                            eachline = eachline.replace(inplist[ii],new_tmp,1)
                    self.neednextline = False
                    return eachline

                else:
                    self.neednextline = True
                    return eachline
            else:
                self.neednextline = False
                return eachline
        elif eachline[0].isspace() is True:
            if self.neednextline is True and self.tag.isspace() is False:
                if self.findTMP(eachline):
                    for ii,eachstr in enumerate(inplist):
                        if 'tmp' in eachstr or 'TMP' in eachstr:
                            self.temp[self.tag] = float(inplist[ii][4:])/8.617e-11 + self.delttemp
                            new_tmp = 'tmp='+ str(float(inplist[ii][4:]) + 8.617e-11 * self.delttemp)
                            eachline = eachline.replace(inplist[ii],new_tmp,1)
                    self.neednextline = False
                    return eachline

                else:
                    self.neednextline = True
                    return eachline
            else:
                self.neednextline = False
                return eachline

        else:
            self.neednextline = False
            return eachline


    def changeMT(self, eachline):
        inplist = eachline.strip().split()
        if eachline[0] =='m' or eachline[0] =='M':
            if inplist[0][1] == 't' or inplist[0][1] == 'T':
                matnum = inplist[0][2:]
            else:
                matnum = inplist[0][1:]
            trueofnot = self.mthasMtnumInLine(matnum, inplist)
            if trueofnot[0] is True:
                mtnum = trueofnot[1]
                self.tag = mtnum
                for ii in range(len(inplist)):
                    index = (inplist[ii].find('c') or inplist[ii].find('C'))
                    if index != -1:
                        ind = inplist[ii].find('.')
                        ss = inplist[ii][0:ind+1] + self.replacemt(self.temp[mtnum])[0]
                        eachline = eachline.replace(inplist[ii],ss)
                    index = inplist[ii].find('t')
                    if index != -1 and ii != 0:
                        ind = inplist[ii].find('.')
                        ss = inplist[ii][0:ind+1] + self.replacemt(self.temp[mtnum])[1]
                        eachline = eachline.replace(inplist[ii],ss)
                self.findmt = True
                return eachline
            else:
                self.findmt = False
                return eachline
        elif eachline[0].isspace() is True:
            if self.findmt is True:
                for ii in range(len(inplist)):
                    index = inplist[ii].find('c')
                    if index != -1:
                        ind = inplist[ii].find('.')
                        ss = inplist[ii][0:ind+1] + self.replacemt(self.temp[self.tag])[0]
                        eachline = eachline.replace(inplist[ii],ss)
                    index = inplist[ii].find('t')
                    if index != -1:
                        ind = inplist[ii].find('.')
                        ss = inplist[ii][0:ind+1] + self.replacemt(self.temp[self.tag])[1]
                        eachline = eachline.replace(inplist[0],ss)
                return eachline
            else:
                return eachline
        else:
            self.findmt = False
            return eachline

        return eachline


    def changeDesity(self, eachline):
        inplist = eachline.strip().split()
        if eachline[0].isdigit():
            trueofnot = self.denshasMtnumInLine(inplist)
            if trueofnot[0] is True:
                dens = float(inplist[2][1:]) + self.expancoeff * self.delttemp
                eachline = eachline.replace(inplist[2][1:],str(dens))
                return eachline
            else:
                return eachline
        else:
            return eachline

    def changeCardforRun(self, filename):

        with open('inp0','r') as fobjr, open(filename,'w') as fobjw:
            n_line = 0
            n_emptyline = 0
            for eachline in fobjr:
                if n_line > 0 or n_emptyline >0:
                    if eachline[0] == 'c' or eachline[0] == 'C':
                        continue
                if '$' in eachline:
                    eachline = eachline[:eachline.find('$')] + eachline[-1]
                if eachline.isspace():
                    n_emptyline += 1
                n_line += 1
                if n_line == 1:
                    fobjw.write(eachline)
                else:
                    if n_emptyline == 0:
                        eachline = self.changeDesity(eachline)
                        fobjw.write(self.changeTMP(eachline))
                    elif n_emptyline == 2:
                        fobjw.write(self.changeMT(eachline))
                    else:
                        fobjw.write(eachline)

        print (self.temp )

    def cpFile(self):
        if os.path.exists(os.path.join(self.workpath,self.filename)):
            targetdir = os.path.join(self.workpath,self.typeofcoef)
            targetfile = os.path.join(targetdir,'inp0')
            sourefile = os.path.join(self.workpath, self.filename)
            if os.path.exists(targetdir):
                pass
            else:
                os.mkdir(targetdir)

            if os.path.exists(targetfile):
                os.remove(targetfile)
                shutil.copy(sourefile, targetfile)
                print ('copy input to ' ,targetfile)
            #    return True
            else:
                shutil.copy(sourefile, targetfile)
                print ('copy input to ' ,targetfile)
             #   return True


if __name__ == "__main__":
    ick = InpChecker()
    mat = ['1', '3']
    print(ick.checkInput('na402', mat))


