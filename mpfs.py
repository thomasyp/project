#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:15:47 2018
Main program for calculating maximum power peak factor of 
rod withdrawal accident and rod drop accident.

Description of control rod:
Two shim rod: tr3 for 3# rod; tr5 for 5# rod.
One regulating rod: tr6 for 11# rod.
One Scram Rod: tr1 for 1# rod.

Notice:
The rodInsertpostion in the program is not the real insert 
postion, the variable actually equal tothe 180 - insert postion.

@author: Thomas Yang
"""

from tool.handle_mcnpinp import McnpinpHandler 
from control_rod import ControlRod
import os
from powerdistribution import computePowerDesityDistribution
import argparse
import re

def getMeshFilename(outputfile):
    with open(outputfile, 'r') as fid:
        for line in fid:
            if 'Mesh tallies written to file' in line:
                mesh_filename = line.strip().split()[-1]
                return mesh_filename
    return None

def readKeff(inp):
    """
        Function: Read keff,dev and average Num of neutron per Fissionor from mcnp output file.
        Parameters: 
            inp: the name of mcnp output file.
        Return: kef,dev,averageNumNperFission
    
    """

    with open(inp,'r') as f:
        for line in f:
            if 'final estimated' in line:
                kef = float(line.split()[8])
                dev = float(line.split()[15])
            if 'the average number of neutrons produced per fission' in line:
                averageNumNperFission = float(line.strip().split()[-2])
    return kef,dev,averageNumNperFission

def maxPowerPeakFactorSearch(mcnpinp, node, ppn, trforrod, mode, rodstep=10):
    """
        Function: under different rod position, compute the power distribution, power peak factor and find the 
        maximum power peak factor, finally write all results to a filename of inp+'results.out'.
        Parameters: 
            inp: the name of mcnp output file.
            node: the node for parallel computing.
            ppn: the core for parallel computing.
            trforrod: dict for rod, key is 'tr' card, value is rod num.
            mode: mode for rod withdrawal accident or rod drop accident, 'w' stands for withdrawal and
            'd' stands for drop.
            rodstep: rod move step everytime.
        Return: none
    
    """
    cr = {}
    rodlists = {}
    powerfactorresults = {}
    mh = McnpinpHandler()
    # read initial rod position of burnup mcnp input
    for key, value in trforrod.items():
        rodmessage = mh.readContent(mcnpinp, key, 'data')
        lists = rodmessage.strip().split()
        rodxcoordinate = float(lists[1])
        rodycoordinate = float(lists[2])
        rodinsertpostion = float(lists[3])
        cr[value] = ControlRod(rod=value, trCard=key, rodRange=180.0, rodXCoordinate=rodxcoordinate, rodYCoordinate=rodycoordinate)
        cr[value].setInsertPosition(rodinsertpostion)
        rodlists[value] = key
        powerfactorresults[value] = []
    print(rodlists)
    print(powerfactorresults)
    mh.cleanup(mcnpinp)
    if re.match('w', mode, re.I) is not None:
        limit = 180.
        factor = 1
    elif re.match('d', mode, re.I) is not None:
        limit = 0
        factor = -1
    else:
        print("Mode set error! Should be w or d!")
        exit(0)

    for rod in rodlists:
        ii = 0
        initinsertposition = cr[rod].getInsertPosition()
        while(cr[rod].getInsertPosition()*factor < limit):
            instertposition = initinsertposition + rodstep*ii*factor
            if instertposition*factor > limit:
                instertposition = limit
            cr[rod].setInsertPosition(instertposition)
            ### modify mcnp inp
            mh.modifyinp(mcnpinp, cr[rod].getTrCardNo(), cr[rod].ouputforMcnpinp(), 'data')
            ii = ii + 1
            ### run mcnp
            print('  mpirun -r ssh -np '+str(int(node*ppn))+' /home/daiye/bin/mcnp5.mpi n='+mcnpinp)
            os.system('  mpirun -r ssh -np '+str(int(node*ppn))+' /home/daiye/bin/mcnp5.mpi n='+mcnpinp)
            
            if os.path.isfile(mcnpinp+'o'):
                print('MCNP5 run finished!')
            else:
                print('error!!!,MCNP5 run failed!')
                exit(0)
            ### read results and write to results file
            
            keff = readKeff(mcnpinp+'o')
            meshfilename = mcnpinp + '_mesh_' + rod + '_' + str(instertposition)
            original_meshfilename = getMeshFilename(mcnpinp+'o')
            if os.path.isfile(original_meshfilename):
                mh.deleteFiles(meshfilename)
                os.rename(original_meshfilename, meshfilename)
                print("Rename meshtal to {:}\n".format(meshfilename))
				
            resultsfilename = mcnpinp + rod + '_' + str(instertposition) + '.csv'
            uncertainty = 1.1 * 1.1
            radialPowerPeakFactor, axialPowerPeakFactor, totPowerPeakFactor = computePowerDesityDistribution(
                meshfilename, resultsfilename, uncertainty)
            powerfactorresults[rod].append((instertposition, keff[0], radialPowerPeakFactor, 
            axialPowerPeakFactor, totPowerPeakFactor))    
            mh.cleanup(mcnpinp)
        ## set rod insertposition to inital
        cr[rod].setInsertPosition(initinsertposition)
        mh.modifyinp(mcnpinp, cr[rod].getTrCardNo(), cr[rod].ouputforMcnpinp(), 'data')
    

    maxradialPowerPeakFactor = 0
    maxaxialPowerPeakFactor = 0
    maxtotPowerPeakFactor = 0
    maxrod1 = ''
    maxrod2 = ''
    maxrod3 = ''
    #print(powerfactorresults)
    with open(mcnpinp+'results.out', 'w') as fid:
        fid.write('{:^5}{:^20}{:^8}{:^20}{:^20}{:^20}\n'.format\
                ('Rod', 'Insert position', 'Keff', 'Radial peak factor', 'Axial peak factor', 'Tot peak factor'))
        for rod in powerfactorresults:
            for ii in range(len(powerfactorresults[rod])):
                radialpowerfactor = powerfactorresults[rod][ii][2]
                axialpowerfactor = powerfactorresults[rod][ii][3]
                totpowerfactor = powerfactorresults[rod][ii][4]
                instertposition = powerfactorresults[rod][ii][0]
                keff = powerfactorresults[rod][ii][1]
                if maxradialPowerPeakFactor < radialpowerfactor:
                    maxrod1 = rod
                    maxradialPowerPeakFactor = radialpowerfactor
                if maxaxialPowerPeakFactor < axialpowerfactor:
                    maxrod2 = rod
                    maxaxialPowerPeakFactor = axialpowerfactor
                if maxtotPowerPeakFactor < totpowerfactor:
                    maxrod3 = rod
                    maxtotPowerPeakFactor = totpowerfactor
                fid.write('{:^5}{:^20.3f}{:^8.5f}{:^20.4f}{:^20.4f}{:^20.4f}\n'.format\
                (rod, instertposition, keff, radialpowerfactor, axialpowerfactor, totpowerfactor))

        fid.write('{:}:  {:}\n'.format('Rod', maxrod1))
        fid.write('{:}:  {:.4}\n'.format('Max radial power peak factor', maxradialPowerPeakFactor))
        fid.write('{:}:  {:}\n'.format('Rod', maxrod2))
        fid.write('{:}:  {:.4}\n'.format('Max axial power peak factor', maxaxialPowerPeakFactor))
        fid.write('{:}:  {:}\n'.format('Rod', maxrod3))
        fid.write('{:}:  {:.4}\n'.format('Max total power peak factor', maxtotPowerPeakFactor))

parser=argparse.ArgumentParser(description='input file name, node and ppn')
parser.add_argument('-n',action="store",dest="node",type=int,default=1)
parser.add_argument('-p',action="store",dest="ppn",type=int,default=1)
parser.add_argument('-m',action="store",dest="mode",type=str)
parser.add_argument('inp',action="store",type=str)
args=parser.parse_args()

print('inputfile=%s' %args.inp,'node=%s' %args.node,'ppn=%s' %args.ppn, 'mode=%s' %args.mode)
inp = args.inp
node = args.node
ppn = args.ppn
mode = args.mode


# set rod move step
rodstep = 10

# set mcnp input name
mcnpinp = inp

with open(mcnpinp, 'r', encoding="utf-8") as fread, open('init' + mcnpinp, 'w', encoding="utf-8") as fwrite:
    for eachline in fread:
        fwrite.write(eachline)


trforrod = {'tr1': '1#', 'tr3': '3#', 'tr5': '5#', 'tr6': '11#'}

maxPowerPeakFactorSearch(mcnpinp, node, ppn, trforrod, mode, rodstep)





