#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 09 14:56:21 2018

@author: yang
"""
import re
import numpy as np
import h5py
from collections import defaultdict
from tool.self_defined_exception import CustomError


class McnpTallyReader(object):
    def __init__(self):
        self.keyName = []

    def readSingleTally(self, filename, **kw):
        """
            Function: read results(spectrum format data) from mcnp output file
            Parameters: 1.mcnp output file
                        2.关键字参数
            Return: tally results.
        """
        readTag = {}
        datadict = {}
        for key in kw.keys():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []

        with open(filename, 'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == '1tally' and lists[2] == 'nps':
                        for key, tallyNum in kw.items():
                            if lists[1] == str(tallyNum):
                                readTag[key] = True
                            else:
                                readTag[key] = False
                    if len(lists) == 2:
                        for key, tallyNum in kw.items():
                            if readTag[key] is True:
                                if re.match('\d\.\d{5}E[+-]\d{2}', lists[0]) is not None:
                                    datadict[key] = lists

        return datadict

    def readSpectrum2dat(self, filename, **kw):
        """
            Function: read results(spectrum format data) from mcnp output file and write the data to
            a .dat file.
            Parameters: 1.mcnp output file
                        2.关键字参数
        """
        readTag = {}
        datadict = {}
        for key in kw.keys():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []

        with open(filename, 'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == 'total':
                        for key in readTag.keys():
                            readTag[key] = False

                    if len(lists) > 3:
                        if lists[0] == '1tally' and lists[2] == 'nps':
                            for key, tallyNum in kw.items():
                                if lists[1] == str(tallyNum):
                                    readTag[key] = True
                                    datadict[key] = []
                    for key, tallyNum in kw.items():
                        if readTag[key] is True:
                            if re.match('\d\.\d{4}E[+-]\d{2}', lists[0]) is not None:
                                datadict[key].append(eachline.strip())
#        print (datadict)
        for key, tallyNum in kw.items():
            datfilename = key + '.dat'
            with open(datfilename, 'w') as f:
                for row in datadict[key]:
                    f.write('{}\n'.format(row))

    def readLatticeData2dat(self, filename, **kw):
        """
            Function: read results(lattice format data) from mcnp output file and write the data to
            a .dat file.
            Parameters: 1.mcnp output file
                        2.关键字参数
        """
        readTag = {}
        datadict = {}
        for key in kw.keys():
            self.keyName.append(key)
            readTag[key] = False
            datadict[key] = []

        with open(filename, 'r') as fileid:
            for eachline in fileid:
                lists = eachline.strip().split()
                if len(lists) > 0:
                    if lists[0] == 'there':
                        for key in readTag.keys():
                            readTag[key] = False

                if len(lists) > 3:
                    if lists[0] == '1tally' and lists[2] == 'nps':
                        for key, tallyNum in kw.items():
                            if lists[1] == str(tallyNum):
                                readTag[key] = True
                                datadict[key] = []

                for key, tallyNum in kw.items():
                    if readTag[key] is True:
                        if self.isLatticeTag(eachline):
                            datadict[key].append(eachline.strip())
                        if self.isLatticeData(eachline):
                            datadict[key].append(eachline.strip())

        for key, tallyNum in kw.items():
            datfilename = key + '.dat'
            with open(datfilename, 'w') as f:
                for row in datadict[key]:
                    f.write('{}\n'.format(row))

    def isLatticeData(self, strs):
        lists = strs.strip().split()
        if len(lists) > 1:
            if re.match('\d\.\d{4,5}E[+-]\d{2}', lists[0]) is not None:
                if re.match('\d.\d{4,5}$', lists[1]) is not None:
                    return True
        return False

    def isLatticeTag(self, strs):
        lists = strs.strip().split()
        if len(lists) > 0:
            if ('cell (' in strs) and ('[' and ']' in strs):
                return True
        return False

    def readKeff(self, filename):
        results = {}
        with open(filename, 'r') as fileid:
            for eachline in fileid:
                if "the final estimated combined collision" in eachline:
                    data = []
                    lists = eachline.strip().split()
                    for ii in lists:
                        if re.match('\d.\d{4,5}$', ii) is not None:
                            data.append(ii)
                if "the average number of neutrons produced per fission" in eachline:

                    lists = eachline.strip().split()
                    for ii in lists:
                        if re.match('\d.\d{2,3}$', ii) is not None:
                            results['v'] = ii
        if len(data) == 2:
            results['keff'] = float(data[0])
            results['error'] = float(data[1])
        else:
            return None
        return results

    def findPosInLine(self, line, reFormat):
        lists = line.strip().split()
        for num, string in enumerate(lists):
            if re.match(reFormat, string) is not None:
                return num
        return None
            

    def readFmeshDataIntoDic(self, meshtalFile, tallyNumber, groupNum, isWritetoHDF5, *dataType, **kwargs):
        """
        Fuction name:
            readFmeshDataIntoDic
        Fuction:
            读取原始meshtal 文件中的Energy,X,Y,Z,Result,Rel Error,Volume,
            Rslt * Vol等数据
        Input parameter:
            文件路径和文件名：meshtalFile
            需要读取的哪部分tally给出tally number：tally_number
            需要读取的哪个能群的数据：group
            是否需要写入到hdf5格式文件中：isWritetoHDF5(true 为写入)
            需要读取哪一列数据：*dataType
        Return:
            文件中的数据 dict：tallyDic
        """
        readtag = False
        dataArray = []
        namelists = []
        nx = 0
        ny = 0
        nz = 0
        ngroup = 0
        nline = 0
        totColumn = 0  # 选择读取数据的列号
        numMesh = 0

        nColumn = []

        if "Energy" in dataType:
            dataType = dataType[1:]

        try:
            meshFid = open(meshtalFile, 'r')
        except IOError as e:
            print("Error 11004: meshtal file open error: ", e)
            return -1
        else:
            print("Comment: Reading meshtal file...")
            for eachline in meshFid:
                if "Mesh Tally Number" in eachline:
                    lists = eachline.strip().split()
                    if lists[3] == tallyNumber:
                        readtag = True
                    else:
                        readtag = False
                if readtag:
                    lists = eachline.strip().split()
                    if nx*ny*nz*totColumn == 0:
                        if "X direction" in eachline or "R direction" in eachline:
                            nx = len(eachline[eachline.find(
                                ':')+1:].strip().split()) - 1

                        if "Y direction" in eachline or "Theta direction" in eachline:
                            ny = len(eachline[eachline.find(
                                ':')+1:].strip().split()) - 1

                        if "Z direction" in eachline:
                            nz = len(eachline[eachline.find(
                                ':')+1:].strip().split()) - 1

                            # startline = (groupNum - 1) * numMesh + 1

                        if "Rel Error" in eachline:
                            indx = lists.index("Rel")
                            del lists[indx]
                            lists[indx] = "Rel Error"
                            indx = lists.index("Rslt")
                            del lists[indx:indx+2]
                            lists[indx] = "Rslt * Vol"
                            namelists.extend(lists)
                            totColumn = len(lists)
                            for ii in dataType:

                                if ii not in namelists:
                                    print(
                                        "Error 11010: The meshtal file have not the data type: %s" % ii)
                                    return -1
                                nColumn.append(namelists.index(ii))
                            # print(nColumn)
                    else:

                        nline = nline + 1

                        if lists:
                            datalists = []

                            for ii in nColumn:
                                datalists.append(float(lists[ii]))

                            dataArray.append(datalists)

            numMesh = nx * ny * nz
            print('{} {} {}'.format(nx, ny, nz))

            totlines = len(dataArray)
            ngroup = totlines / numMesh  # compute the num of groups.

            if groupNum > ngroup:
                print("Error 11015: Input group number is out of range!")
                return -1

            startid = numMesh * (groupNum - 1)
            endid = numMesh * groupNum
            n = len(nColumn)
            arrays = [[y[x] for y in dataArray[startid:endid]]
                      for x in range(n)]
            tallyDic = {dataType[i]: np.array(
                arrays[i]) for i in range(len(arrays))}
            if isWritetoHDF5:
                self.write2HDF5('biasedtaly.hdf5', tallyDic, nx, ny, nz)
            return tallyDic

    def write2HDF5(self, hdfFileName, data, *dimension):
        """
        Fuction name:
            write2HDF5
        Fuction:
            读取dict 数据并存入hdf5格式文件中,
            Rslt * Vol等数据
        Input parameter:
            需要写入的hdf5文件名：hdfFileName
            需要读取的 dict 数据：data
            写入数据数组维数设置：dimension
        Return:
            0
        """

        with h5py.File(hdfFileName, "w") as f:
            for key in data.keys():
                f[key] = data[key].reshape(dimension)

        return 0

    def readMdataIntoHDF5(self, source, mdataFileName, hdfFileName):
        """
        Fuction name:
            readMdataIntoHDF5
        Fuction:
            读取dict 数据并存入hdf5格式文件中,
            Rslt * Vol等数据
        Input parameter:
            需要读取的 mdata文件名：mdataFileName
            需要写入的 hdf5文件名：hdfFileName

        Return:
            0
        """
        nlines = 0
        dimension = []
        nxnynz = []
        headerdata = []
        lenthofHeader = 19 + 2 + 2
        nx = 0
        ny = 0
        nz = 0
        xcord = []
        ycord = []
        zcord = []
        tallyName = None
        readDataTag = False
        data = []
        readid = 0
        isNewTallySegment = True
        methType = []  # '1'表示rectangular mesh；'2'表示cylindrical mesh；'3'表示spherical meshes
        grouplists = [] # group name in hdf5 file

        with open(mdataFileName, 'r') as fid, h5py.File(hdfFileName, "w") as hdfid:
            for eachline in fid:
                nlines = nlines + 1
                lists = eachline.strip().split()
                # 读取tally的总数
                if nlines == 1:
                    tallyName = lists[:2]
                if nlines == 2:
                    numtallys = int(lists[0])
                    for ii in range(numtallys):
                        groupname = ''.join(tallyName + [str(ii + 1)])
                        hdfid.create_group(groupname)
                    totHeaderLenth = numtallys * lenthofHeader + 1

                if readDataTag:
                    #print(methType)
                    if isNewTallySegment:
                        nx = nxnynz[readid][0]
                        ny = nxnynz[readid][1]
                        nz = nxnynz[readid][2]
                        # rectangular mesh : 网格数据个数为(nx - 1) * (ny - 1) * (nz - 1)
                        if methType[readid] == '1':
                            nmeshs = (nx - 1) * (ny - 1) * (nz - 1)
                            dimension = [int(nx - 1), int(ny - 1), int(nz - 1)]
                            hdfid[grouplists[readid]].create_dataset(
                                'dimension', data=dimension)
                        # cylindrical mesh: nz 为角向，0到360
                        elif methType[readid] == '2':
                            nmeshs = (nx - 1) * (ny - 1) * nz
                            dimension = [int(nx - 1), int(ny - 1), int(nz)]
                            hdfid[grouplists[readid]].create_dataset(
                                'dimension', data=dimension)
                        # spherical mesh: ny 为角向，0到180; nz 为角向，0到360
                        elif methType[readid] == '3':
                            nmeshs = (nx - 1) * ny * nz
                            dimension = [int(nx - 1), int(ny), int(nz)]
                            hdfid[grouplists[readid]].create_dataset(
                                'dimension', data=dimension)
                        else:
                            self.errorMessage('Error: The mesh type is {}, not supported!'.format(methType[readid]))
                            return -1
                        readid += 1
                        data = []
                        isNewTallySegment = False
                    data += lists
                    lenth = len(data)
                    # 写入coordinates
                    if lenth == sum([nx, ny, nz]):
                        xcord = data[:nx]
                        ycord = data[nx:nx+ny]
                        zcord = data[nx+ny:]
                        dd = [float(x) for x in xcord]
                        hdfid[grouplists[readid-1]].create_dataset('XCoordinate', data=dd)
                        dd = [float(x) for x in ycord]
                        hdfid[grouplists[readid-1]].create_dataset('YCoordinate', data=dd)
                        dd = [float(x) for x in zcord]
                        hdfid[grouplists[readid-1]].create_dataset('ZCoordinate', data=dd)
                    # 写入统计结果和误差
                    if isNewTallySegment == False and lenth == sum([nx, ny, nz, 2*nmeshs]):
                        arrd =  [float(x) * source for x in data[sum([nx, ny, nz]):sum([nx, ny, nz, nmeshs])]]
                        dd = np.array(arrd).reshape(dimension[0], dimension[1], dimension[2])
                        hdfid[grouplists[readid-1]].create_dataset('data', data=dd)
                        arrd = [float(x) for x in data[sum([nx, ny, nz, nmeshs]):]]
                        dd = np.array(arrd).reshape(dimension[0], dimension[1], dimension[2])
                        hdfid[grouplists[readid-1]].create_dataset('error', data=dd)
                        isNewTallySegment = True

                if nlines > 2 and not readDataTag:
                    headerdata += lists
                    lenth = len(headerdata)
                    if lenth == totHeaderLenth:
                        grouplists = [x for x in hdfid]
                        for ii in range(numtallys):
                            dd = [int(x) for x in headerdata[ii *
                                                             lenthofHeader+3:ii*lenthofHeader+6]]
                            nxnynz.append(dd)
                            methType.append(headerdata[ii*lenthofHeader+1][0])
                        readDataTag = True

        # print(data)

    def errorMessage(self, strs):
        print("Error: {:}!".format(strs))


    def readNeutronActivity(self, outfile, cell=None, nuclides=None):
        """
        Fuction:
            读取mcnp输出文件中的俘获率，泄漏率以及裂变率（归一到一个源中子）
            case1: cell=None, nuclides=None 返回 总的俘获率，泄漏率以及裂变率（loss to fission）;
            case2: cell!=None, nuclides=None 返回 cell内的俘获率;
            case3: cell!=None, nuclides!=None 返回 cell内 的nulides 的俘获率, wgt. gain by fission, wgt. gain by (n,xn);
            case4: cell=None, nuclides!=None 返回 nulides 的俘获率, wgt. gain by fission, wgt. gain by (n,xn);

        Input parameter:
            需要读取的 mcnp输出文件名：outfile
            需要读取俘获率的 cell 类型为lists
            需要读取俘获率的 nuclides 类型为lists
        Return:
            case1:返回俘获率，泄漏率以及裂变率，'photonuclear', '(n,xn)', 'loss to (n,xn)', 'prompt fission', 'delayed fission'。返回类型为字典
            case2,3,4:仅返回俘获率，返回类型为字典
        """
        if nuclides:
            try:
                if type(nuclides) != list:
                    raise CustomError('Input type of nuclides should be list!')
            except TypeError as e:
                print(e)
                return -1
        results = {}
        tag  = False
        physical_quantity_to_be_read = ['escape', 'loss to fission', 'capture', \
            'photonuclear', '(n,xn)', 'loss to (n,xn)', 'prompt fission', 'delayed fission', 'nucl. interaction']
        if cell is None and nuclides is None:
            with open(outfile, 'r') as fid:
                for eachline in fid:
                    lists = eachline.strip().split()
                    if 'neutron creation' in eachline:
                        tag = True
                    if 'photon creation' in eachline:
                        tag = False
                    if tag:
                        for physiclquantity in physical_quantity_to_be_read:                            
                            if 'total' in eachline:
                                tag = False
                            elif physiclquantity in eachline:
                                if physiclquantity == 'loss to fission':
                                    results['lossfission'] = float(lists[lists.index('loss')+4])
                                elif physiclquantity == 'loss to (n,xn)':
                                    results['loss(n,xn)'] = float(lists[lists.index('loss')+4])
                                elif physiclquantity == 'prompt fission':
                                    results['pfission'] = float(lists[lists.index('prompt')+3])
                                elif physiclquantity == 'delayed fission':
                                    results['dfission'] = float(lists[lists.index('delayed')+3])
                                elif physiclquantity == 'nucl. interaction':
                                    if lists[0] == 'nucl.':
                                        results['nuclinteraction'] = float(lists[lists.index('interaction')+2])
                                    else:
                                        results['lossnuclinteraction'] = float(lists[lists.index('interaction')+2])
                                else:
                                    results[physiclquantity] = float(lists[lists.index(physiclquantity)+2])
                            else:
                                pass

            return results
        # cell is not None and nuclides is None:
        elif nuclides is None:
            start = 0
            content = []
            capturelists = []
            with open(outfile, 'r') as fid:
                for eachline in fid:
                    lists = eachline.strip().split()
                    if "neutron activity of each nuclide in each cell, per source particle" in eachline:
                        tag = True
                    if "total" in eachline and lists[0] == 'total':
                        tag = False
                    if tag:
                        content.append(lists)

            for ind, ll in enumerate(content):
                if ll and ll[1] == str(cell):
                    start = ind
            try:
                if start == 0:
                    raise CustomError('Cell {:} not found!'.format(cell))
            except TypeError as e:
                print(e)
                return -1

            for ind, ll in enumerate(content[start:]):
                if ll:
                    if ind == 0:
                        capturelists.append(float(ll[6]))
                    else:
                        capturelists.append(float(ll[4]))
                else:
                    break

            results['capture'] = np.array(capturelists).sum()
            return results

        # cell is None and nuclides is not None:
        elif cell is None:
            results = {}
            content = []
            for nuclide in nuclides:
                results[str(nuclide)] = defaultdict(lambda: 0)
            
            with open(outfile, 'r') as fid:
                for eachline in fid:
                    lists = eachline.strip().split()
                    if "total over all cells by nuclide" in eachline:
                        tag = True
                    if tag:
                        if len(lists) == 9 and lists[1].isnumeric():
                            # print(lists)
                            content.append(lists)
                        if content and len(lists) != 9:
                            tag = False

            for ll in content:
                for nuclide in nuclides:
                    if str(nuclide) in ll[0]:
                        results[str(nuclide)]['capture'] = float(ll[3])
                        results[str(nuclide)]['fission'] = float(ll[4])
                        results[str(nuclide)]['n,xn'] = float(ll[5])
                    # else:
                    #     results[str(nuclide)]['capture'] = 0

            return results

        # cell is not None and nuclides is not None:
        else:
            start = 0
            content = []
            capturelists = []
            results = {}
            for nuclide in nuclides:
                results[str(nuclide)] = defaultdict(lambda: 0)
            with open(outfile, 'r') as fid:
                for eachline in fid:
                    lists = eachline.strip().split()
                    if "neutron activity of each nuclide in each cell, per source particle" in eachline:
                        tag = True
                    if "total" in eachline and lists[0] == 'total':
                        tag = False
                    if tag:
                        content.append(lists)

            for ind, ll in enumerate(content):
                if ll and ll[1] == str(cell):
                    start = ind
            
            try:
                if start == 0:
                    raise CustomError('Cell {:} not found!'.format(cell))
            except TypeError as e:
                print(e)
                return -1

            content = content[start:]
            filtercontent = []
            for ind, ll in enumerate(content):
                if ll:
                    if ind == 0:
                        filtercontent.append(ll[2:])
                    else:
                        filtercontent.append(ll)
                else:
                    break

            for line in filtercontent:
                for nuclide in nuclides:
                    if str(nuclide) in line[0]:
                        results[str(nuclide)]['capture'] = float(line[4])
                        results[str(nuclide)]['fission'] = float(line[5])
                        results[str(nuclide)]['n,xn'] = float(line[6])
            return results

    def getCR(self, outfile):
        totratedic = self.readNeutronActivity(outfile)
        totfission = totratedic['lossfission']
        activitydic = self.readNeutronActivity(outfile, nuclides=['90232', '92234', '94240', '91233', '92238', '92233', '92235', '94239', '94241'])
        
        # CR=Rc(Th232 + U234 + U238 + Pu240 -Pa233) / Ra(U233 + U235 + Pu239 + Pu241)
        CR = (activitydic['90232']['capture'] + activitydic['92234']['capture'] + activitydic['94240']['capture'] \
            + activitydic['92238']['capture'] - activitydic['91233']['capture'])/(activitydic['92233']['capture'] + activitydic['92235']['capture'] \
                + activitydic['94239']['capture'] + activitydic['94241']['capture'] + totfission)
        print(CR)
        return CR

    def getNeutronYield(self, outfile):
        '''
        Fuction:
            读取mcnp输出文件中的neutron creation表，计算出中子产额。
            注：该函数主要用于质子打靶的中子产额计算，基于mcnpx输出文件。
           
        Input parameter:
            需要读取的 mcnp输出文件名：outfile
            
        Return:
            中子产额.返回类型float
            
        '''
        totratedic = self.readNeutronActivity(outfile)
        neutronyield = totratedic['nuclinteraction'] - totratedic['lossnuclinteraction'] + \
            totratedic['(n,xn)'] - totratedic['loss(n,xn)']
        return neutronyield

    def getNeutronWeightBalance(self, outfile, particleType='n'):
        '''
        Fuction:
            读取mcnp输出文件中的print table 130: weight balance in each cell
            注：该函数主要用于读取不同栅元内粒子的行为，包括发生的反应类型，泄露，进入等信息。
            
        Input parameter:
            需要读取的 mcnp输出文件名：outfile
            粒子类型：希望读取的粒子类型，支持：'n','h','pi_+'
        Return:
            返回类型dict
            
        '''
        
        supportparticletype = {'n':'neutron', 'h':'proton', 'pi_+':'pi_+'}
        if particleType not in supportparticletype.keys():
            self.errorMessage('Particle types are not supported!')
            return -1
        results = {'external events':{}, 'variance reduction events':{}, 'physical events':{}}
        external_events_data = []
        variance_reduction_events_data = []
        physical_events_data = []

        external_events_keys = []
        variance_reduction_events_keys = []
        physical_events_keys = []
        cellnum = []
        tag  = False
        readtagfor_external_events = False
        readtagfor_variance_reduction = False
        readtagfor_physical_events = False

        external_events_dic = {}
        variance_reduction_events_dic = {}
        physical_events_dic = {}

        
        with open(outfile, 'r') as fid:
            for eachline in fid:
                lists = eachline.strip().split()
                if not eachline[0].isspace():
                    tag = False
                if 'print table 130' in eachline and supportparticletype[particleType] in eachline:
                    tag = True
                    external_events_data = []
                    variance_reduction_events_data = []
                    physical_events_data = []
                    external_events_keys = []
                    variance_reduction_events_keys = []
                    physical_events_keys = []
                    cellnum = []

                if tag:
                    if 'cell number' in eachline:
                        # for cell in lists[2:]:
                        cellnum.append(lists[2:])
                    if 'external events' in eachline:
                        readtagfor_external_events = True
                        external_events_keys = []
                    if 'variance reduction events' in eachline:
                        readtagfor_variance_reduction = True
                        variance_reduction_events_keys = []
                    if 'physical events' in eachline:
                        readtagfor_physical_events = True
                        physical_events_keys = []
                    if lists and lists[0] == 'total':
                        readtagfor_external_events = False
                        readtagfor_variance_reduction = False
                        readtagfor_physical_events = False
                    if readtagfor_external_events:
                        indx =  self.findPosInLine(eachline, '-?\d\.\d{4,5}E[+-]\d{2}')
                        if indx is not None:
                            external_events_keys.append(' '.join(lists[:indx]))
                            external_events_data.extend([float(data) for data in lists[indx:]])
                    if readtagfor_variance_reduction:
                        indx =  self.findPosInLine(eachline, '-?\d\.\d{4,5}E[+-]\d{2}')
                        if indx is not None:
                            variance_reduction_events_keys.append(' '.join(lists[:indx]))
                            variance_reduction_events_data.extend([float(data) for data in lists[indx:]])
                    if readtagfor_physical_events:
                        indx =  self.findPosInLine(eachline, '-?\d\.\d{4,5}E[+-]\d{2}')
                        if indx is not None:
                            physical_events_keys.append(' '.join(lists[:indx]))
                            physical_events_data.extend([float(data) for data in lists[indx:]])
       
        
        for celllists in cellnum:
            for cell in celllists:
                external_events_dic[cell] = {}
                variance_reduction_events_dic[cell] = {}
                physical_events_dic[cell] = {}
        
        
        ind = 0
        for celllists in cellnum:
            for key in external_events_keys:
                for cell in celllists:
                    external_events_dic[cell][key] = external_events_data[ind]
                    ind += 1
        ind = 0
        for celllists in cellnum:
            for key in variance_reduction_events_keys:
                for cell in celllists:
                    variance_reduction_events_dic[cell][key] = variance_reduction_events_data[ind]
                    ind += 1
        ind = 0
        for celllists in cellnum:
            for key in physical_events_keys:
                for cell in celllists:
                    physical_events_dic[cell][key] = physical_events_data[ind]
                    ind += 1
        
        results['external events'] = external_events_dic
        results['variance reduction events'] = variance_reduction_events_dic
        results['physical events'] = physical_events_dic
        
        return results

    
    def getNuclideKeff(self, filename, cell, matnum, nuclide):
        '''
        Fuction:
            得到燃耗计算输出文件中不同核素对keff的贡献：
            计算公式为 keff(i) = Rf(i)*V(i)/sum(Rc(j))+L+sum(Rm(j))+sum(Rf(j))
            V为核素i的平均单词裂变中子数;L 为泄露率；Rf为裂变率；Rc为俘获率；Rm为(n,xn)反应反应率
        Input parameter:
            需要读取的 mcnp输出文件名：filename
            核素nuclide所在的栅元号：cell
            核素number：nuclide
        Return:
            返回类型float, keffbynuclide
            
        '''

        nuclidereactionratedic = self.readNeutronActivity(filename, cell=cell, nuclides=nuclide.strip().split())
        gainbyfissrate = nuclidereactionratedic[nuclide]['fission']    
        totreactionratedic = self.readNeutronActivity(filename)
        totfissionrate = totreactionratedic['lossfission']
        escaperate = totreactionratedic['escape']      
        totn_xnrate = totreactionratedic['loss(n,xn)']
        totcapturerate = totreactionratedic['capture']
        totlossrate = totfissionrate + escaperate + totn_xnrate + totcapturerate
        # print(totlossrate)
        nuclideatomdensity = self.getNuclideDensity(filename, cell, matnum, nuclide)
        # print(nuclideatomdensity)
        matcarddic = {}
        keywords = 'multiplier bin:   1.00000E+00'
        fissreactionnumber = '-6'
        tag = False
        cellvolume = self.getTallyVolume(filename, cell)
        with open(filename, 'r') as fid:
            for line in fid:
                contentlist = line.strip().split()
                if contentlist:
                    if re.match('\d{1,5}-', contentlist[0]) is not None:
                        if len(contentlist) > 3:
                            if re.match(nuclide+'.\d{2}c', contentlist[2]) is not None:
                                matcarddic[nuclide] = contentlist[1][1:]
        keywords = ' '.join([keywords, matcarddic[nuclide]])  
        fissreactionratecontent = ''                      
        with open(filename, 'r') as fid:
            for line in fid:
                contentlist = line.strip().split()
                if keywords in line and fissreactionnumber in line:
                    tag = True
                if line.isspace():
                    tag = False
                if tag:
                    fissreactionratecontent = ''.join([fissreactionratecontent, line])
        
        nuclidefissreactionrate = float(fissreactionratecontent.strip().split()[-2]) * nuclideatomdensity
        keffbynuclide = (nuclidefissreactionrate*cellvolume + gainbyfissrate) / (escaperate + totn_xnrate + totcapturerate + totfissionrate)
        return keffbynuclide


    def getTallyVolume(self, filename, cell):
        tag = False
        keywords = 'volumes'
        content = ''
        with open(filename, 'r') as fid:
            for line in fid:
                contentlist = line.strip().split()
                if contentlist and contentlist[0] == keywords:
                    tag = True
                if line.isspace():
                    tag = False
                if tag:
                    content = ''.join([content, line])
        contentlist = content.strip().split()
        return float(contentlist[contentlist.index(cell)+1])


    def readMaterialInfo(self, filename):
        '''
        Fuction:
            读取talbe 50 中的栅元的材料的密度、体积、质量等信息
            
        Input parameter:
            需要读取的 mcnp输出文件名：filename
            
        Return:
            返回类型dict, 栅元的材料密度体积等信息
            
        '''
        
        tag = False
        resultdic = defaultdict(lambda: 0)
        
        startkeywords = '1cell volumes and masses'
        endkeywords = '1surface areas'
        with open(filename, 'r') as fid:
            for line in fid:
                linelist = line.strip().split()
                if startkeywords in line:
                    tag = True
                if endkeywords in line:
                    tag = False
                if tag:
                    if linelist:
                        if linelist[0].isdecimal():
                            resultdic[linelist[1]] = linelist[2:7]
        
        return resultdic
        


    def getNuclideDensity(self, filename, cell, matnum, nuclide, mode='atom'):
        '''
        Fuction:
            计算得到某个核素的密度
            
        Input parameter:
            需要读取的 mcnp输出文件名：filename
            核素number：nuclide
            核素nuclide所在的材料号：matnum
            模式：mode 两种模式质量密度（mass） 和 原子数密度（atom）
        Return:
            返回类型float, 核素密度
            
        '''
             
        nuclidefractioninfo = self.readNuclideFraction(filename, mode)
        nuclidefraction = float(nuclidefractioninfo[matnum][nuclidefractioninfo[matnum].index(nuclide+',')+1])
        
        materialatomdensitydic = self.readMaterialInfo(filename)
        if mode == 'atom':
            return float(materialatomdensitydic[cell][0])*nuclidefraction
        else:
            return float(materialatomdensitydic[cell][1])*nuclidefraction


    def readNuclideFraction(self, filename, mode):
        '''
        Fuction:
            读取 table 40 中的核素份额
            
        Input parameter:
            需要读取的 mcnp输出文件名：filename
            模式：mode 两种模式质量密度（mass） 和 原子数密度（atom）
        Return:
            返回类型list, 核素份额
            
        '''

        try:
            if mode != 'atom' and mode != 'mass':
                raise CustomError('Mode should be mass or atom!')
        except TypeError as e:
            print(e)
            return -1

        if mode == 'atom':
            keywords = 'component nuclide, atom fraction'
        else:
            keywords = 'component nuclide, mass fraction'

        tag = False
        emptyline = 0
        contentlist = []
        content = ''
        with open(filename, 'r') as fid:
            for line in fid:
                if keywords in line:
                    tag = True
                if emptyline == 2:
                    tag = False
                if tag:
                    linelist = line.strip().split()
                    if linelist:
                        if emptyline == 1:
                            content = ''.join([content, line])
                    else:
                        emptyline += 1
        contentlist = content.strip().split()
        splitpos = []
        for ii, data in enumerate(contentlist):
            if data.isdecimal():
                splitpos.append(ii)
        splitpos.append(len(contentlist))
        result = defaultdict(lambda: 0)
        for ii in range(len(splitpos)-1):
            result[contentlist[splitpos[ii]]] = contentlist[(splitpos[ii]+1):splitpos[ii+1]]
            # result.append(contentlist[splitpos[ii]:splitpos[ii+1]])
        return result
               

       

if __name__ == '__main__':
    mtr = McnpTallyReader()
    # path = 'D:\\work\\mcnpxwork\\博士课题\\msasd\\氯盐堆\\扩大堆芯搜索\\微调\\120r60ko_40.00_6.70_53.30'
    path = 'D:\\work\\mcnpxwork\\博士课题\\msasd\\氯盐堆\\r150\\850500OUT\\850500o-1-1'
    # path = 'D:\\work\\mcnpwork\\lf1\\初步设计\\升版\\能量沉积\\dept.log'
    # path = 'D:\\work\\mcnpwork\\lf1\\初步设计\\核测\\base.log'
    # mtr.getCR(path)
    # test = mtr.readNeutronActivity(path, '4', ['94239'])
    # print(test)
    nuclidelist = ['94238', '94239', '94240', '94241', '94242', '90232']
    keff = 0
    for nuclide in nuclidelist:
        keffofnuclide = mtr.getNuclideKeff(path, '4', '1', nuclide)
        keff = keff + keffofnuclide
        print(keffofnuclide)
    print(keff)

    # volume = mtr.getTallyVolume(path, '4')
    # print(volume)
    # print(num)
    # lists = line.strip().split()
    # print(lists[num:-1])
    # print(' '.join(lists[:num]))
    # test = mtr.readNeutronActivity(path)
    # cr = mtr.getCR(path)
    # ny = mtr.getNeutronYield(path)
    # print(ny)
    # for key, value in test.items():
    #     print(key,value)

    # import yt
    # groupname = []
    # mtr = McnpTallyReader()
    # source = 7.58318e18
    # mtr.readMdataIntoHDF5(source, 'kcord.dat', 'kcod.hdf5')
    # source = 7.00279e15
    # mtr.readMdataIntoHDF5(source, 'fixed.dat', 'fixe.hdf5')
#     with h5py.File("kcode.hdf5", "r") as f:
#         for group in f:
#             groupname.append(group)
#         #print(groupname)
#         x = [f[groupname[0]]['XCoordinate'][0], f[groupname[0]]['XCoordinate'][-1]]
#         y = [f[groupname[0]]['YCoordinate'][0], f[groupname[0]]['YCoordinate'][-1]]
#         z = [f[groupname[0]]['ZCoordinate'][0], f[groupname[0]]['ZCoordinate'][-1]]
#         bbox = np.array([x, y, z])
#         print(bbox)
#         d = dict(deposit=np.transpose(f[groupname[0]]["data"]), err=np.transpose(f[groupname[0]]['error']))
#         ds = yt.load_uniform_grid(d, d["deposit"].shape, length_unit="cm", bbox=bbox, nprocs=9)
#         p = yt.SlicePlot(ds, "x", ["deposit", 'err'], center='c')
#         p.set_cmap(field="deposit", cmap='jet')
#         p.set_xlabel('x (cm)')
#         p.set_ylabel('z (cm)')
#         #p.set_log("deposit", False)
# #         p.set_zlim('err', 0, 1)
# #         # p.set_background_color('err','red')
#         p.save()

    # mtr.readLatticeData2dat('pow.log',fuel=36)
    # tallys = {'fuel in active region':6, "grapht in active region":16, \
    # 'bypass':26, "primary container":36, "top plenum":46, "top support plate":56,\
    # 'top cap':66, 'bottom plenum':76, 'top support plate':86, 'bottom cap':96, \
    # 'top reflector':116, 'bottom reflector':126, 'pump sump':136, 'rod':146,\
    # 'tube':156, 'heat exchanger':166}
    ###
    # print mtr.readSingleTally('dept.log', **tallys)
    ##
    ##
    # data = mtr.readFmeshDataIntoDic("meshtal", '4', 2, True, "Rel Error", "Result")
#     import h5py
#     import yt
# #    with h5py.File("mytestfile.hdf5", "w") as f:
# #        f["Volume"] = data["Volume"].reshape(74,74,90)
# #        f["Result"] = data["Result"].reshape(74,74,90)
# #        for key in f.keys():
# #            print(f[key].name)
# #            print(f[key].value)
# #        bbox = np.array([[-94.35, 94.35], [-94.35, 94.35], [-90, 90]])
# #    d = dict(Result=data["Result"].reshape(74,74,90))
# #    ds = yt.load_uniform_grid(d, d["Result"].shape, length_unit="cm", bbox=bbox, nprocs=9)
# #    p = yt.SlicePlot(ds, "z", ["Result"],center='c')
# #    p.set_cmap(field="Result", cmap='jet')
# #    #ax = p.plots['Result'].axes
# #    #ax.set_yticks([0,180])
# #    p.set_log("Result", False)
# #    p.annotate_sphere([0, 0, 0], radius=(20, 'cm'),
# #                  circle_args={'color':'black'})
# #    with h5py.File('F:\pythonwork\mcnp_n_impr_fluka.h5m', "r") as f:
# #        coords = f["/tstt/nodes/coordinates"][:]
# #        conn = f["/tstt/elements/Tri3/connectivity"][:]
# #    points = coords[conn-1]
# #    p.annotate_triangle_facets(points, plot_args={"colors": 'black'})
# #    p.save('hot_cmap1.png')

#     with h5py.File("biasedtaly.hdf5", "r") as f:

#         bbox = np.array([[-94.35, 94.35], [-94.35, 94.35], [-90, 90]])
#         d = dict(Flux=f["Result"], err=f['Rel Error'])
#         ds = yt.load_uniform_grid(
#             d, d["Flux"].shape, length_unit="cm", bbox=bbox, nprocs=9)
#         p = yt.SlicePlot(ds, "x", ["Flux", 'err'], center='c')
#         p.set_cmap(field="Flux", cmap='jet')
#         p.set_xlabel('x (cm)')
#         p.set_ylabel('z (cm)')
#         p.set_log("err", False)
#         p.set_zlim('err', 0, 1)
#         # p.set_background_color('err','red')
#         p.save()
   # d = np.array(data[1])
    # print data[0]

#    data = mtr.readKeff("fast.log")
