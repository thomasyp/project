#!/home/yangpu/bin/anaconda3/bin/python
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
    rawdata = mtr.readFmeshDataIntoDic(meshfilename, '14', 1, False, "Rslt * Vol", "Volume")
    neutronRadialEDeposit = np.array(rawdata["Rslt * Vol"]) 

    rawdata = mtr.readFmeshDataIntoDic(meshfilename, '114', 1, False, "Rslt * Vol", "Volume")

    gammaRadialEDeposit = np.array(rawdata["Rslt * Vol"]) 
    volume = np.array(rawdata["Volume"])
    radialPowerDensityDistri = (neutronRadialEDeposit + gammaRadialEDeposit) / volume
    
    # print(radialPowerDensityDistri)

    totpowerDesity = (gammaRadialEDeposit.sum() + neutronRadialEDeposit.sum())\
    / volume.sum()
    normRadialPowerDensityDistri =  radialPowerDensityDistri / totpowerDesity
    # print(totpowerDesity)
    # print(normRadialPowerDensityDistri)
    
    rawdata = mtr.readFmeshDataIntoDic(meshfilename, '24', 1, False, "Rslt * Vol", "Volume")
    neutronAxialEDeposit = np.array(rawdata["Rslt * Vol"])

    rawdata = mtr.readFmeshDataIntoDic(meshfilename, '124', 1, False, "Rslt * Vol", "Volume")
    gammaAxialEDeposit = np.array(rawdata["Rslt * Vol"])
    volume = np.array(rawdata["Volume"])

    axialPowerDensityDistri = (neutronAxialEDeposit + gammaAxialEDeposit) / volume
    normAxialPowerDensityDistri =  axialPowerDensityDistri / totpowerDesity
    #  计算径向功率峰因子
    radialPowerPeakFactor = np.max(normRadialPowerDensityDistri)
    
    #  计算轴向功率峰因子
    maxRadalPDIndex = np.argmax(radialPowerDensityDistri)
    
    rawdata = mtr.readFmeshDataIntoDic(meshfilename, '34', 1, False, "Rslt * Vol", "Volume")    
    neutronRAEDeposit = np.array(rawdata["Rslt * Vol"])

    rawdata = mtr.readFmeshDataIntoDic(meshfilename, '134', 1, False, "Rslt * Vol", "Volume")
    gammaRAEDeposit = np.array(rawdata["Rslt * Vol"])
    
    volume = np.array(rawdata["Volume"])
    
    nrow = radialPowerDensityDistri.shape[0]
    ncolumn = axialPowerDensityDistri.shape[0]
    RAEDensity = ((neutronRAEDeposit + gammaRAEDeposit) / volume).reshape(nrow, ncolumn)
    
    
    axialPowerPeakFactor = np.max(RAEDensity[maxRadalPDIndex]) / np.max(radialPowerDensityDistri)
    
    #输出结果到文件
    csvfilename = csvfilename
    radialstep = 10
    axialstep = 10
    with open(csvfilename, 'w', newline='') as fid:
        writer = csv.writer(fid)
        lenth = len(normRadialPowerDensityDistri)
        writer.writerow(["Radial normalized power distribution:"])
        for ii in range(lenth):
            if ii == 0:
                str1 = "{}~{}".format(0, 15)
            else:
                str1 = "{}~{}".format((ii-1)*10+15, ii*10+15)
            
            writer.writerow([str1, "{:.4f}".format(normRadialPowerDensityDistri[ii])])
        writer.writerow([""])
        writer.writerow(["Axial normalized power distribution:"])
        lenth = len(normAxialPowerDensityDistri)
        for ii in range(lenth):        
            str1 = "{}~{}".format((lenth-ii-1)*axialstep, (lenth-ii)*axialstep)
            
            writer.writerow([str1, "{:.4f}".format(normAxialPowerDensityDistri[lenth-ii-1])])
        writer.writerow([""])
        writer.writerow(["Radial Power Peak Factor:", "{:.4f}".format(radialPowerPeakFactor)])
        writer.writerow(["Axial Power Peak Factor:", "{:.4f}".format(axialPowerPeakFactor)])
        writer.writerow(["Total Power Peak Factor:", "{:.4f}".format(radialPowerPeakFactor*axialPowerPeakFactor*uncertainty)])
    return radialPowerPeakFactor, axialPowerPeakFactor, radialPowerPeakFactor*axialPowerPeakFactor*uncertainty
            
if __name__ == '__main__':
    computePowerDesityDistribution('meshtal', '1000.csv')
    computePowerDesityDistribution('meshtam', '1002.csv')
    computePowerDesityDistribution('meshtan', '1060.csv')
    computePowerDesityDistribution('meshtap', '1120.csv')
    computePowerDesityDistribution('meshtao', '1180.csv')
    computePowerDesityDistribution('meshtaq', '1240.csv')
    computePowerDesityDistribution('meshtar', '1300.csv')
