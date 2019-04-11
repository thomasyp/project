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
    def __init__(self, lable, nuclideDict, density):
        super(Compound, self).__init__(lable)
        self.nuclideDict = nuclideDict
        self.density =density
        mass = 0
        for key, item in self.nuclideDict.items():
            mass += key.getActomicMass() * item
        self.actomicMass = mass

    def getNuclide(self):
        return self.nuclideDict

    def getActomicMass(self):
        return self.actomicMass
        

    def getMolarVolume(self):
        return self.actomicMass / self.density

class Material(BaseClass):
    def __init__(self, lable, compoundDict):
        super(Material, self).__init__(lable)
        self.compoundDict = compoundDict

    def getCompound(self):
        return self.compoundDict

    def getDensity(self):
        mass = 0
        volum = 0
        for key, item in self.compoundDict.items():
            mass += key.getActomicMass() * item
            volum += key.getMolarVolume() * item
            print(key, item)

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
        for isotope, num in totIsotopeDict.items():
            print("{:<10}   {:<12.6e}".format(isotope, num/normaConstant))
            
 


if __name__ == '__main__':
    u235 = Isotope('U235', 92, 235.043923)
    u238 = Isotope('U238', 92, 238.050783)
    th232 = Isotope('Th232', 90, 232.03805)
    pu239 = Isotope('Pu239', 94, 239.0) 
    f19 = Isotope('F19', 9, 18.998403)
    be9 = Isotope('Be9', 4, 9.012182)
    li6 = Isotope('li6', 3, 9.012182)
    li7 = Isotope('li7', 3, 9.012182)
    cl37 = Isotope('cl37', 17, 36.965903)
    mg24= Isotope('mg24', 12, 23.985042)
    mg25= Isotope('mg25', 12, 24.985837)
    mg26= Isotope('mg26', 12, 25.982593)
    na23 = Isotope('na23', 11, 22.989770)
    udict = {u235:0.1995, u238:0.8005}
    fdict = {f19:1}
    cldict = {cl37:1}
    pudict = {pu239:1}
    mgdict = {mg24:0.7899, mg25:0.10, mg26:0.1101}
    nadict = {na23:1}
    cl = Nuclide('Cl', cldict)
    u = Nuclide('U', udict)
    f = Nuclide("F", fdict)
    th = Nuclide("Th", {th232:1})
    be = Nuclide("Be", {be9:1})
    pu = Nuclide("Pu", pudict)
    mg = Nuclide("Mg", mgdict)
    na = Nuclide("Na", nadict)
    nacldict = {na:1, cl:1}
    thcl4dict = {th:1, cl:4}
    mgcl2dict = {mg:1, cl:2}
    pucl3dict = {pu:1, cl:3}
    ucl3dic = {u:1, cl:3}
    # lifdict = {li:1, f:1}
    nacl = Compound('NaCl', nacldict, 1.741139)
    thcl4 = Compound('ThCl4', thcl4dict, 3.82)
    mgcl2 = Compound('MgCl2', mgcl2dict, 1.700576)
    pucl3 = Compound('PuCl3', pucl3dict, 4.809)
    ucl3 = Compound('UCl3', pucl3dict, 5.00472)
    # thf4 = Compound('ThF4', thf4dict, 6.490933)
    # bef2 = Compound('BeF2', bef2dict, 1.9602115)
    matdict = {nacl:64, pucl3:36}
    mat = Material('mat1', matdict)
    # print(uf4.getActomicMass())
    # print(thf4.getActomicMass())
    print(mat.getDensity())
    mat.toMcnpCard()

    

