from tool.mcnp_reader import McnpTallyReader
import matplotlib.pyplot as plt
import pandas as pd
import re
from pathlib import Path, PurePath
import numpy as np
from collections import defaultdict

def poltCR(foldname, ndict):
    path = foldname + '\\MOBATADS.OUT'
    mtr = McnpTallyReader()
    with open(path, 'r') as fid:
            for eachline in fid:
                title = eachline
                break
        
    namelists = re.split("\s{2,}", title.strip())
    timetag = namelists[1]
    namelists.insert(1, 'dummy')

    results = pd.read_csv(path, sep='\s+', usecols=lambda x: x not in ['dummy'], skiprows=1, header=None, names=namelists)

    inpname = foldname[:-3]
    print(inpname)
    # print(results['Time(d)'])
    crlists = []
    for ii in ndict.keys():
        for jj in range(ndict[ii]):
            path = foldname + '\\' + inpname + 'o-' + str(ii) + '-' + str(jj+1)
            crlists.append(mtr.getCR(path))    

    plt.plot(results['Time(d)'], crlists, '-o')
    # plt.xlim(0,1500)
    plt.xlabel('Time (days)')
    plt.ylabel('CR')
    plt.show()

def readFmtally(filename, tallynum, reaction):
    tag = False
    tally = 0
    keywords = ' '.join(['multiplier bin:   1.00000E+00', tallynum])
    with open(filename, 'r') as fid:   
        for eachline in fid:
            linelist = eachline.strip().split()
            if keywords in eachline and reaction == linelist[-1]:
                tag = True
            if not linelist:
                tag = False
            if tag and len(linelist) == 2:
                tally = float(linelist[0])
            
    return tally

def getCR(filename, tallydic, cell, matnum, volume):
    nuclidelist = ['90232', '91233', '94239', '94240', '94241', '92233', '92234', '92235', '92238']
    captureratedic = {}
    fissratedic = {}
    atomdensitydic = {}
    for nuclide in nuclidelist:
        atomdensitydic[nuclide] = mtr.getNuclideDensity(PurePath.joinpath(path, filename), cell, matnum, nuclide)
    for tallynum, nuclide in tallydic.items():    
        capturetally = readFmtally(PurePath.joinpath(path, filename), tallynum, '102')
        fisstally = readFmtally(PurePath.joinpath(path, filename), tallynum, '-6')
        captureratedic[nuclide] = volum * atomdensitydic[nuclide] * capturetally
        fissratedic[nuclide] = volum * atomdensitydic[nuclide] * fisstally
    cr = (captureratedic['90232']+captureratedic['92234']+captureratedic['92238']+\
        captureratedic['94240']-captureratedic['91233']) / (captureratedic['92233']+\
        captureratedic['92235']+captureratedic['94239']+captureratedic['94241']+\
        fissratedic['92233']+fissratedic['92235']+fissratedic['94239']+\
        fissratedic['94241'])
    return cr

def getfissrate(filename, cell, matnum, volume):
    fissratedic = defaultdict(lambda: 0)
    nuclidelist = ['90232', '91233', '94239', '94240', '94241', '92233', '92234', '92235', '92238']
    tallydic = {'1003':'94239', '1005':'94241', '1018':'92233', '1020':'92235'}
    atomdensitydic = {}
    for nuclide in nuclidelist:
        atomdensitydic[nuclide] = mtr.getNuclideDensity(PurePath.joinpath(path, filename), cell, matnum, nuclide)
    for tallynum, nuclide in tallydic.items():    
        fisstally = readFmtally(PurePath.joinpath(path, filename), tallynum, '-6')
        fissratedic[nuclide] = volum * atomdensitydic[nuclide] * fisstally
    return fissratedic 

def getThoriumPowerFraction(path, filename, cell, matnum, volume):
    mtr = McnpTallyReader()
    fission_energy_dic = defaultdict(lambda: 0)
    nuclidelist = ['90232', '91233', '94239', '94240', '94241', '92233', '92234', '92235', '92238']
    tallydic = {'1003':'94239', '1005':'94241', '1018':'92233', '1020':'92235'}
    atomdensitydic = {}
    for nuclide in nuclidelist:
        atomdensitydic[nuclide] = mtr.getNuclideDensity(PurePath.joinpath(path, filename), cell, matnum, nuclide)
    for tallynum, nuclide in tallydic.items():    
        Z = float(nuclide[0:2])
        A = float(nuclide[2:])
        Q = 0.00129927 * Z**2 * A**0.5+33.12
        fisstally = readFmtally(PurePath.joinpath(path, filename), tallynum, '-6')
        fission_energy_dic[nuclide] = volume * atomdensitydic[nuclide] * fisstally * Q 
    tot_energy = 0
    for nuclide, fission_energy in fission_energy_dic.items():
        tot_energy += fission_energy
    print(tot_energy)
    return fission_energy_dic    


if __name__ == '__main__':  
    mtr = McnpTallyReader()
    path = Path('D:\work\mcnpxwork\博士课题\msasd\氯盐堆\\r150\四代\\burnup\g4OUT')
    # path = Path('D:\work\mcnpxwork\博士课题\msasd\氯盐堆\\r150\850cOUT')
    basefilename = 'g4o'
    # basefilename = '850co'
    # filename = '-'.join([basefilename, str(1), str(15)])
    # # nuclidelist = ['90232', '91233', '94239', '94240', '94241', '92233', '92234', '92235', '92238']
    # # atomdensitydic = {}
    tallydic = {'1004':'94240', '1003':'94239', '1005':'94241', '1007':'90232', 
    '1016':'91233', '1018':'92233', '1020':'92235', '1019':'92234', '1023':'92238'}
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
    # fission rate calculate*****************************
#     loopdic = {1:4, 2:8, 3:5}
#     # loopdic = {1:21}
#     fissratelist = []
#     for key in loopdic.keys():
#         for ii in range(loopdic[key]):
#             filename = '-'.join([basefilename, str(key), str(ii+1)])
#             print('read file {:}\n'.format(filename))
#             fissratelist.append(getfissrate(PurePath.joinpath(path, filename), 4, 1, volum))
#     timelist = np.array([0.00000e+00
# , 0.00000e+00
# , 2.00000e+01
# , 4.00000e+01
# , 6.00000e+01
# , 8.00000e+01
# , 2.80000e+02
# , 4.80000e+02
# , 6.80000e+02
# , 8.80000e+02
# , 1.08000e+03
# , 1.28000e+03
# , 1.48000e+03
# , 1.68000e+03
# , 2.28000e+03
# , 2.88000e+03
# , 3.48000e+03
# , 4.08000e+03
# ])
#     # timelist = np.array([0.00000e+00
#     #     ,2.00000e+01
#     #     ,4.00000e+01
#     #     ,6.00000e+01
#     #     ,8.00000e+01
#     #     ,2.80000e+02
#     #     ,4.80000e+02
#     #     ,6.80000e+02
#     #     ,8.80000e+02
#     #     ,1.08000e+03
#     #     ,1.68000e+03
#     #     ,2.28000e+03
#     #     ,2.88000e+03
#     #     ,3.48000e+03
#     #     ,4.08000e+03
#     #     ,4.68000e+03
#     #     ,5.28000e+03
#     #     ,5.88000e+03
#     #     ,6.48000e+03
#     #     ,7.08000e+03
#     #     ,7.68000e+03
#     #     ,8.28000e+03
#     #     ,8.88000e+03
#     #     ,9.48000e+03
#     #     ,1.00800e+04
#     #     ,1.06800e+04
#     #     ,1.12800e+04
#     #     ,1.18800e+04
#     #     ,1.24800e+04
#     #     ])
#     outputfile = 'fissionrate.dat'
#     sumfissrate = []
#     for ii, cr in enumerate(fissratelist):
#         sumfissrate.append(sum(fissratelist[ii].values()))
#     # print(fissratelist)
#     with open(PurePath.joinpath(path, outputfile), 'w') as fid:
#         fid.write('{:^12} {:^20} {:^20} {:^20} {:^20}\n'.format('Time (d)', 'fiss rate of U233', 'fiss rate of U235', 'fiss rate of Pu239', 'fiss rate of Pu241'))
#         for ii, cr in enumerate(fissratelist):
#             fid.write('{:^12.5e} {:^20.5f} {:^20.5f} {:^20.5f} {:^20.5f}\n'.format(timelist[ii], 
#             fissratelist[ii]['92233']/sumfissrate[ii], fissratelist[ii]['92235']/sumfissrate[ii], 
#             fissratelist[ii]['94239']/sumfissrate[ii], fissratelist[ii]['94241']/sumfissrate[ii]))
#*******************************************************************************************************

#Thorium power Fraction calculate
        
    thorium_power_fraction_list = []
    loopdic = {1:4, 2:8, 3:25}
    # loopdic = {1:21}
    for key in loopdic.keys():
        for ii in range(loopdic[key]):
            filename = '-'.join([basefilename, str(key), str(ii+1)])
            print('read file {:}\n'.format(filename))
            thorium_power_fraction_list.append(getThoriumPowerFraction(PurePath.joinpath(path, filename), 4, 1, volum))
#     timelist = np.array([0.00000e+00
# , 0.00000e+00
# , 2.00000e+01
# , 4.00000e+01
# , 6.00000e+01
# , 8.00000e+01
# , 2.80000e+02
# , 4.80000e+02
# , 6.80000e+02
# , 8.80000e+02
# , 1.08000e+03
# , 1.28000e+03
# , 1.48000e+03
# , 1.68000e+03
# , 2.28000e+03
# , 2.88000e+03
# , 3.48000e+03
# , 4.08000e+03
# ])
    outputfile = 'ThPF.dat'
    totpower = []
    for ii, thorium_power_fraction in enumerate(thorium_power_fraction_list):
        totpower.append(sum(thorium_power_fraction.values()))
    # print(fissratelist)
    with open(PurePath.joinpath(path, outputfile), 'w') as fid:
        fid.write('{:^12} {:^20} {:^20} {:^20} {:^20}\n'.format('Time (d)', 'power of U233', 
        'power of U235', 'power of Pu239', 'power of Pu241'))
        for ii, thorium_power_fraction in enumerate(thorium_power_fraction_list):
            fid.write('{:^12d} {:^20.5f} {:^20.5f} {:^20.5f} {:^20.5f}\n'.format(ii, 
            thorium_power_fraction['92233']/totpower[ii], thorium_power_fraction['92235']/totpower[ii], 
            thorium_power_fraction['94239']/totpower[ii], thorium_power_fraction['94241']/totpower[ii]))
            

