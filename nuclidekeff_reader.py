from tool.mcnp_reader import McnpTallyReader
from pathlib import Path, PurePath
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

mtr = McnpTallyReader()
loopdic = {1:4, 2:5, 3:13}
path = Path('D:\work\mcnpxwork\博士课题\msasd\氯盐堆\\r150\8501gOUT')
basefilename = '8501go'

keffofnuclide = defaultdict(lambda : 0)
nuclidelist = ['94238', '94239', '94240', '94241', '94242', '90232', '92235', '91233', '92233']
for nuclide in nuclidelist:
    keffofnuclide[nuclide] = []
for key in loopdic.keys():
    for ii in range(loopdic[key]):
        filename = '-'.join([basefilename, str(key), str(ii+1)])
        print('read file {:}\n'.format(filename))
        for nuclide in nuclidelist:
            keffofnuclide[nuclide].append(mtr.getNuclideKeff(PurePath.joinpath(path, filename), '4', '1', nuclide))

timelist = np.array([0.00000e+00
,2.00000e+01
,4.00000e+01
,6.00000e+01
,8.00000e+01
,2.80000e+02
,4.80000e+02
,6.80000e+02
,8.80000e+02
,1.08000e+03
,1.68000e+03
,2.28000e+03
,2.88000e+03
,3.48000e+03
,4.08000e+03
,4.68000e+03
,5.28000e+03
,5.88000e+03
,6.48000e+03
,7.08000e+03
,7.68000e+03
,8.28000e+03
,8.88000e+03
,9.48000e+03
,1.00800e+04
,1.06800e+04
,1.12800e+04
,1.18800e+04
,1.24800e+04])
outputfile = 'keffofnuclide.dat'
with open(PurePath.joinpath(path, outputfile), 'w') as fid:
    fid.write('{:^12}'.format('Time (d)'))
    for nuclide in nuclidelist:
         fid.write('{:^10}'.format(nuclide))
    fid.write('\n')
    for ii, time in enumerate(timelist):
        fid.write('{:^12.5e}'.format(timelist[ii]))
        for nuclide in nuclidelist:
            fid.write('{:^10.5f}'.format(keffofnuclide[nuclide][ii]))
        fid.write('\n')




