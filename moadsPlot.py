import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os  
import re

#  MOLARMASS= {'902270':227,'902280':228,'902290':229,'902300':230,'902320':232.03805,'902330':233,'902340':234
#        ,'912310':231.035879,'912320':232,'912330':233
#        ,'922320','922330','922340','922350','922360','922370','922380','922390','922400'
#        ,'932350','932360','932370','932380','932390'
#        ,'942360','942370','942380','942390','942400','942410','942420','942430','942440','942460'
#        ,'952410','952420','952430','952440','952421','952441'
#        ,'962410','962420','962430','962440','962450','962460','962470','962480'
#        ,'972490'
#        ,'982490','982500','982510','982520'
#        ,'892270','892260','892250'
#        ,'882260','882250','882240','882230'
#        ,'832090'
#        ,'822080','822070','822060','822040'
#        ,'802040','802020','802010','802000','801990','801980','801960'
#        ,'791970'
#        ,'771930','771910'
#        ,'751870','751850'
#        ,'741860','741840','741830','741820'
#        ,'731810'
#        ,'721800','721790','721780','721770','721760','721740'
#        ,'711760','711750'
#        ,'681700','681680','681670','681660','681640','681620'
#        ,'671660','671650'
#        ,'661640','661630','661620','661610','661600','661580','661560'
#        ,'651600','651590'
#        ,'641600','641580','641570','641560','641550','641540','641520'
#        ,'631570','631560','631550','631540','631530','631520','631510'
#        ,'621540','621530','621520','621510','621500','621490','621480','621470','621440'
#        ,'611510','611490','611480','611470','611481'
#        ,'601500','601480','601470','601460','601450','601440','601430','601420'
#        ,'591430','591420','591410'
#        ,'581440','581430','581420','581410','581400'
#        ,'571400','571390'
#        ,'561400','561380','561370','561360','561350','561340'
#        ,'551370','551360','551350','551340','551330'
#        ,'541360','541350','541340','541330','541320','541310','541300','541290','541280','541260','541240'
#        ,'531350','531310','531300','531290','531270'
#        ,'521320','521300','521290','521280','521270','521260','521250','521240','521230','521220','521200','521271','521291'
#        ,'511260','511250','511240','511230','511210'
#        ,'501260','501250','501240','501230','501220','501200','501190','501180','501170','501160','501150','501140','501120'
#        ,'491150','491130'
#        ,'481160','481150','481140','481130','481120','481110','481100','481080','481060','481151'
#        ,'471110','471090','471070','471101'
#        ,'461100','461080','461070','461060','461050','461040','461020'
#        ,'451050','451030'
#        ,'441050','441040','441030','441020','441010','441000','440990','440980','440960'
#        ,'430990'
#        ,'421000','420990','420980','420970','420960','420950','420940','420920'
#        ,'410950','410940','410930'
#        ,'400960','400950','400940','400930','400920','400910','400900'
#        ,'390910','390900','390890'
#        ,'380900','380890','380880','380870','380860','380840'
#        ,'370870','370860','370850'
#        ,'360860','360850','360840','360830','360820','360800','360780'
#        ,'350810','350790'
#        ,'340820','340800','340780','340790','340770','340760','340740'
#        ,'330750','330740'
#        ,'320760','320740','320730','320720','320700'
#        ,'310710','310690'
#        ,'290650','290630'
#        ,'280640','280620','280610','280600','280590','280580'
#        ,'270590','270580'
#        ,'260580','260570','260560','260540'
#        ,'250550'
#        ,'240540','240530','240520','240500'
#        ,'220500','220490','220480','220470','220460'
#        ,'210450'
#        ,'200480','200460','200440','200430','200420','200400'
#        ,'190410','190400','190390'
#        ,'180400','180380','180360'
#        ,'170370','170350'
#        ,'160360','160340','160330','160320'
#        ,'150310'
#        ,'140300','140290','140280'
#        ,'130270'
#        ,'120260','120250','120240'
#        ,'110230'
#        ,'90190'
#        ,'80170','80160'
#        ,'70150','70140'
#        ,'60000'
#        ,'50110','50100'
#        ,'40090'
#        ,'30070','30060'
#        ,'20040','20030'
#        ,'10030','10020','10010'
#  }

class Moadsploter(object):
    def __init__(self):
        pass
    
    def readData(self, folderPath, matfileName):
        if folderPath[-1] != '\\':
            folderPath += '\\' 
        resultsFilename = folderPath + 'MOBATADS.OUT'

        with open(resultsFilename, 'r') as fid:
            for eachline in fid:
                title = eachline
                break
        
        namelists = re.split("\s{2,}", title.strip())
        self.timetag = namelists[1]
        namelists.insert(1, 'dummy')
        
        # print(pd.read_csv(resultsFilename))
        self.results = pd.read_csv(resultsFilename, sep='\s+', usecols=lambda x: x not in ['dummy'], skiprows=1, header=None, names=namelists)

        mafileName = folderPath + matfileName
        self.matdata = pd.read_csv(mafileName, sep='\s+', nrows=self.results.shape[0])
        
        self.matdata[self.timetag] = self.results[self.timetag] 
        self.pername = folderPath.split('\\')[-2]
        self.perplotmatname = matfileName
       

    def plotKeff(self, **kw):
        defaultDic = {}
        defaultDic['linewidth'] = 2.0
        defaultDic['xlim'] = [self.results.iloc[0,1], self.results.iloc[-1,1]]
        defaultDic['logx'] = False
        defaultDic['marker'] = 'o'
        for key, value in defaultDic.items():
            if key in kw.keys():
                pass
            else:
                kw[key] = value
        tag = None
        # find the column name of keff        
        for name in self.results.columns:
            if re.search('keff', name, re.I) is not None:
                tag = name
                break
        if tag is None:
            return 0

        ax = self.results.plot(x=self.timetag, y=[tag], **kw)
        plt.xlabel('$Time \ (days)$', fontsize=15)
        plt.ylabel('$Keff$', fontsize=15)
        plt.show()
        fig = ax.get_figure()
        figname = self.pername + '_keff.jpg'
        fig.savefig(figname)
        
        return 1
    
    def plotBeamIntensity(self, **kw):
        defaultDic = {}
        defaultDic['linewidth'] = 2.0
        defaultDic['xlim'] = [self.results.iloc[0,1], self.results.iloc[-1,1]]
        defaultDic['logx'] = False
        defaultDic['marker'] = 'o'
        for key, value in defaultDic.items():
            if key in kw.keys():
                pass
            else:
                kw[key] = value
        
        tag = None
        for name in self.results.columns:
            if re.search('beam', name, re.I) is not None:
                tag = name
                break
        if tag is None:
            return 0

        ax = self.results.plot(x=self.timetag, y=[tag], **kw)
        plt.xlabel('$Time \ (days)$', fontsize=15)
        plt.ylabel('$Beam \ Intensity \ (mA)$', fontsize=15)
        plt.show()
        fig = ax.get_figure()
        figname = self.pername + '_beamintensity.jpg'
        fig.savefig(figname)
        return 1
    
    def plotNeutronImportance(self, **kw):
        defaultDic = {}
        defaultDic['linewidth'] = 2.0
        defaultDic['xlim'] = [self.results.iloc[0,1], self.results.iloc[-1,1]]
        defaultDic['logx'] = False
        defaultDic['marker'] = 'o'
        for key, value in defaultDic.items():
            if key in kw.keys():
                pass
            else:
                kw[key] = value

        tag = None
        for name in self.results.columns:
            if re.search('importance', name, re.I) is not None:
                tag = name
                break
        
        if tag is None:
            return 0

        ax = self.results.plot(x=self.timetag, y=[tag], **kw)
        plt.xlabel('$Time \ (days)$', fontsize=15)
        plt.ylabel('$Neutron \ Importance$', fontsize=15)
        plt.show()
        fig = ax.get_figure()
        figname = self.pername + '_neutronimportance.jpg'
        fig.savefig(figname)
        return 1

    def plotSourcestrength(self, **kw):
        defaultDic = {}
        defaultDic['linewidth'] = 2.0
        defaultDic['xlim'] = [self.results.iloc[0,1], self.results.iloc[-1,1]]
        defaultDic['logx'] = False
        defaultDic['marker'] = 'o'
        for key, value in defaultDic.items():
            if key in kw.keys():
                pass
            else:
                kw[key] = value
        tag = None
        for name in self.results.columns:
            if re.search('source', name, re.I) is not None:
                tag = name
                break
        if tag is None:
            return 0

        ax = self.results.plot(x=self.timetag, y=[tag], **kw)
        plt.xlabel('$Time \ (days)$', fontsize=15)
        plt.ylabel('$Source \ strength$', fontsize=15)
        plt.show()
        fig = ax.get_figure()
        figname = self.pername + '_sourcestrength.jpg'
        fig.savefig(figname)
        return 0
    
    def plotMat(self, *matname, **kw):
        defaultDic = {}
        defaultDic['linewidth'] = 2.0
        defaultDic['xlim'] = [self.results.iloc[0,1], self.results.iloc[-1,1]]
        defaultDic['logx'] = False
        defaultDic['logy'] = False
        
        
        if 'yunit' in kw.keys():
            yunit = kw.pop('yunit')
            
        if 'foldername' in kw.keys():
            foldername = kw.pop('foldername')
            
        for key, value in defaultDic.items():
            if key in kw.keys():
                pass
            else:
                kw[key] = value
        data = pd.DataFrame(columns=['time'])

        if 'mass' == yunit.lower():
            for name in matname:
                molarmass = float(name[-4:-1])
                data[name] = self.matdata[name] * molarmass * 1e-3
                ylabels = '$Mass \ (kg)$'
        elif 'moore' == yunit.lower():
            data = self.matdata[list(matname)]
            ylabels = '$Moore \ (mol)$'
        else:
            print("error!")
            exit(1)

        data[self.timetag ] = self.matdata[self.timetag]
        data.to_csv(foldername + 'mat.csv')
        ax = data.plot(x=self.timetag , y=list(matname), **kw)
        plt.xlabel('$Time \ (days)$', fontsize=15)
        plt.ylabel(ylabels, fontsize=15)
        plt.show()
        fig = ax.get_figure()
        figname = self.pername + '_' + self.perplotmatname+ '.jpg'
        fig.savefig(figname)

if __name__ == '__main__':
    path = os.path.abspath('.')
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs='?', help="MOADS results folder.")
    parser.add_argument("nuclides", nargs='+', help="Nuclides to plot.")
    parser.add_argument("--niylim", nargs='+', help="ylim of Neutron Importance plot.", type=float)
    parser.add_argument("--matunit", nargs='?', help="unit of mat plot.", default='mass')
    args = parser.parse_args()
    pathoffolder =  path + '\\' + args.folder
    #print(pathoffolder)
    #print(args.nuclides)
    #print(args.niylim)
    mp = Moadsploter()
    mp.readData(pathoffolder, 'MAT1')
    mp.plotKeff(marker='o', color='r')
    mp.plotBeamIntensity(marker='*', color='g')
    mp.plotNeutronImportance(marker='+', color='b', ylim=args.niylim)
    mp.plotMat(*args.nuclides, yunit=args.matunit, foldername=args.folder)
    mp.plotSourcestrength(marker='.', color='y')
    # mp = Moadsploter()
    # mp.readData('6rOUT', 'MAT1')
    # mp.plotKeff(marker='o', color='r')
    # mp.plotBeamIntensity(marker='*', color='g')


    