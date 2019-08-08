from tool.mcnp_reader import McnpTallyReader
import matplotlib.pyplot as plt
import pandas as pd
import re

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

poltCR('pu862_1OUT', {1:4, 2:5, 3:16})
