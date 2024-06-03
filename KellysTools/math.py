# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:08:31 2023

@author: TSM
"""
import numpy as np
import warnings


def eV2nm(energy):
    h=4.1357e-15 #eV s
    c=2.998e17 #nm/s
    return h*c/energy

def g(x,mu,sigma):
    return np.exp(-(x-mu)**2/(2*sigma**2))

def stepper(x,k):
    """Step function
    input:
        x: arr, input x-coordinates
        k: float, variable determining steepness of slope, if desiring a certain rise time, use k=1/t
    return:
        arr, step function array"""
    return .5+.5*np.tanh(np.pi*k*x)

def log_floor(x):
    """Truncate to nearest 10^n
    input:
        x: val,arr, input value
    return:
        val,arr, nearest log"""
    val=np.log10(x)//1
    return 10**val

def log_round(x):
    """Round to nearest 10^n
    input:
        x: val,arr, input value
    return:
        val,arr, nearest log"""
    val=np.round(np.log10(x))
    return 10**val

def log_nearest_factor(x,k,decimal=0):
    """Round to nearest factor of k at the level of the nearest 10^n"""
    level=log_floor(x)/10**(decimal)
    factor=k*level
    return np.round(x/factor)*factor
    

def square(x,dt,delta_t,shift=0,inverted=False):
    xnew=(x-shift)%dt
    y=(xnew<delta_t)^inverted
    return y.astype(int)

def freq_square(x,freq,duty_cycle=.5,cycle_shift=0,inverted=False):
    dt=1/freq
    delta_t=dt*duty_cycle
    shift=dt*cycle_shift
    y=square(x,dt,delta_t,shift,inverted)
    return y

def argmin2d(pos,x2d=None,y2d=None,z2d=None,axis=0,returnalt=False):
    """Returns the indices in a 2d array that most closely match the input position, even when the data sets are non-linear
    
        pos: int or float, value that function looks for minimum position in either x2d or y2d
        x2d: 2d numpy.array, 2d array of x values (mxn)
        y2d: 2d numpy.array, 2d array of y values (mxn)
        z2d: 2d numpy.array, 2d array of z values (mxn)
        axis: int, axis to slice from
        returnalt: bool, return the values for the axis you are slicing"""
    for i in [x2d,y2d,z2d]:
        if i is not None:
            yshape,xshape=i.shape
    if z2d is None:
        if axis==0:
            warnings.warn("z2d defaulting to 2d arange array along the y axis",Warning)
            z2d=np.repeat(np.arange(yshape)[:,np.newaxis],xshape,1)
        elif axis==1:
            warnings.warn("z2d defaulting to 2d arange array along the y axis",Warning)
            z2d=np.repeat(np.arange(xshape)[np.newaxis],yshape,0)
    if x2d is None:
        if axis==0:
            warnings.warn("x2d defaulting to 2d arange array",Warning)
        x2d=np.repeat(np.arange(xshape)[np.newaxis],yshape,0)
    if y2d is None:
        if axis==1:
            warnings.warn("y2d defaulting to 2d arange array",Warning)
        y2d=np.repeat(np.arange(yshape)[:,np.newaxis],xshape,1)
    
    if axis==0:
        temp=np.argmin(abs(y2d-pos),0)
        x=x2d[temp,np.arange(temp.shape[0])]
        y=y2d[temp,np.arange(temp.shape[0])]
        z=z2d[temp,np.arange(temp.shape[0])]
        if returnalt:
            return x,y,z
        else:
            return x,z
    elif axis==1:
        temp=np.argmin(abs(x2d-pos),1)
        x=x2d[np.arange(temp.shape[0]),temp]
        y=y2d[np.arange(temp.shape[0]),temp]
        z=z2d[np.arange(temp.shape[0]),temp]
        if returnalt:
            return x,y,z
        else:
            return y,z  