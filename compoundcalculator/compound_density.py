from itertools import groupby
import re

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


class Nuclide(BaseClass):
    def __init__(self, label, atomic_number, mass):
        super().__init__(label)
        self.atomicNumber = atomic_number
        self.mass = mass

    def getAtomicNumber(self):
        return self.atomicNumber

    def getMass(self):
        return self.mass


class Element(BaseClass):
    def __init__(self, label, nuclidedict):
        super().__init__(label)
        tot = sum([massabundance for massabundance in nuclidedict.values()])
        if abs(tot-1) > 1e-6:
            print('Warning! the sum of nuclide {:} abundance is {:} does not add up to 1!'.format(
                self.getLabel(), tot))
            print('The abundance is going to be normalized!')
        for nuclide, massabundance in nuclidedict.items():
            nuclidedict[nuclide] = massabundance/tot
        self.nuclidedict = nuclidedict

    def getNuclide(self):
        return self.nuclidedict

    def getActomicAbundance(self):
        actomic_abudance_dic = {}
        totmolar = sum([massabundance/nuclide.getMass() for nuclide, massabundance 
        in self.nuclidedict.items()])
        for nuclide, massabundance in self.nuclidedict.items():
            actomic_abudance_dic[nuclide] = massabundance/nuclide.getMass() / totmolar
        return actomic_abudance_dic

    def getMass(self):
        mass = 0
        tot = 0
        actomic_abudance_dic = self.getActomicAbundance()
        for nuclide, abudance in actomic_abudance_dic.items():
            tot += abudance
            mass += nuclide.getMass() * abudance
        mass = mass / tot 
        return mass


class Compound(BaseClass):
    def __init__(self, lable, elementdict, p_a, p_b):
        super().__init__(lable)
        self.elementdict = elementdict
        self.p_a = p_a
        self.p_b = p_b
        mass = 0
        for key, item in self.elementdict.items():
            mass += key.getMass() * item
        self.mass = mass

    def getElement(self):
        return self.elementdict

    def getMass(self):
        return self.mass
        
    def getDensity(self, temp):
        """
           Bashed on this density computational function:
               pro = p_a - p_b * T (k)
        """
        return self.p_a - self.p_b * temp 
        
    def getMolarVolume(self, temp):
        return self.mass / self.getDensity(temp)


class Material(BaseClass):
    def __init__(self, lable, compounddict, temp):
        super().__init__(lable)
        self.compounddict = compounddict
        self.temp = temp

    def getCompound(self):
        return self.compounddict

    def getDensity(self):
        mass = 0
        volum = 0
        for key, item in self.compounddict.items():
            mass += key.getMass() * item
            volum += key.getMolarVolume(self.temp) * item

        return mass / volum

    def toMcnpCard(self):
        nuclide_compostion_in_material_dict = self.getNuclideFactionsInMaterial()
        return self.nuclideCompostionConvert2McnpFormat(nuclide_compostion_in_material_dict)   
    
    def nuclideCompostionConvert2McnpFormat(self, nuclide_compostion_in_material_dict):
        normalize_constant = abs(sum(nuclide_compostion_in_material_dict.values()))
        lines = ''
        for nuclide, fraction in nuclide_compostion_in_material_dict.items():
            if fraction != 0:
                line = "{:}{:}.{:<12}  {:<12.6e}\n".format(nuclide.getAtomicNumber(),
                    self.mcnpNuclideNotation(nuclide.getLabel()), self.chooselib(self.temp), fraction/normalize_constant)
                lines += line 

        return lines 

    def getElementCompostionInMaterial(self):
        element_compostion_in_material_dict = {}
        for compound, compound_ratio in self.compounddict.items():
            try:
                element_in_compound_dict = compound.getElement()
            except AttributeError:
                # for case of a material composed of elements only.
                for element, element_ratio in self.compounddict.items():
                    # in this case mass fraction are used which is negative.
                    element_compostion_in_material_dict[element] = element_ratio*-1
            else:
                # for case of a material composed of compounds.
                for element, element_ratio in element_in_compound_dict.items():
                    is_new_element = True # is or is't new element in element_in_compound_dict
                    if element.getLabel() in [element.getLabel() for element in
                    element_compostion_in_material_dict.keys()]:
                        is_new_element = False
                        element_compostion_in_material_dict[element] += element_ratio*compound_ratio
                    if is_new_element:
                        element_compostion_in_material_dict[element] = element_ratio*compound_ratio
        return element_compostion_in_material_dict
        
    def getNuclideMassFactionsInMaterial(self):
        element_compostion_in_material_dict = self.getElementCompostionInMaterial()
        nuclide_compostion_in_material_dict = {}
        for element, ratio in element_compostion_in_material_dict.items():
            nuclide_dict = element.getNuclide()  
            for nuclide in nuclide_dict.keys():
                nuclide_compostion_in_material_dict[nuclide] = ratio*nuclide_dict[nuclide]
        return nuclide_compostion_in_material_dict
    
    def getNuclideActiomicFactionsInMaterial(self):
        element_compostion_in_material_dict = self.getElementCompostionInMaterial()
        nuclide_compostion_in_material_dict = {}
        for element, ratio in element_compostion_in_material_dict.items():
            nuclide_dict = element.getNuclide()  
            actomic_abundance_dict = element.getActomicAbundance()     
            for nuclide in nuclide_dict.keys():
                print(ratio, actomic_abundance_dict[nuclide])
                nuclide_compostion_in_material_dict[nuclide] = ratio*actomic_abundance_dict[nuclide]
        return nuclide_compostion_in_material_dict
    
    def getNuclideFactionsInMaterial(self):
        compound_or_element = self.compounddict.keys()
        try:
            compound_or_element.getElement() 
        except AttributeError:
            return self.getNuclideMassFactionsInMaterial()
        else:
            return self.getNuclideActiomicFactionsInMaterial()
                    
    def mcnpNuclideNotation(self, nuclidelabel):
        lists = [''.join(list(g)) for k, g in groupby(nuclidelabel, key=lambda x: x.isdigit())]
        if len(lists[1]) == 1:
            return '00'+lists[1]
        elif len(lists[1]) == 2:
            return '0'+lists[1]
        elif len(lists[1]) == 3:
            return lists[1]
        else:
            return -1

    def chooselib(self, tem):
        mcnplib = {300:'30c',400:'40c',500:'50c',600:'60c',700:'70c',750:'75c'\
            ,800:'80c',820:'82c',840:'84c',860:'86c',870:'87c',880:'88c',900:'90c'\
            ,920:'92c',940:'94c',960:'96c',980:'98c',1000:'10c',1050:'05c'\
            ,1100:'11c',1200:'12c',1300:'13c',1400:'14c',1500:'15c',1600:'16c'\
            ,1700:'17c',1800:'18c',1900:'19c',2000:'20c',2100:'21c',2200:'22c'} 
        liblist = [300,400,500,600,700,750,800,820,840,860,870,880,900,920,940,960,980,1000,1050\
            ,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200]
        ii = 0
        if tem > 2200 or tem < 300:
            raise Exception("temperature is out of range")       
        else:
            for ii in range(len(liblist)):
                delttem = tem - liblist[ii]
                if delttem > 0:
                    ii = ii + 1
                else:
                    break
            if abs(tem - liblist[ii])>abs(tem - liblist[ii-1]):         
                return mcnplib[liblist[ii-1]]
            else:
                return mcnplib[liblist[ii]]

 


if __name__ == '__main__':
    
    u235 = Nuclide('U235', 92, 235.043923)
    u233 = Nuclide('U233', 92, 233.043923)
    u238 = Nuclide('U238', 92, 238.050783)
    th232 = Nuclide('Th232', 90, 232.03805)
    pu238 = Nuclide('Pu238', 94, 238.0)
    pu239 = Nuclide('Pu239', 94, 239.0)
    pu240 = Nuclide('Pu240', 94, 240.0)
    pu241 = Nuclide('Pu241', 94, 241.0)
    pu242 = Nuclide('Pu242', 94, 242.0)
    f19 = Nuclide('F19', 9, 18.998403)
    be9 = Nuclide('Be9', 4, 9.012182)
    li6 = Nuclide('li6', 3, 6.015122)
    li7 = Nuclide('li7', 3, 7.016004)
    cl37 = Nuclide('cl37', 17, 36.965903)
    mg24= Nuclide('mg24', 12, 23.985042)
    mg25= Nuclide('mg25', 12, 24.985837)
    mg26= Nuclide('mg26', 12, 25.982593)
    na23 = Nuclide('na23', 11, 22.989770)
    udict = {u235:19.75, u238:80.25}
    # udict = {u233:1}
    lidict = {li6:0.0005, li7:0.9995}
    fdict = {f19:1}
    cldict = {cl37:1}
    pudict = {pu238:0.019497, pu239:0.5875682, pu240:0.2371, pu241:0.10133776, pu242:0.05449704}
    mgdict = {mg24:0.7899, mg25:0.10, mg26:0.1101}
    nadict = {na23:1}
    cl = Element('Cl', cldict)
    u = Element('U', udict)
    f = Element("F", fdict)
    li = Element("Li", lidict)
    th = Element("Th", {th232:1})
    be = Element("Be", {be9:1})
    pu = Element("Pu", pudict)
    
    mg = Element("Mg", mgdict)
    na = Element("Na", nadict)
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
    # matdict = {nacl:10, pucl3:6, thcl4:4}
    # matdict = {nacl:55, ucl3:25, thcl4:20}
    matdict = {lif:0.6529, bef2:0.2873, thf4:0, uf4:0.0598}
    # 'label' 'matdict' 'temp'
    mat = Material('mat1', matdict, 973.15)
    # print(uf4.getActomicMass())
    # print(thf4.getActomicMass())
    print(mat.getDensity())
    print(mat.toMcnpCard())


    

