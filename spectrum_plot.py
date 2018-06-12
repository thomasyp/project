# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 15:06:26 2018

@author: yang
"""
import numpy as np
import pandas as pd
import re
import math
import matplotlib.pyplot as plt


class SpectrumPloter(object):
    def __init__(self):
        self.keyName = []
        self.volum = {}

    def write2dat(self, filename, **kw):
        readTag = {}
        datadict = {}
        for key, (_, vol) in kw.items():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []
            self.volum[key] = vol

        with open(filename, 'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == 'total':
                        for key in readTag.keys():
                            readTag[key] = False

                    if len(lists) > 3:
                        if lists[0] == '1tally' and lists[2] == 'nps':
                            for key, (tallyNum, _)in kw.items():
                                if lists[1] == str(tallyNum):
                                    readTag[key] = True
                                    datadict[key] = []
                    for key, (tallyNum, _) in kw.items():
                        if readTag[key] is True:
                            if re.match('\d\.\d{4}E[+-]\d{2}', lists[0]) is not None:
                                datadict[key].append(eachline.strip())
        #        print (datadict)
        for key, (tallyNum, _) in kw.items():
            datafilename = key + '.dat'  # type: str
            with open(datafilename, 'w') as f:
                for row in datadict[key]:
                    f.write('{}\n'.format(row))

    def plotSpectrum(self, sourceStrength, *dateName):
        spectrumData = pd.DataFrame(columns=['E'])
        for name in dateName:  # type: basestring
            filename = name + '.dat'
            obj = pd.read_csv(filename, header=None, sep=' ')
            df = obj.dropna(axis=1)
            df.columns = ['E', 'flux', 'error']
            spectrumData['E'] = df['E']
            spectrumData[name] = df['flux']
        

        for name in dateName:
            for ii in range(len(spectrumData['E'])):
                if ii == 0:
                    spectrumData[name][ii] = spectrumData[name][ii] * sourceStrength / \
                                             (math.log(spectrumData['E'][ii]) - math.log(1e-11)) \
                                             / self.volum[name]
                else:
                    spectrumData[name][ii] = spectrumData[name][ii] * sourceStrength / \
                                             (math.log(spectrumData['E'][ii]) - math.log(spectrumData['E'][ii - 1])) \
                                            / self.volum[name]
#        print(spectrumData)            
        ax = spectrumData.plot(x='E', y=list(dateName), logx=True, linewidth=3.0)
        plt.xlabel('$E \ (MeV)$', fontsize=15)
        plt.ylabel('$Flux\ per\ lethargy\ (n/cm^2/s)$', fontsize=15)
        plt.show()
        fig = ax.get_figure()
        fig.savefig('spectrum.tif',dpi=200)


if __name__ == '__main__':
    sp = SpectrumPloter()
    path = u'000.log'
    fuelTallyNum = 14
    fuelVolum = 6.30E+05
    graphtTallyNum = 24
    graphtVolum = 6.65E+06
    coreTallyNum = 4
    coreVolum = 7.28E+06

    sp.write2dat(path, fuel=[fuelTallyNum, fuelVolum], grapht=[graphtTallyNum, graphtVolum], core=[coreTallyNum, coreVolum])
    sp.plotSpectrum(1.52e17, 'fuel', 'core', 'grapht')
#    sp.write2dat(path, core=[coreTallyNum, coreVolum], grapht=[graphtTallyNum, graphtVolum])
#    sp.plotSpectrum(1.52e17, 'core', 'grapht')