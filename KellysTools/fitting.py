# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 11:48:36 2023

@author: TSM
"""

import lmfit

def gaussianNModel(n):
    """Built an lmfit model of Gaussians
    input:
        n: int, number of gaussians to include
    return:
        obj, instance of lmfit.models.GaussianModel with n Gaussians.
    """
    temp=sum([lmfit.models.GaussianModel(prefix='g{}'.format(i)) for i in range(n)])+lmfit.models.ConstantModel()
    for i in range(n):
        temp.set_param_hint('g{}amplitude'.format(i),min=0)
    return temp

class ExpFit:
    def __init__(self,n=1):
        """n is number of exponentials to fit"""
        self.mod=lmfit.models.ExpressionModel("+".join(["a{}*exp(-(x-x0)/t{})".format(i,i) for i in range(n)])+"+c")
        self.pars=self.mod.make_params()
        for i in range(n):
            self.pars['a{}'.format(i)].set(.003)
            self.pars['t{}'.format(i)].set(25)
        self.pars['c'].set(.0035)
        self.pars['x0'].set(0,vary=False)
        
    def setXY(self,x,y):
        """input x and y arrays for fitting"""
        self.x=x
        self.y=y
        
    def modelFit(self,t0,t1):
        """Model using n exponentials between x-coordinates t0 and t1"""
        self.fit=self.mod.fit(self.y[(self.x>t0)&(self.x<t1)],self.pars,x=self.x[(self.x>t0)&(self.x<t1)])
        _=self.fit.plot()
        
    def __str__(self):
        """Prints the fit_report when print(obj) is used"""
        return self.fit.fit_report()