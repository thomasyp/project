'''
Created on 2015/9/28

@author: Thomas
'''
#!/user/bin/env python

def chooselib(tem):
    mcnplib = {300:'30c',400:'40c',500:'50c',600:'60c',700:'70c',750:'75c'\
          ,800:'80c',820:'82c',840:'84c',860:'86c',870:'87c',880:'88c',900:'90c'\
          ,920:'92c',940:'94c',960:'96c',980:'98c',1000:'10c',1050:'05c'\
          ,1100:'11c',1200:'12c',1300:'13c',1400:'14c',1500:'15c',1600:'16c'\
          ,1700:'17c',1800:'18c',1900:'19c',2000:'20c',2100:'21c',2200:'22c'} 
    mcnpths = {300:'30t',400:'40t',500:'50t',600:'60t',700:'70t',750:'75t'\
          ,800:'80t',820:'82t',840:'84t',860:'86t',870:'87t',880:'88t',900:'90t'\
          ,920:'92t',940:'94t',960:'96t',980:'98t',1000:'10t',1050:'05t'\
          ,1100:'11t',1200:'12t',1300:'13t',1400:'14t',1500:'15t',1600:'16t'\
          ,1700:'17t',1800:'18t',1900:'19t',2000:'20t',2100:'21t',2200:'22t'}
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
            return (mcnplib[liblist[ii-1]], mcnpths[liblist[ii-1]])
        else:
            return (mcnplib[liblist[ii]], mcnpths[liblist[ii]])
