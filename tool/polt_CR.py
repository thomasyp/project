from tool.mcnp_reader import McnpTallyReader
import matplotlib.pyplot as plt
import pandas as pd
import re
from pathlib import Path, PurePath
import numpy as np

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

if __name__ == '__main__':  
    mtr = McnpTallyReader()
    path = Path('D:\work\mcnpxwork\博士课题\msasd\氯盐堆\\r150\850500OUT')
    basefilename = '850500o'
    loopdic = {1:4, 2:5, 3:20}
    crlist = []
    for key in loopdic.keys():
        for ii in range(loopdic[key]):
            filename = '-'.join([basefilename, str(key), str(ii+1)])
            print('read file {:}\n'.format(filename))
            crlist.append(mtr.getCR(PurePath.joinpath(path, filename)))
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
    outputfile = 'CR.dat'
    with open(PurePath.joinpath(path, outputfile), 'w') as fid:
        fid.write('{:^12}{:^10}\n'.format('Time (d)', 'CR'))
        for ii, cr in enumerate(crlist):
            fid.write('{:^12.5e} {:^10.5f}\n'.format(timelist[ii], cr))
          

