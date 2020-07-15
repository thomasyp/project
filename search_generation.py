#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-

from tool.mcnp_reader import McnpTallyReader
from collections import defaultdict
from tool.handle_mcnpinp import McnpinpHandler
import numpy as np
import argparse
import os

parser=argparse.ArgumentParser(description='input file name, node and ppn')
parser.add_argument('-n', action="store", dest="node", type=int, default=1)
parser.add_argument('-p', action="store", dest="ppn", type=int, default=1)
parser.add_argument('--inp', '-i', action="store", dest='input', metavar="", 
                    help='MCNP input file', required=True, type=str)
parser.add_argument('--step', '-s', help='step lenth for calculation', 
                   metavar="", default=1e-5, type=float)
args=parser.parse_args()
print("input file is {:}, step lenth is {:}".format(args.input, args.step))
mcnpinp = args.input
node = args.node
ppn = args.ppn
step = args.step

mh = McnpinpHandler()
mtr = McnpTallyReader()
end = 5.0000e-04
resultfile = mcnpinp + 'results.out'

with open(resultfile, 'w') as fid:
   fid.write("{:^10} {:^10}\n".format('Added Th', 'keff'))
mh.cleanup(mcnpinp)
resultfile = mcnpinp + 'results.out'

for ii in np.arange(0, end, step):
    #modify density
    mcnpcontent = mh.readContent(mcnpinp, '4')
    density = mcnpcontent.strip().split()[2]
    mh.modifyinp(mcnpinp, '4', mcnpcontent.replace(density, '{:.6e}'.format(float(density)+ii)))
    #modify m card
    mcnpcontent = mh.readContent(mcnpinp, 'm1', section='data')
    mcnplist = mcnpcontent.strip().split()
    indx = mcnplist.index('90232.90c')
    mcnplist[indx+1] = '{:.6e}'.format(float(mcnplist[indx+1]) + ii)
    mcnpline = ' '.join(mcnplist)
    mh.modifyinp(mcnpinp, 'm1', mcnpline, section='data')
    os.system('mpirun -r ssh -np '+ str(int(node*ppn)) +' /home/daiye/bin/mcnp5.mpi n=' + mcnpinp)
    if os.path.isfile(mcnpinp+'o'):
        print('MCNP5 run finished!')
        keff = mtr.readKeff(mcnpinp+'o')['keff']        
        oldfilename = mcnpinp+'o'
        newfilename = mcnpinp+'o_'+'{:.4e}'.format(ii)
        mh.deleteFiles(newfilename)
        os.rename(oldfilename, newfilename)
        mh.cleanup(mcnpinp)
    else:
        print('error!!!,MCNP5 run failed!')
        exit(0)
    with open(resultfile, 'a') as fid:
        fid.write("{:^.4e} {:^.5f}\n".format(ii, keff))
                    
