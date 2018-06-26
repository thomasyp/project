# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 10:15:47 2018

@author: yang
"""

from mcnp_reader import McnpTallyReader 
import numpy as np
import csv

def computePowerDesityDistribution(meshfilename, csvfilename, uncertainty=1.2):
    """
    Fuction name: 
            computePowerDesityDistribution           
    Fuction:
            计算径向和轴向归一化功率密度分布和功率峰因子并输出到.csv文件中。
    Input parameter:
            fmesh文件路径和文件名：meshfilename
            输出.csv文件名： csvfilename
            总功率峰不确定度： uncertainty
    Return:   
            无
    """
    
    mtr = McnpTallyReader()
    neutronRadialEDeposit = np.array(mtr.readDataIntoArray(meshfilename, '14', 1, "Rslt * Vol", "Volume"))
    gammaRadialEDeposit = np.array(mtr.readDataIntoArray(meshfilename, '114', 1, "Rslt * Vol", "Volume"))
    radialPowerDensityDistri = (neutronRadialEDeposit + gammaRadialEDeposit)[0] / gammaRadialEDeposit[1]
    
    totpowerDesity = (gammaRadialEDeposit.sum(axis=1)[0] + neutronRadialEDeposit.sum(axis=1)[0])\
     / neutronRadialEDeposit.sum(axis=1)[1]
    normRadialPowerDensityDistri =  radialPowerDensityDistri / totpowerDesity
    
    
    neutronAxialEDeposit = np.array(mtr.readDataIntoArray(meshfilename, '24', 1, "Rslt * Vol", "Volume"))
    gammaAxialEDeposit = np.array(mtr.readDataIntoArray(meshfilename, '124', 1, "Rslt * Vol", "Volume"))
    
    axialPowerDensityDistri = (neutronAxialEDeposit + gammaAxialEDeposit)[0] / gammaAxialEDeposit[1]
    normAxialPowerDensityDistri =  axialPowerDensityDistri / totpowerDesity
    #  计算径向功率峰因子
    radialPowerPeakFactor = np.max(normRadialPowerDensityDistri)
    
    #  计算轴向功率峰因子
    maxRadalPDIndex = np.argmax(radialPowerDensityDistri)
    
        
    neutronRAEDeposit = np.array(mtr.readDataIntoArray(meshfilename, '34', 1, "Rslt * Vol", "Volume"))
    gammaRAEDeposit = np.array(mtr.readDataIntoArray(meshfilename, '134', 1, "Rslt * Vol", "Volume"))
    nrow = radialPowerDensityDistri.shape[0]
    ncolumn = axialPowerDensityDistri.shape[0]
    RAEDensity = ((neutronRAEDeposit[0] + gammaRAEDeposit[0]) / neutronRAEDeposit[1]).reshape(nrow, ncolumn)
    
    
    axialPowerPeakFactor = np.max(RAEDensity[maxRadalPDIndex]) / np.max(radialPowerDensityDistri)
    
    #输出结果到文件
    csvfilename = csvfilename
    with open(csvfilename, 'wb') as fid:
        writer = csv.writer(fid)
        lenth = len(normRadialPowerDensityDistri)
        writer.writerow(['', "Radial normalized power distribution:"])
        for ii in range(lenth):
            if ii == 0:
                str1 = "{}~{}".format(0, 15)
            else:
                str1 = "{}~{}".format((ii-1)*10+15, ii*10+15)
            
            writer.writerow([str1, "{:.4f}".format(normRadialPowerDensityDistri[ii])])
        writer.writerow([""])
        writer.writerow(['', "Axial normalized power distribution:"])
        lenth = len(normAxialPowerDensityDistri)
        for ii in range(lenth):        
            str1 = "{}~{}".format((lenth-ii)*18, (lenth-ii-1)*18)
            
            writer.writerow([str1, "{:.4f}".format(normAxialPowerDensityDistri[lenth-ii-1])])
        writer.writerow([""])
        writer.writerow(["Radial Power Peak Factor:", "{:.4f}".format(radialPowerPeakFactor)])
        writer.writerow(["Axial Power Peak Factor:", "{:.4f}".format(axialPowerPeakFactor)])
        writer.writerow(["Total Power Peak Factor:", "{:.4f}".format(radialPowerPeakFactor*axialPowerPeakFactor*uncertainty)])
            
if __name__ == '__main__':
    computePowerDesityDistribution('meshtam', '0000.csv')
    computePowerDesityDistribution('meshtam', '0002.csv')
    computePowerDesityDistribution('meshtam', '0060.csv')
    computePowerDesityDistribution('meshtam', '0120.csv')
    computePowerDesityDistribution('meshtam', '0180.csv')
    computePowerDesityDistribution('meshtam', '0240.csv')
    computePowerDesityDistribution('meshtam', '0300.csv')
