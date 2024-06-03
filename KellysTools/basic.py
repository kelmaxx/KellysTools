# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 11:45:15 2023

@author: TSM
"""
import numpy as np
import threading
import os

def smooth(y, box_pts):
    """Smoothing method for a dataset
    input:
        y: arr, 1d array to smooth
        box_pts: int, width of smoothing box
    return: arr, smoothed 1d array"""
    box=ones(box_pts)/box_pts
    y_smooth=np.convolve(y,box,mode='same')
    return y_smooth

def FWHM(arr,x=None):
    """This determines the full width at half max of an array, ideally this has a uniform baseline for determining relative FWHM.
    If x=None, then this returns FWHM in array coordinates, otherwise it returns values from x.
    
    Parameters
    ----------
    arr:  ndarray
        An array with some central peak
    x:    ndarray
        X values corresponding to values in arr
        
    Returns
    -------
    out: float
        FWHM of an array
    """
    posmax=np.argmax(arr)
    arrmax,arrmin=arr.max(),arr.min()
    HM=(arrmax-arrmin)/2+arrmin
    p1=np.argmin(np.abs(HM-arr[:posmax]))
    p2=np.argmin(np.abs(HM-arr[posmax:]))+posmax
    if x is None:
        return p2-p1
    return x[p2]-x[p1]

def unravel(x2d,y2d):
    """Returns the values from the outer edge of the 2 input arrays. Useful for plotting a box around 2d array of coordinates
    input:
        x2d: arr, 2d array of x coordinates
        y2d: arr, 2d array of y coordinates
    return:
        (arr,arr), 1d arrays from the outer perimeter of x2d, y2d
    """
    x=np.concatenate([x2d[0],x2d[:,-1],x2d[-1,::-1],x2d[::-1,0]])
    y=np.concatenate([y2d[0],y2d[:,-1],y2d[-1,::-1],y2d[::-1,0]])
    return x,y

def getIndex(val,arr,axis=None):
    """Find the index in an array that is closest to the input value, built off of np.argmin
    input:
        val: float, target value to find in arr
        arr: arr, array where you are trying to find closest point to val
        axis: int, array axis to find the closest value along
    return:
        int or arr, closest index in array based on axis.
    """
    return np.argmin(np.abs(val-arr),axis)

def chunkAvg(arr,binsize,axis=0,rolling_step=None):
    """This takes an array and averages along one axis according to the bin size in small chunks"""
    n=arr.shape[axis]
    if rolling_step==None: j=binsize
    else: j=rolling_step
    return np.concatenate([np.expand_dims(np.average(arr.take(indices=range(i,min(i+binsize,n)),axis=axis),axis),axis) for i in range(0,n,j)],axis)

def sound(pause=False):
    """Play a sound, maybe to alert when a calculation finishes or something."""
    import winsound
    spath=os.path.dirname(__file__)+os.sep+"DING.wav"
    if pause:
        winsound.PlaySound(spath,winsound.SND_FILENAME)
    else:
        th=threading.Thread(target=winsound.PlaySound,args=(spath,winsound.SND_FILENAME))
        th.start()

def getHex(r,g,b):
    s="#{:02x}{:02x}{:02x}".format(r,g,b)
    return s
        
def rgb_tint(rgb,factor=2):
    """darkens an input hex color string, used for contrasting two lines"""
    h=rgb.lstrip('#')
    vals=tuple(int(int(h[i:i+2], 16)/factor) for i in (0, 2, 4))
    s="#{:02x}{:02x}{:02x}".format(*vals)
    return s 

def capture_qt_object(obj):
    from PyQt5.QtWidgets import QApplication
    cboard=QApplication.clipboard()
    cboard.setPixmap(obj.grab())

dtt_='ΔT/T'
mdtt_='m'+dtt_