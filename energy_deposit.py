# -*- coding: utf-8 -*-
"""
Created on Wed May 30 14:48:06 2018

@author: yang
"""

from mcnp_reader import McnpTallyReader
import csv

mtr = McnpTallyReader()
#    mtr.readLatticeData2dat('pow.log',fuel=36)
tallys = {'fuel in active region':6, "grapht in active region":16, \
    'bypass':26, "primary container":36, "top plenum":46, "top support plate":56,\
    'top cap':66, 'bottom plenum':76, 'bottom support plate':86, 'bottom cap':96, \
    'top reflector':116, 'bottom reflector':126, 'pump sump':136, 'rod':146,\
    'tube':156, 'heat exchanger':166}
    
tallysResults = mtr.readSingleTally('dept.log', **tallys)

totEnergy = 0
for key in tallysResults.keys():
    totEnergy += float(tallysResults[key][0])
    
with open(u'1.5份额.csv','wb') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Component", "Tally results" , "Deposit Energy Portion"])
    for key, value in tallysResults.items():
        energyPortion ="{:.2f}".format(float(value[0]) / totEnergy * 100)
        lists = [key,value[0],energyPortion]
        writer.writerow(lists)
    
print totEnergy

