# -*- coding: utf-8 -*-
"""
Read spectrum tally data in mcnp output file, and plot the spectrum.

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
        """
        Function: read spectrum tally data in mcnp output file and write to .dat file

        """
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

    def plotSpectrum(self, sourceStrength, *dateName, **kw):
        """
        Function: use .dat file which created by write2dat() to plot spectrum.
        """
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
    
#        ax = spectrumData.plot(x='E', y=list(dateName), logx=True, linewidth=3.0)
        
        setlogx = True
        setlogy = True
        

        if 'setlogx' in kw.keys():
            setlogx = kw['setlogx']

        if 'setlogy' in kw.keys():
            setlogy = kw['setlogy']

        ax = spectrumData.plot(x='E', y=list(dateName), logx=setlogx, logy=setlogy, linewidth=1.0)

        if 'xlabel' in kw.keys():
            plt.xlabel(kw['xlabel'], fontsize=15) 
        else:
            plt.xlabel('$E \ (MeV)$', fontsize=15)
        
        if 'ylabel' in kw.keys():
            plt.ylabel(kw['ylabel'], fontsize=15) 
        else:
            plt.ylabel('$Flux\ per\ lethargy\ (n/cm^2/s)$', fontsize=15)

        if 'ylim' in kw.keys():
            plt.ylim(kw['ylim'])

        if 'xlim' in kw.keys():
            plt.xlim(kw['xlim'])

        plt.show()
        fig = ax.get_figure()
        fig.savefig('spectrum.tif',dpi=200)


    def plotNormalizedSpectrum(self, *dateName, **kw):
        """
        Function: use .dat file which created by write2dat() to plot spectrum.
        """
        spectrumData = pd.DataFrame(columns=['E'])
        for name in dateName:  # type: basestring
            filename = name + '.dat'
            obj = pd.read_csv(filename, header=None, sep=' ')
            df = obj.dropna(axis=1)
            df.columns = ['E', 'flux', 'error']
            spectrumData['E'] = df['E']
            spectrumData[name] = df['flux'] 
        

        for name in dateName:
            sumdata = sum(spectrumData[name])
            for ii in range(len(spectrumData['E'])):
                if ii == 0:
                    spectrumData[name][ii] = spectrumData[name][ii]  / sumdata /\
                                             (math.log(spectrumData['E'][ii]) - math.log(1e-11)) \
                                             / self.volum[name]
                else:
                    spectrumData[name][ii] = spectrumData[name][ii] / sumdata / \
                                             (math.log(spectrumData['E'][ii]) - math.log(spectrumData['E'][ii - 1])) \
                                            / self.volum[name]
#        print(spectrumData) 
        setlogx = True
        setlogy = True
        

        if 'setlogx' in kw.keys():
            setlogx = kw['setlogx']

        if 'setlogy' in kw.keys():
            setlogy = kw['setlogy']

        ax = spectrumData.plot(x='E', y=list(dateName), logx=setlogx, logy=setlogy, linewidth=1.0)
        if 'xlabel' in kw.keys():
            plt.xlabel(kw['xlabel'], fontsize=15) 
        else:
            plt.xlabel('$E \ (MeV)$', fontsize=15)
        
        if 'ylabel' in kw.keys():
            plt.ylabel(kw['ylabel'], fontsize=15) 
        else:
            plt.ylabel('$Flux\ per\ lethargy\ (n/cm^2/s)$', fontsize=15)

        if 'ylim' in kw.keys():
            plt.ylim(kw['ylim'])

        if 'xlim' in kw.keys():
            plt.xlim(kw['xlim'])


        plt.show()
        fig = ax.get_figure()
        fig.savefig('spectrum.tif',dpi=200)


if __name__ == '__main__':
    sp = SpectrumPloter()
#    path = u'otag18'
    fuelTallyNum = 4
    fuelVolum = 1
    

#    sp.write2dat(path, salt_HM18=[fuelTallyNum, fuelVolum])
    path = u'otag5'
    sp.write2dat(path, salt_HM5=[fuelTallyNum, fuelVolum])
    
    path = u'otag10'    
    sp.write2dat(path, salt_HM10=[fuelTallyNum, fuelVolum])
    
    path = u'otag15'    
    sp.write2dat(path, salt_HM15=[fuelTallyNum, fuelVolum])
    
    path = u'otag20'    
    sp.write2dat(path, salt_HM20=[fuelTallyNum, fuelVolum])
    
    path = u'otag25'    
    sp.write2dat(path, salt_HM25=[fuelTallyNum, fuelVolum])
    
    path = u'otag30'    
    sp.write2dat(path, salt_HM30=[fuelTallyNum, fuelVolum])
    
    path = u'pbouv'    
    sp.write2dat(path, Pb=[fuelTallyNum, fuelVolum])
    
#    path = u'otag25'    
#    sp.write2dat(path, salt_HM25=[fuelTallyNum, fuelVolum])
#    
#    path = u'otag30'    
#    sp.write2dat(path, salt_HM30=[fuelTallyNum, fuelVolum])
    
    sp.plotSpectrum(1., 'salt_HM5', 'salt_HM10', 'salt_HM15', 'salt_HM20', 'salt_HM25', 'salt_HM30', 'Pb')
#    sp.write2dat(path, core=[coreTallyNum, coreVolum], grapht=[graphtTallyNum, graphtVolum])
#    sp.plotSpectrum(1.52e17, 'core', 'grapht')