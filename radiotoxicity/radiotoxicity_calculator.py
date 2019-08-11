import os 

def newRadiotoxicity(numberofnuclide):
    with open('new_radiotoxicity.inp', 'r') as fid1, open('radiotoxicity.inp', 'w') as fid2:
        for eachline in fid1:
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
                 fid2.write(eachline)

def radiation(nucliemassdic):
    with open('nucl_ID.inp', 'r') as fid1, open('rad_ID.inp', 'w') as fid2,\
         open('rad_NC.inp', 'w') as fid3, open('rad_LB.inp', 'w') as fid4:
        fid2.write("73$$   ")
        fid3.write("74**   ")
        fid4.write("75$$   ")
        for eachline in fid1:
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
    with open('curies_coef.dat', 'w') as fid1, open('r-coef.inp', 'r') as fid2,\
        open('curies.dat', 'r') as fid3:
        lists = fid3.readlines()
        
        for line in fid2:
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
    with open('curies_coef.dat', 'r') as fid:
        for line in fid:
            linelist = line.strip().split()
            fcurie.append([float(x) for x in linelist[1:]])
    lenthcolumn = len(fcurie[0])
    lenthrow = len(fcurie)
    print(fcurie[772][1])
    with open('SV.dat', 'w') as fid:
        for ii in range(lenthcolumn):
            tot = 0
            for jj in range(lenthrow):
                tot += fcurie[jj][ii]

            fid.write('{:^13.7e}\n'.format(tot))
    

        

           


    

def mainFunc(filename):
    time = [1, 1, 5]
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
            time.append(1.0 * 10**jj)
            time.append(2.0 * 10**jj)
            time.append(5.0 * 10**jj)           
            jj += 1
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
    nuclidedic = {'U':92}
    # for uranium
    basemassnumberofuranium = 231
    
    with open('com_nucl.inp', 'r') as fid3:
        for eachline in fid3:
            linelist = eachline.strip().split()
            if len(linelist) > 2:
                tagofnuclide = int(linelist[0]) 
                atomnumber = int(linelist[1])
                massnumber = int(linelist[2])
                massofnuclide = float(linelist[3])
                for ii in range(1,8):
                    massofuranium = {}
                    massnumberofuranium = ii + basemassnumberofuranium
                    if atomnumber == nuclidedic['U'] and massnumberofuranium == massnumber:
                        massofuranium[tagofnuclide] = massofnuclide   
                        radiation(massofuranium)
    
    # with open('SV.dat', 'r') as fid

    

    # outfilename = ''.join(['SVGWy_', prefixofinp, '_', nuclidedic['U'], '.dat'])
    # with open(outfilename, 'w') as fid:


if __name__ == '__main__':
    mainFunc('input-dose.inp')
    # newRadiotoxicity(1)
    
    