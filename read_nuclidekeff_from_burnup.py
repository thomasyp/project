from tool.mcnp_reader import McnpTallyReader
from pathlib import Path, PurePath
from collections import defaultdict


mtr = McnpTallyReader()
loopdic = {1:4, 2:5, 3:20}
path = Path('D:\work\mcnpxwork\博士课题\msasd\氯盐堆\\r150\850500OUT')
basefilename = '850500o'

keffofnuclide = defaultdict(lambda : 0)
nuclidelist = ['94238', '94239', '94240', '94241', '94242', '90232', '92235', '91233', '92233']
for nuclide in nuclidelist:
    keffofnuclide[nuclide] = []
for key in loopdic.keys():
    for ii in range(loopdic[key]):
        filename = '-'.join([basefilename, str(key), str(ii+1)])
        print('read file {:}\n'.format(filename))
        for nuclide in nuclidelist:
            keffofnuclide[nuclide].append(mtr.getNuclideKeff(PurePath.joinpath(path, filename), '4', '1', nuclide))
           
print(keffofnuclide)

