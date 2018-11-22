#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 09 14:56:21 2018

@author: yang
"""
import re
import numpy as np
import h5py


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
            results['keff'] = data[0]
            results['error'] = data[1]
        else:
            return None
        return results

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


if __name__ == '__main__':
    import yt
    groupname = []
    mtr = McnpTallyReader()
    source = 7.58318e18
    mtr.readMdataIntoHDF5(source, 'kcord.dat', 'kcod.hdf5')
    source = 7.00279e15
    mtr.readMdataIntoHDF5(source, 'fixed.dat', 'fixe.hdf5')
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
