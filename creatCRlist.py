from tool.mcnp_reader import McnpTallyReader
import tool.polt_CR
from pathlib import Path, PurePath
import numpy as np

mtr = McnpTallyReader()
path = Path('D:\\work\\mcnpxwork\\博士课题\\msasd\\氯盐堆\\r150\\四代\\burnup\\g4OUT')
basefilename = 'g4o'
# filename = '-'.join([basefilename, str(1), str(15)])
# # nuclidelist = ['90232', '91233', '94239', '94240', '94241', '92233', '92234', '92235', '92238']
# # atomdensitydic = {}
tallydic = {'1004':'94240', '1003':'94239', '1005':'94241', '1007':'90232', '1016':'91233', '1018':'92233', '1020':'92235', '1019':'92234', '1023':'92238'}
volum = 2.12058E+07
# captureratedic = {}
# fissratedic = {}
# for nuclide in nuclidelist:
#     print(nuclide)
#     atomdensitydic[nuclide] = mtr.getNuclideDensity(PurePath.joinpath(path, filename), 4, 1, nuclide)
# for tallynum, nuclide in tallydic.items():
    
#     capturetally = readFmtally(PurePath.joinpath(path, filename), tallynum, '102')
#     fisstally = readFmtally(PurePath.joinpath(path, filename), tallynum, '-6')
#     captureratedic[nuclide] = volum * atomdensitydic[nuclide] * capturetally
#     fissratedic[nuclide] = volum * atomdensitydic[nuclide] * fisstally
# cr = (captureratedic['90232']+captureratedic['92234']+captureratedic['92238']+\
#     captureratedic['94240']-captureratedic['91233']) / (captureratedic['92233']+\
#     captureratedic['92235']+captureratedic['94239']+captureratedic['94241']+\
#     fissratedic['92233']+fissratedic['92235']+fissratedic['94239']+\
#     fissratedic['94241'])
# print(getCR(PurePath.joinpath(path, filename), tallydic, 4, 1, volum))
# print (atomdensitydic)
loopdic = {1:4, 2:8, 3:5}
# loopdic = {1:21}
crlist = []
for key in loopdic.keys():
    for ii in range(loopdic[key]):
        filename = '-'.join([basefilename, str(key), str(ii+1)])
        print('read file {:}\n'.format(filename))
        crlist.append(tool.polt_CR.getCR(PurePath.joinpath(path, filename), tallydic, 4, 1, volum))
# timelist = np.array([0.00000e+00
#     ,6.00000e+02
#     ,1.20000e+03
#     ,1.80000e+03
#     ,2.40000e+03
#     ,3.00000e+03
#     ,3.60000e+03
#     ,4.20000e+03
#     ,4.80000e+03
#     ,5.40000e+03
#     ,6.00000e+03
#     ,6.60000e+03
#     ,7.20000e+03
#     ,7.80000e+03
#     ,8.40000e+03
#     ,9.00000e+03
#     ,9.60000e+03
#     ,1.02000e+04
#     ,1.08000e+04
#     ,1.14000e+04
#     ,1.20000e+04
# ])
timelist = np.array([0.00000e+00, 2.00000e+01, 4.00000e+01, 
                     6.00000e+01, 8.00000e+01, 2.80000e+02,
                     4.80000e+02, 6.80000e+02, 8.80000e+02,
                     1.08000e+03, 1.28000e+03, 1.48000e+03,
                     1.68000e+03, 2.28000e+03, 2.88000e+03,
                     3.48000e+03, 4.08000e+03, 4.68000e+03,
                     5.28000e+03, 5.88000e+03, 6.48000e+03,
                     7.08000e+03, 7.68000e+03, 8.28000e+03,
                     8.88000e+03, 9.48000e+03, 1.00800e+04,
                     1.06800e+04, 1.12800e+04, 1.18800e+04,
                     1.24800e+04, 1.30800e+04, 1.36800e+04,
                     1.42800e+04, 1.48800e+04, 1.54800e+04,
                     1.60800e+04
                    ])
outputfile = 'CR.dat'
with open(PurePath.joinpath(path, outputfile), 'w') as fid:
    fid.write('{:^12}{:^10}\n'.format('Time (d)', 'CR'))
    for ii, cr in enumerate(crlist):
        fid.write('{:^12.5e} {:^10.5f}\n'.format(timelist[ii], cr))