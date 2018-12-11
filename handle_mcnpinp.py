#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:15:47 2018

@author: Thomas Yang
"""

import os

class McnpinpHandler(object):
    def __init__(self):
        pass
    
    def readContent(self, inpname, designator):
        """
            Function: read content from  mcnp input card.
            Parameters: 
                inpname: the name of mcnp input card which need to be modfied. 
                designator: the designator in mcnp input, which indicate the part in mcnp input need to be
                read.
            Return: 
                line: read context.
        
        """
        with open(inpname, 'r', encoding="utf-8") as fid:
            content = fid.readlines()
        line = ''
        for eachline in content:
            if eachline.strip() == '':
                line = eachline
            elif eachline[0] != ' ':
                lists = line.strip().split()
                if len(lists) !=0 and lists[0] == designator:
                    return line
                else:
                    line = eachline
            else:
                line = line + eachline
        return line
        

    def modifyinp(self, inpname, designator, modifiedline):
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
        with open(inpname, 'r', encoding="utf-8") as fid:
            content = fid.readlines()
            
        with open(inpname, 'w', encoding="utf-8") as f:
            line = ''
            for eachline in content:
                if eachline.strip() == '':
                    f.write(line)
                    line = eachline
                elif eachline[0] != ' ':
                    lists = line.strip().split()
                    if len(lists) !=0 and lists[0] == designator:
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
        if os.path.isfile('meshtal'):
            os.remove('meshtal')

if __name__ == "__main__":
    mh = McnpinpHandler()
    # line = "502       18 -2.1 (465:452:-454) -466 -452 454 2002 2004 2030 2032 2036 2038\
    #   2040 2042 2044 2046 2048 2050 2052 2054 2056 imp:n=4 502 18 -2.1\
    #   (465:452:-454) -466 -452 454 2002 2004 2030 2032 2036 2038 2040 2042\
    #   2044 2046 2048 2050 2052 2054 2056 imp:n=4 502 18 -2.1"
    # mh.modifyinp('0000.txt', '1', line)
    line = mh.readContent('0000.txt', '32')
    print(line)
    


        