#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
import struct
import numpy as np
import h5py

kBytesPerFloat = 4
kBytesPerInt = 4
kBytesPerDouble = 8
kBytesPerChar = 1
BytesPerUnit = {}
BytesPerUnit['f'] = kBytesPerFloat
BytesPerUnit['i'] = kBytesPerInt
BytesPerUnit['c'] = kBytesPerChar
BytesPerUnit['d'] = kBytesPerDouble

def readByteRange(fid):
    string = fid.read(kBytesPerInt)
    (num,) = struct.unpack('i', string)
    return num

def skipDataBlock(fid):
    struct.unpack('i', fid.read(kBytesPerInt))

def readString(fid, byte_range):
    char_list = []
    for ii in range(0, byte_range):
        (ch, ) = struct.unpack('c', fid.read(kBytesPerChar))
        char_list.append(ch.decode('UTF-8', 'strict'))
    string = ''.join(char_list)
    return string

def readData(fid, byte_range, data_type):
    data_list = []

    for ii in range(0, int(byte_range/BytesPerUnit[data_type])):
        (data, ) = struct.unpack(data_type, 
                fid.read(BytesPerUnit[data_type]))
        data_list.append(data)

    return data_list

def readMeshInfo(fid):
    mesh_info = []
    num_bytes = readByteRange(fid)
    print('1', num_bytes)
    data_list = readData(fid, num_bytes, 'i')
    mesh_info.append(data_list)
    skipDataBlock(fid)
    num_bytes = readByteRange(fid)
    print('2', num_bytes)
    energy_bin = readData(fid, num_bytes-4, 'd')
    mesh_info.append(energy_bin)
    extr_data = readData(fid, 4, 'i')
    mesh_info.append(extr_data)
    skipDataBlock(fid)
    num_bytes = readByteRange(fid)
    print('3', num_bytes)
    zeros = readData(fid, num_bytes, 'i') 
    skipDataBlock(fid)
    num_bytes = readByteRange(fid)
    print('4', num_bytes)
    zeros = readData(fid, num_bytes, 'i') 
    return mesh_info

def readRealData(fid, totmesh_num):
    data = {}
    num_bytes = readByteRange(fid)
    mesh_x = readData(fid, num_bytes, 'd')
    data['mesh_x'] = mesh_x
    skipDataBlock(fid) 
    num_bytes = readByteRange(fid)
    mesh_y = readData(fid, num_bytes, 'd')
    data['mesh_y'] = mesh_y
    skipDataBlock(fid) 
    num_bytes = readByteRange(fid)
    mesh_z = readData(fid, num_bytes, 'd')
    data['mesh_z'] = mesh_z
    data['data'] = []
    while len(data['data']) < totmesh_num:
        skipDataBlock(fid) 
        num_bytes = readByteRange(fid)
        data['data'].extend(readData(fid, num_bytes, 'd'))
    data['error'] = []
    while len(data['error']) < totmesh_num:
        skipDataBlock(fid) 
        num_bytes = readByteRange(fid)
        data['error'].extend(readData(fid, num_bytes, 'd'))

    return data

def readMdataFile(mdata_file):
    mdata = {}
    with open(mdata_file, 'rb') as fid:
        fid.seek(0, 0)
        num_bytes = readByteRange(fid)
        mdata['title'] = readString(fid, int(num_bytes/kBytesPerChar))
        skipDataBlock(fid)
        num_bytes = readByteRange(fid)
        data_list = []
        (meshtally_num, ) = struct.unpack('i', fid.read(kBytesPerInt))
        mdata['meshtally_num'] = meshtally_num
        string = readString(fid, num_bytes-8)
        mdata['mcnp_version_time'] = string
        (num, ) = struct.unpack('i', fid.read(kBytesPerInt))
        print(mdata['mcnp_version_time'])
        skipDataBlock(fid)
        num_bytes = readByteRange(fid)
        twenty_zeros = readData(fid, num_bytes, 'i')
        for ii in range(meshtally_num):
            skipDataBlock(fid)
            meshtally = 'mesh_{:}_info'.format(ii+1)
            mdata[meshtally] = readMeshInfo(fid)
            totnum_mesh = 'totnum_mesh_{:}'.format(ii+1)
            mdata[totnum_mesh] = mdata[meshtally][0][6]
            mdata['mesh_{:}_type'.format(ii+1)] = str(mdata[meshtally][0][0])[0] 

        for ii in range(meshtally_num):
            skipDataBlock(fid)
            meshtally_info = 'mesh_{:}_info'.format(ii+1)
            meshtally = 'meshtally_{:}'.format(ii+1)
            totnum_mesh = mdata[meshtally_info][0][6] 
            data = readRealData(fid, totnum_mesh)
            mdata[meshtally] = data
        
    
    return mdata

def readMdataIntoHDF5(source, nps, mdataFileName, hdfFileName):
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
    dimension = []
    nx = 0
    ny = 0
    nz = 0
    xcord = []
    ycord = []
    zcord = []
    grouplists = [] # group name in hdf5 file

    mdata = readMdataFile(mdataFileName)
    numtallys = mdata['meshtally_num']
    with  h5py.File(hdfFileName, "w") as hdfid:
        for ii in range(numtallys):
            groupname = 'mesh_{:}'.format(ii + 1)
            hdfid.create_group(groupname)
        grouplists = [x for x in hdfid]
        for ii in range(numtallys):
            meshinfo = 'mesh_{:}_info'.format(ii+1)
            meshtally = 'meshtally_{:}'.format(ii+1)
            mesh_type = mdata['mesh_{:}_type'.format(ii+1)]
            nx = mdata[meshinfo][0][2]
            ny = mdata[meshinfo][0][3]
            nz = mdata[meshinfo][0][4]
            # rectangular mesh : 网格数据个数为(nx - 1) * (ny - 1) * (nz - 1)
            if mesh_type == '1':
                nmeshs = (nx - 1) * (ny - 1) * (nz - 1)
                dimension = [int(nx - 1), int(ny - 1), int(nz - 1)]
                hdfid[grouplists[ii]].create_dataset(
                    'dimension', data=dimension)
            # cylindrical mesh: nz 为角向，0到360
            elif mesh_type == '2':
                nmeshs = (nx - 1) * (ny - 1) * nz
                dimension = [int(nx - 1), int(ny - 1), int(nz)]
                hdfid[grouplists[ii]].create_dataset(
                    'dimension', data=dimension)
            # spherical mesh: ny 为角向，0到180; nz 为角向，0到360
            elif mesh_type == '3':
                nmeshs = (nx - 1) * ny * nz
                dimension = [int(nx - 1), int(ny), int(nz)]
                hdfid[grouplists[ii]].create_dataset(
                    'dimension', data=dimension)
            else:
                raise Exception(
                    'Error: The mesh type is {}, not supported!'.format(
                        mesh_type))
            # 写入coordinates
            xcord = mdata[meshtally]['mesh_x']
            ycord = mdata[meshtally]['mesh_y']
            zcord = mdata[meshtally]['mesh_z']
            dd = [x for x in xcord]
            hdfid[grouplists[ii]].create_dataset('XCoordinate', data=dd)
            dd = [x for x in ycord]
            hdfid[grouplists[ii]].create_dataset('YCoordinate', data=dd)
            dd = [x for x in zcord]
            hdfid[grouplists[ii]].create_dataset('ZCoordinate', data=dd)
            # 写入统计结果和误差
            arrd = [dd*source/nps for dd in mdata[meshtally]['data']] 
            dd = np.array(arrd).reshape(dimension[0], dimension[1], dimension[2])
            hdfid[grouplists[ii]].create_dataset('data', data=dd)
            arrd = mdata[meshtally]['error']
            dd = np.array(arrd).reshape(dimension[0], dimension[1], dimension[2])
            hdfid[grouplists[ii]].create_dataset('error', data=dd)


if __name__ == '__main__':
    proton_intensity = 4e-3 #mA
    MeV2J = 1.6022e-13
    proton_num_per_A = 6.24e18
    source = proton_intensity*proton_num_per_A*MeV2J
    print(source)
    readMdataIntoHDF5(source, 50000, 'mdatb', 'power.hdf5')
    # print(mdata['mesh_z'])
