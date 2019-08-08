
def mainFunc(filename):
    time = [1, 1, 5]
    totHM = 0    
    with open(filename, 'r') as fid:
        listfromfile = fid.readlines()
        numoffile = int(listfromfile[1].strip())
        print(numoffile)
        burnup = float(listfromfile[3].strip())
        print(burnup)
        inpname = listfromfile[5].strip().split()[0]
        inpname = '.'.join([inpname, 'txt'])
        print(inpname)
        jj = 1
        for ii in range(4, 23, 3):
            time.append(1.0 * 10**jj)
            time.append(2.0 * 10**jj)
            time.append(5.0 * 10**jj)           
            jj += 1
    with open(inpname, 'r') as fid1, open('sum_HM.dat', 'w') as fid2:
        for eachline in fid1:
            linelist = eachline.strip().split()
            if linelist:
                numofnuclide = int(linelist[0])
                massofnuclide = float(linelist[1])
                if numofnuclide > 890000:
                        totHM += massofnuclide
        fid2.write('{:}\n'.format('总重金属质量(g)'))
        fid2.write('{:.7e}'.format(totHM))



if __name__ == '__main__':
    mainFunc('input-dose.inp')
    