import os 
import pkgutil
from tool.self_defined_exception import CustomError

def newRadiotoxicity(numberofnuclide):
    contents = getDataInPackage('new_radiotoxicity.inp').split('\r\n')
    with open('radiotoxicity.inp', 'w') as fid2:
        for eachline in contents:
            if 'n56_13.inp' in eachline:
                fid2.write("a13     {:d}\n".format(numberofnuclide))
            elif 'rad_ID.inp' in eachline:
                with open('rad_ID.inp', 'r') as fid:
                    for line in fid:
                        linelist = line.strip().split()
                        if linelist:
                            fid2.write(line)
            elif 'rad_LB.inp' in eachline:
                with open('rad_LB.inp', 'r') as fid:
                    for line in fid:
                        linelist = line.strip().split()
                        if linelist:
                            fid2.write(line)
            elif 'rad_NC.inp' in eachline:
                with open('rad_NC.inp', 'r') as fid:
                    for line in fid:
                        linelist = line.strip().split()
                        if linelist:
                            fid2.write(line)
            else:
                 fid2.write(eachline+'\n')

def output(filename, nuclidelist=None, timelist=None, datalist=None, unit='Sv/GWy'):
    with open(filename, 'w') as fid:
        fid.write('{:^100}\n'.format(''.join(['Radiotoxicity, ', 'Unit ', unit])))
        if nuclidelist:
            fid.write('{:^12}'.format('Time(years)'))
            for nuclide in nuclidelist:
                fid.write('{:^14}'.format(nuclide))
            fid.write('\n')
        if timelist and datalist:
            for ii, time in enumerate(timelist):
                fid.write('{:^12d}'.format(time))
                for data in datalist:
                    fid.write('{:^14.4e}'.format(data[ii]))
                fid.write('\n')

def calculateSVofNuclide(atomnumberofelement, basemassnumberofelement, numofnuclide):
    svdata = []
    with open('com_nucl.inp', 'r') as fid3:
        for eachline in fid3:
            linelist = eachline.strip().split()
            if len(linelist) > 2:
                tagofnuclide = int(linelist[0]) 
                atomnumber = int(linelist[1])
                massnumber = int(linelist[2])
                massofnuclide = float(linelist[3])
                for ii in range(1, numofnuclide):
                    massofelement = {}
                    massnumberofnuclide = ii + basemassnumberofelement
                    if atomnumber == atomnumberofelement and massnumberofnuclide == massnumber:
                        massofelement[tagofnuclide] = massofnuclide   
                        sv = radiation(massofelement)
                        svdata.append(sv[1:])
        # print(massofelement) 
    return svdata

def calculateSVofElement(atomnumberofelement):
    massofelement = {}
    with open('com_nucl.inp', 'r') as fid3:
        for eachline in fid3:
            linelist = eachline.strip().split()
            if len(linelist) > 2:
                tagofnuclide = int(linelist[0]) 
                atomnumber = int(linelist[1])
                massnumber = int(linelist[2])
                massofnuclide = float(linelist[3])
                if atomnumber == atomnumberofelement:
                    massofelement[tagofnuclide] = massofnuclide
        if massofelement:
            # print(massofelement)  
            sv = radiation(massofelement)
        else:
            sv = [x*0 for x in range(23)]
             
    return sv[1:]

def covert2SvperGWy(svdata, burnup):
    for ii, row in enumerate(svdata):
        for jj, data in enumerate(row):
            svdata[ii][jj] = svdata[ii][jj] / burnup
    return svdata

def radiation(nucliemassdic):
    nuclID = getDataInPackage('nucl_ID.inp').split('\r\n')
    with open('rad_ID.inp', 'w') as fid2,\
         open('rad_NC.inp', 'w') as fid3, open('rad_LB.inp', 'w') as fid4:
        fid2.write("73$$   ")
        fid3.write("74**   ")
        fid4.write("75$$   ")
        for eachline in nuclID:
            linelist = eachline.strip().split()
            if linelist and linelist[1].isdigit():
                nuclidelable = linelist[0]
                tagofnuclide = int(linelist[1])
                massnumber = int(linelist[2])
                ntype = int(linelist[3])
                if tagofnuclide in nucliemassdic.keys():
                    fid2.write('{:^10d}\n'.format(tagofnuclide))
                    fid3.write('{:^20.7e}\n'.format(nucliemassdic[tagofnuclide]))
                    fid4.write('{:^10d}\n'.format(ntype))
    
    newRadiotoxicity(len(nucliemassdic))
    os.system("runscale1 radiotoxicity.inp")

    flag = False
    
    with open('radiotoxicity.out', 'r') as fid1, open('curies.dat', 'w') as fid2:
        for line in fid1:
            linelist = line.strip().split()
            if line[47:76] == "nuclide radioactivity, curies":
                flag = True
                numofline = 0
            if linelist and (linelist[0] == '1' or linelist[0] == 'total'):
                flag = False
                # print('teststs')
            if flag:
                numofline += 1
                if numofline > 5:
                    if line[4] == ' ':
                        testlist = line.strip().split()
                        if len(testlist) > 12:
                            fid2.write('{:<8}'.format(''.join(testlist[:2])))
                            fid2.write(line[11:].strip())
                        else:
                            fid2.write('{:<8}'.format(testlist[0]))
                            fid2.write(line[12:].strip())
                    else:
                        fid2.write(line)

    rcoef = getDataInPackage('r-coef.inp').split('\r\n')
    with open('curies_coef.dat', 'w') as fid1, open('curies.dat', 'r') as fid3:
        lists = fid3.readlines()
        
        for line in rcoef:
            linelist = line.strip().split()
            if linelist:
                tagofnuclide = linelist[0]
                fcoef = float(linelist[1])
                for subline in lists:
                    sublist = subline.strip().split()
                    if tagofnuclide == sublist[0]:
                        fid1.write('{:<6}'.format(tagofnuclide))
                        for data in sublist[1:]:
                            fid1.write('{:^13.5e}'.format(float(data)*fcoef))
                        fid1.write('\n')
    fcurie = []
    sv = []
    with open('curies_coef.dat', 'r') as fid:
        for line in fid:
            linelist = line.strip().split()
            fcurie.append([float(x) for x in linelist[1:]])
    lenthcolumn = len(fcurie[0])
    lenthrow = len(fcurie)
    with open('SV.dat', 'w') as fid:
        for ii in range(lenthcolumn):
            tot = 0
            for jj in range(lenthrow):
                tot += fcurie[jj][ii]
            sv.append(tot)
            fid.write('{:^13.7e}\n'.format(tot))
    return sv

def getDataInPackage(filename):
    data_bytes = pkgutil.get_data(__package__, filename)
    data_str = data_bytes.decode("utf8")
    return data_str

def mainFunc(filename, toxicitytype='Ac'):
    try:
        if toxicitytype not in ['Ac', 'FP']:
            raise CustomError('Unrecognizedtoxicity type!')
    except TypeError as e:
        print(e)
        return -1

    time = [1, 5]
    totHM = 0    
    with open(filename, 'r') as fid:
        listfromfile = fid.readlines()
        numoffile = int(listfromfile[1].strip())
        print(numoffile)
        burnup = float(listfromfile[3].strip())
        print(burnup)
        prefixofinp = listfromfile[5].strip().split()[0]
        inpname = '.'.join([prefixofinp, 'txt'])
        print(inpname)
        jj = 1
        for ii in range(4, 23, 3):
            time.append(1 * 10**jj)
            time.append(2 * 10**jj)
            time.append(5 * 10**jj)           
            jj += 1
        time = time[:-2]
    with open(inpname, 'r') as fid1, open('sum_HM.dat', 'w') as fid2, open('com_nucl.inp', 'w') as fid3:
        
        for eachline in fid1:
            linelist = eachline.strip().split()
            if linelist:
                tagofnuclide = int(linelist[0])
                massofnuclide = float(linelist[1])
                if tagofnuclide > 890000:
                    totHM += massofnuclide
        fid2.write('{:}\n'.format('总重金属质量(g)'))
        fid2.write('{:.7e}'.format(totHM))

    with open(inpname, 'r') as fid1, open('com_nucl.inp', 'w') as fid3:
        fid3.write("nuclear  concent(g/MTHN)\n")
        for eachline in fid1:
            linelist = eachline.strip().split()
            if linelist:
                tagofnuclide = int(linelist[0])
                massofnuclide = float(linelist[1])
                atomnumber = int(tagofnuclide / 10000)
                massnumber = int(tagofnuclide / 10) - atomnumber*1000
                fid3.write('{:^10d} {:^10d} {:^10d} {:^20.7e}\n'.format(tagofnuclide, atomnumber, massnumber, massofnuclide/totHM*1e6))
    if toxicitytype == 'Ac':
        # for uranium
        basemassnumberofuranium = 231
        atomnumber = 92
        numofnuclideinuranium = 7
        
        svdata = calculateSVofNuclide(atomnumber, basemassnumberofuranium, numofnuclideinuranium+1)
        nuclidelist = ['U-232', 'U-233', 'U-234', 'U-235', 'U-236', 'U-237', \
                        'U-238']
        output(''.join(['SVMTHN_', prefixofinp,'_', 'U', '.dat']), nuclidelist, time, svdata, unit='Sv/MTHN')
        output(''.join(['SVGWy_', prefixofinp,'_', 'U', '.dat']), nuclidelist, time, covert2SvperGWy(svdata, burnup), unit='Sv/GWy')

        # for plutonium
        basemassnumberofplutonium = 237
        atomnumber = 94
        numofnuclideinplutonium = 7
        
        svdata = calculateSVofNuclide(atomnumber, basemassnumberofplutonium, numofnuclideinplutonium+1)
        nuclidelist = ['Pu-238', 'Pu-239', 'Pu-240', 'Pu-241', 'Pu-242', 'Pu-243',\
            'Pu-244']
        output(''.join(['SVMTHN_', prefixofinp,'_', 'Pu', '.dat']), nuclidelist, time, svdata, unit='Sv/MTHN')
        output(''.join(['SVGWy_', prefixofinp,'_', 'Pu', '.dat']), nuclidelist, time, covert2SvperGWy(svdata, burnup), unit='Sv/GWy')

        # #for Th
        # basemassnumberofthorium  = 226
        # atomnumber = 90
        # numofnuclideinthorium = 9
        
        # svdata = calculateSVofNuclide(atomnumber, basemassnumberofthorium, numofnuclideinthorium+1)
        # nuclidelist = ['Th-226', 'Th-227', 'Th-228', 'Th-229', 'Th-230', 'Th-231', 'Th-232', 'Th-233', 'Th-234']
        # output(''.join(['SVMTHN_', prefixofinp,'_', 'Th', '.dat']), nuclidelist, time, svdata, unit='Sv/MTHN')
        # output(''.join(['SVGWy_', prefixofinp,'_', 'Th', '.dat']), nuclidelist, time, covert2SvperGWy(svdata, burnup), unit='Sv/GWy')
        
        #for Th-Cf
        baseatomnumber = 89
        numofelement = 10
        svdata = []
        for ii in range(1, numofelement):
            atomnumber = ii + baseatomnumber
            # print(atomnumber)
            sv = calculateSVofElement(atomnumber)
            svdata.append(sv)
        tot = [0*ii for ii in range(len(svdata[0]))]
        for sv in svdata:
            for ii, data in enumerate(sv):
                tot[ii] += data

        svdata.append(tot)
        nuclidelist = ['Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'total']
        output(''.join(['SVMTHN_', prefixofinp, '_', 'Ac', '.dat']), nuclidelist, time, svdata, unit='Sv/MTHN')
        output(''.join(['SVGWy_', prefixofinp, '_', 'Ac', '.dat']), nuclidelist, time, covert2SvperGWy(svdata, burnup), unit='Sv/GWy')
    else:
        #for FP
        baseatomnumber = 1
        numofelement = 80
        skiplist = [48, 52, 67, 76]
        svdata = []
        for ii in range(1, numofelement):
            atomnumber = ii + baseatomnumber
            print("starting atom number: {:}".format(atomnumber))
            if atomnumber in skiplist:
                continue
            sv = calculateSVofElement(atomnumber)
            svdata.append(sv)
        tot = [0*ii for ii in range(len(svdata[0]))]
        for sv in svdata:
            for ii in range(len(tot)):
                tot[ii] += sv[ii]
        svdata.append(tot)
        nuclidelist = ['total']
        output(''.join(['SVMTHN_', prefixofinp, '_', 'FP', '.dat']), nuclidelist, time, [svdata[-1]], unit='Sv/MTHN')
        output(''.join(['SVGWy_', prefixofinp, '_', 'FP', '.dat']), nuclidelist, time, covert2SvperGWy([svdata[-1]], burnup), unit='Sv/GWy')
    


if __name__ == '__main__':
    mainFunc('input-dose.inp')
    # newRadiotoxicity(1)
    
    