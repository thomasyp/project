from itertools import groupby

class BaseClass():
    def __init__(self, label):
        self.label = label
   
    def __str__(self):
        return self.label

    def __format__(self,specification):
        if specification == "":
            return str(self)  
        strformat = '{:<6}'.format(self.label)
        return strformat
    
    def getLabel(self):
        return self.label

class Isotope(BaseClass):
    def __init__(self, label, an, mn):
        super(Isotope, self).__init__(label)
        self.atomicNumber = an
        self.massNumber = mn

    def getAtomicNumber(self):
        return self.atomicNumber

    def getMassNumber(self):
        return self.massNumber

class Nuclide(BaseClass):
    def __init__(self, label, isotopeDict):
        super(Nuclide, self).__init__(label)
        self.isotopeDict = isotopeDict
        tot = 0
        mass = 0
        for key, item in self.isotopeDict.items():
            tot += item
            mass += key.getMassNumber() * item
        self.actomicMass = mass / tot

    def getIsotope(self):
        return self.isotopeDict

    def getActomicMass(self):
        return self.actomicMass

class Compound(BaseClass):
    def __init__(self, lable, nuclideDict, p_a, p_b):
        super(Compound, self).__init__(lable)
        self.nuclideDict = nuclideDict
        self.p_a = p_a
        self.p_b = p_b
        mass = 0
        for key, item in self.nuclideDict.items():
            mass += key.getActomicMass() * item
        self.actomicMass = mass

    def getNuclide(self):
        return self.nuclideDict

    def getActomicMass(self):
        return self.actomicMass
        
    def getDensity(self, temp):
        """
           Bashed on this density computational function:
               pro = p_a - p_b * T (k)
        """
        return self.p_a - self.p_b * temp 
        
    def getMolarVolume(self, temp):
        return self.actomicMass / self.getDensity(temp)

class Material(BaseClass):
    def __init__(self, lable, compoundDict, temp):
        super(Material, self).__init__(lable)
        self.compoundDict = compoundDict
        self.temp = temp

    def getCompound(self):
        return self.compoundDict

    def getDensity(self):
        mass = 0
        volum = 0
        for key, item in self.compoundDict.items():
            mass += key.getActomicMass() * item
            volum += key.getMolarVolume(self.temp) * item
            # print(key, item)

        return mass / volum

    def toMcnpCard(self):
        totnuclideDict = {}
        for compound, molar in self.compoundDict.items():
            nuclideDict = compound.getNuclide()
            for nuclide, num in nuclideDict.items():
                if nuclide in totnuclideDict.keys():
                    totnuclideDict[nuclide] += num * molar
                else:
                    totnuclideDict[nuclide] = num * molar
        
        totIsotopeDict = {}
        for nuclide, num in totnuclideDict.items():
            isotopeDic = nuclide.getIsotope()
            for isotope, at in isotopeDic.items():
                totIsotopeDict[isotope] = num * at
        
        normaConstant = sum(totIsotopeDict.values())
        lines = ''
        for isotope, num in totIsotopeDict.items():
            if num != 0:
                line = "{:}{:}{:<12}  {:<12.6e}\n".format(isotope.getAtomicNumber(),
                    self.mcnpIsotopeNotation(isotope.getLabel()), self.tem2suffix(), num/normaConstant)
                lines += line 
            # print("{:}{:<10}  {:<12.6e}".format(isotope.getAtomicNumber(), isotope.getLabel(), num/normaConstant))
        return lines

    def mcnpIsotopeNotation(self, isotopelabel):
        lists = [''.join(list(g)) for k, g in groupby(isotopelabel, key=lambda x: x.isdigit())]
        if len(lists[1]) == 1:
            return '00'+lists[1]
        elif len(lists[1]) == 2:
            return '0'+lists[1]
        elif len(lists[1]) == 3:
            return lists[1]
        else:
            return -1

    def tem2suffix(self):
        return '.90c'

 


if __name__ == '__main__':
    u235 = Isotope('U235', 92, 235.043923)
    u233 = Isotope('U233', 92, 233.043923)
    u238 = Isotope('U238', 92, 238.050783)
    th232 = Isotope('Th232', 90, 232.03805)
    pu238 = Isotope('Pu238', 94, 238.0)
    pu239 = Isotope('Pu239', 94, 239.0)
    pu240 = Isotope('Pu240', 94, 240.0)
    pu241 = Isotope('Pu241', 94, 241.0)
    pu242 = Isotope('Pu242', 94, 242.0)
    f19 = Isotope('F19', 9, 18.998403)
    be9 = Isotope('Be9', 4, 9.012182)
    li6 = Isotope('li6', 3, 6.015122)
    li7 = Isotope('li7', 3, 7.016004)
    cl37 = Isotope('cl37', 17, 36.965903)
    mg24= Isotope('mg24', 12, 23.985042)
    mg25= Isotope('mg25', 12, 24.985837)
    mg26= Isotope('mg26', 12, 25.982593)
    na23 = Isotope('na23', 11, 22.989770)
    udict = {u235:0.1995, u238:0.8005}
    # udict = {u233:1}
    lidict = {li6:0.0005, li7:0.9995}
    fdict = {f19:1}
    cldict = {cl37:1}
    pudict = {pu238:0.019497, pu239:0.5875682, pu240:0.2371, pu241:0.10133776, pu242:0.05449704}
    mgdict = {mg24:0.7899, mg25:0.10, mg26:0.1101}
    nadict = {na23:1}
    cl = Nuclide('Cl', cldict)
    u = Nuclide('U', udict)
    f = Nuclide("F", fdict)
    li = Nuclide("Li", lidict)
    th = Nuclide("Th", {th232:1})
    be = Nuclide("Be", {be9:1})
    pu = Nuclide("Pu", pudict)
    mg = Nuclide("Mg", mgdict)
    na = Nuclide("Na", nadict)
    nacldict = {na:1, cl:1}
    thcl4dict = {th:1, cl:4}
    thf4dict = {th:1, f:4}
    mgcl2dict = {mg:1, cl:2}
    pucl3dict = {pu:1, cl:3}
    ucl3dict = {u:1, cl:3}
    uf4dict = {u:1, f:4}
    lifdict = {li:1, f:1}
    bef2dict = {be:1, f:2}
    # lifdict = {li:1, f:1}
    nacl = Compound('NaCl', nacldict, 2.1393, 0.543e-3)
    
    thcl4 = Compound('ThCl4', thcl4dict, 4.823, 0.0014)
    
    thf4 = Compound('ThF4', thf4dict, 7.108, 7.59e-4)
    
    pucl3 = Compound('PuCl3', pucl3dict, 4.809, 0.0014)
    # pucl3 = Compound('PuCl3', pucl3dict, 4.809, 9.92e-4)
    ucl3 = Compound('UCl3', uf4dict, 6.3747, 1.5222e-3)
    uf4 = Compound('UF4', uf4dict, 7.784, 9.92e-4)

    lif = Compound('lif', lifdict, 2.358, 4.902e-4)
    # thf4 = Compound('ThF4', thf4dict, 6.490933)
    bef2 = Compound('BeF2', bef2dict, 1.972, 1.45e-5)
    matdict = {nacl:90, pucl3:6, thcl4:4}
    # matdict = {nacl:55, ucl3:25, thcl4:20}
    # matdict = {lif:60, bef2:20, thf4:17.6, uf4:2.4}
    # 'label' 'matdict' 'temp'
    mat = Material('mat1', matdict, 900)
    # print(uf4.getActomicMass())
    # print(thf4.getActomicMass())
    print(mat.getDensity())
    print(mat.toMcnpCard())

    

