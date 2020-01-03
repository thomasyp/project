#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:15:47 2018

@author: Thomas Yang
"""

import os
import re
from tool.self_defined_exception import CustomError

class McnpinpHandler(object):
    CELL_SECTION = 0
    SURFACE_SECTION = 1
    DATA_SECTION = 2

    def __init__(self):
        pass

    def copyinp(self, inpname, newinpname):
        try:
            if inpname == newinpname:
                raise CustomError('The copied file and the the target file are same!')
        except TypeError as e:
            print(e)
            return -1
        with open(inpname, 'r') as fread, open(newinpname, 'w') as fwrite:
            for eachline in fread:
                fwrite.write(eachline)

    def readContent(self, inpname, designator, section='cell'):
        """
            Function: read content from  mcnp input card.
            Parameters:
                inpname: the name of mcnp input card which need to be modfied.
                designator: the designator in mcnp input, which indicate the part in mcnp input need to be
                read.
            Return:
                line: read context.
        """
        if section == 'cell':
            numsp = 0
        elif section == 'surface':
            numsp = 1
        elif section == 'data':
            numsp = 2
        else:
            self.errorMessage("section input error!")
            return -1
        with open(inpname, 'r', encoding="utf-8") as fid:
            content = fid.readlines()
        line = ''
        targetline = None
        numSeparator = 0
        for eachline in content:
            # empty line case
            if eachline.strip() == '':
                lists = line.strip().split()
                # if lists and lists[0] == str(designator) and numSeparator == numsp:
                if lists and re.match(str(designator), lists[0], re.I) and numSeparator == numsp:
                    targetline = line
                    return targetline
                else:
                    line = eachline
                numSeparator += 1
            # mcnp card start line case
            elif eachline[0] != ' ' and re.match(eachline.split()[0], 'c', re.I) is None:
                lists = line.strip().split()
                # if lists and lists[0] == str(designator) and numSeparator == numsp:
                if lists and re.match(str(designator), lists[0], re.I) and numSeparator == numsp:
                    targetline = line
                    return targetline
                else:
                    line = eachline
            # annotation line case
            elif eachline[0] != ' ' and re.match(eachline.split()[0], 'c', re.I) is not None:
                pass
            # mcnp card continuation line case
            else:
                line = line + eachline
        # end of the file case
        lists = line.strip().split()
        # if lists and lists[0] == str(designator) and numSeparator == numsp:
        if lists and re.match(str(designator), lists[0], re.I) and numSeparator == numsp:
            targetline = line
            return targetline    
        
        return targetline


    def readCellCards(self, inpname):
        """
            Function: read all cell cards from mcnp input.
            Parameters:
                inpname: the name of mcnp input card which need to be read.
                
            Return:
                lists: read context.
        """
        section = 0
        cellcards = []

        with open(inpname, 'r') as fid:
            for eachline in fid:
                # restrict in cell cards 
                lines = eachline.strip()
                if lines:
                    if section == McnpinpHandler.CELL_SECTION:
                        if eachline[0].isspace() is False:
                            if re.match(eachline.split()[0], 'c', re.I) is not None:
                                pass
                            else:
                                lists = eachline.strip().split()                                
                                cellcards.append(self.readContent(inpname, lists[0]))
                        
                else:
                    section += 1
                    
        return cellcards[1:]  # delete title


    def readSurfaceCards(self, inpname):
        """
            Function: read all surface cards from mcnp input.
            Parameters:
                inpname: the name of mcnp input card which need to be read.
                
            Return:
                lists: read context.
        """
        section = 0
        surfacecards = []

        with open(inpname, 'r') as fid:
            for eachline in fid:
                # restrict in surface cards 
                
                lines = eachline.strip()
                if lines:
                    if section == McnpinpHandler.SURFACE_SECTION:
                        if eachline[0].isspace() is False:
                            if re.match(eachline.split()[0], 'c', re.I) is not None:
                                pass
                            else:
                                lists = eachline.strip().split()                                
                                surfacecards.append(self.readContent(inpname, lists[0], section='surface'))
                        
                else:
                    section += 1
                    
        return surfacecards 


    def readDataCards(self, inpname):
        """
            Function: read all surface cards from mcnp input.
            Parameters:
                inpname: the name of mcnp input card which need to be read.
                
            Return:
                lists: read context.
        """
        section = 0
        datacards = []

        with open(inpname, 'r') as fid:
            for eachline in fid:
                # restrict in surface cards 
                
                lines = eachline.strip()
                if lines:
                    if section == McnpinpHandler.DATA_SECTION:
                        if eachline[0].isspace() is False:
                            if re.match(eachline.split()[0], 'c', re.I) is not None:
                                pass
                            else:
                                lists = eachline.strip().split()                                
                                datacards.append(self.readContent(inpname, lists[0], section='data'))
                        
                else:
                    section += 1
                    
        return datacards  
       

    def modifyinp(self, inpname, designator, modifiedline, section='cell'):
        """
            Function: modify mcnp input card by modifiedline.
            Parameters:
                inpname: the name of mcnp input card which need to be modfied.
                designator: the designator in mcnp input, which indicate the part in mcnp input need to be
                modifid.
                modifiedline: Modified content.
            Return:
                normalizecontent: none.

        """

        if section == 'cell':
            numsp = 0
        elif section == 'surface':
            numsp = 1
        elif section == 'data':
            numsp = 2
        else:
            self.errorMessage("section input error!")
            return -1
        with open(inpname, 'r', encoding="utf-8") as fid:
            content = fid.readlines()

        with open(inpname, 'w', encoding="utf-8") as f:
            line = ''
            numSeparator = 0
            for eachline in content:
                
                if eachline.strip() == '':

                    lists = line.strip().split()
                    if len(lists) !=0 and lists[0] == designator and numSeparator == numsp:
                        line = self.normalize(modifiedline)
                        f.write(line)
                        line = eachline
                    else:
                        f.write(line)
                        line = eachline
                    numSeparator += 1
                elif eachline[0] != ' ':
                    lists = line.strip().split()
                    if len(lists) !=0 and lists[0] == designator and numSeparator == numsp:
                        line = self.normalize(modifiedline)
                        f.write(line)
                        line = eachline
                    else:
                        f.write(line)
                        line = eachline
                else:
                    line = line + eachline
            f.write(line)

    def normalize(self, line):
        """
            Function: modify the format of the line, make sure it won't exceed 80 rows.
            Parameters:
                line: the content whos format need to be modfied.
            Return:
                normalizecontent: the content after modifed format.

        """
        eachlinelenthlimt = 75
        normalizecontent = ''
        fivespace = ' '*6
        lists = line.strip().split()
        lenth = len(lists)
        i = 0

        while(i < lenth):
            if i == 0:
                normalizeline = lists[i] + fivespace
            else:
                normalizeline = fivespace + lists[i]
            i = i + 1
            linelenth = 0
            while linelenth < eachlinelenthlimt and i < lenth:
                    if linelenth + len(lists[i]) > eachlinelenthlimt:
                        break
                    normalizeline =  normalizeline + ' ' + lists[i]
                    i = i + 1
                    linelenth = len(normalizeline)
            normalizecontent =  normalizecontent + normalizeline + '\n'

        return normalizecontent

    def deleteFiles(self, inp):
        if os.path.isfile(inp):
            os.remove(inp)

    def cleanup(self, inp):
        """
            Function: Clean up mcnp output file including 'out','runtpe' and 'srctp', 'meshtal'.
            Parameters: inp: the name of mcnp input file.
            Return: none

        """
        if os.path.isfile(inp+'s'):
            os.remove(inp+'s')
        if os.path.isfile(inp+'r'):
            os.remove(inp+'r')
        if os.path.isfile(inp+'o'):
            os.remove(inp+'o')
        if os.path.isfile(inp+'d'):
            os.remove(inp+'d')
        if os.path.isfile('meshtal'):
            os.remove('meshtal')

    def errorMessage(self, line):
        print('error:{}'.format(line))


if __name__ == "__main__":
    mh = McnpinpHandler()
    line = "560       18 -2.1 (465:452:-454) -466 -452 454 2002 2004 2030 2032 imp:n=4"
    mh.modifyinp('D:\\work\\mcnpwork\\lf1\\工程设计\\功率分布\\一维\\drop\\0000', '560', line)
    # line = mh.readContent('cor4.txt', '4')
    # print(line)
    # print(mh.readCellCards('na402'))
    # print(mh.readCellCards('na402'))
    # print(mh.readSurfaceCards('na402'))
    # print(mh.readDataCards('na402'))




