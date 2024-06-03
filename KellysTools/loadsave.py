# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:02:27 2023

@author: TSM
"""
import numpy as np
import os

def loadLV(fpath,ndim):
    from ._LVBF import LV_fd
    reader=LV_fd()
    with open(fpath,mode='rb') as reader.fobj:
        array0=reader.read_array(reader.read_numeric,reader.LVfloat64,ndim)
    return array0

def fileStack(directory,filerange,fmt="{}.npy"):
    """Stack .npy of shape (a1,...,an) files to build a m-dim array of shape (m,a1,...,an) where m is the number of files
    directory: str, filepath to iterable file name
    filerange: iter, list range that specifies name of file
    fmt: str, format of file name e.g. {}.npy, {:.3f}.npy
    """
    temp=[]
    for i in filerange:
        temp2=np.load(directory+os.sep+fmt.format(i))
        if temp2.ndim>1:
            temp.append(temp2)
        else:
            print("{} is empty".format(i))
    return np.stack(temp)

def fileStackLV(directory,filerange,ndim,fmt="{}.npy"):
    """Stack 1dLV files to build a 2d array
    directory: str, filepath to iterable file name
    filerange: iter, list range that specifies name of file
    fmt: str, format of file name e.g. {}.npy, {:.3f}.npy
    """
    temp=[]
    for i in filerange:
        temp2=loadLV(directory+os.sep+fmt.format(i),ndim)
        if temp2.ndim>1:
            temp.append(temp2)
        else:
            print("{} is empty".format(i))
    return np.stack(temp)

def fileStack2d(directory,filerange,fmt="{}.npy",axis=0,avg=False):
    """Stack 2d array files on top of each other to build a large 2d array
    
    directory: str, filepath to iterable file name
    filerange: iter, list range that specifies name of file
    fmt: str, format of file name e.g. {}.npy, {:.3f}.npy
    axis: int, axis number to concatenate and, if avg==True, average
    avg: bool, average each file individually before adding to array"""
    temp=[]
    for i in filerange:
        temp2=np.load(directory+os.sep+fmt.format(i))
        if temp2.ndim>0:
            if avg:
                temp2=expand_dims(average(temp2,axis),axis)
            temp.append(temp2)
        else:
            print("{} is empty".format(i))
    return np.concatenate(temp,axis)

class Dict2Obj:
    def __init__(self,tempdict):
        self.__dict__.update(tempdict)
        
def loadz(fpath):
    return Dict2Obj(np.load(fpath,allow_pickle=True))
        
def npz2mat(fpath):
    from scipy.io import savemat
    base=os.path.splitext(fpath)[0]
    temp=np.load(fpath)
    savemat(base+'.mat',temp)
    
def npy2mat(fpath):
    from scipy.io import savemat
    base=os.path.splitext(fpath)[0]
    temp=np.load(fpath)
    savemat(base+'.mat',dict(arr=temp))