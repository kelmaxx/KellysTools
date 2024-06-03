# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:30:20 2023

@author: TSM
"""
import matplotlib as mpl
import numpy as np
from kimpl.Tools.DraggableSlicer import DraggableLine as _DraggableLine
import kimpl as kmpl
from PyQt5 import QtWidgets,QtCore
from time import sleep
from matplotlib import ticker as _ticker

from KellysTools.basic import rgb_tint

class Cmapper(mpl.colors.Normalize):
    def __init__(self,setpoints=None,clip=False):
        """Color scale normalizer, input a range of set points and it will distribute the color density accordingly
        e.g.
        [0,1,5,10] will map to default colormap of [0,.33,.66,1]"""
        self.setpoints=setpoints
        self._y=np.linspace(0,1,len(self.setpoints))
        super().__init__(self.setpoints[0],self.setpoints[-1],clip)
        
        
    def __call__(self,value,clip=None):
        return np.ma.masked_array(np.interp(value,self.setpoints,self._y))
    
def sqax(ax):
    """Force bbox to be square"""
    tempbbox=ax.get_position()
    w,h=ax.figure.get_size_inches()
    width=(tempbbox.x1-tempbbox.x0)/h*w
    tempbbox.y1=tempbbox.y0+width
    ax.set_position(tempbbox)

def vshift(listax,amount):
    """Shift axes an amount vertically, ammount is between 0 and 1"""
    for i in listax.flatten():
        tempbbox=i.get_position()
        tempbbox.y0,tempbbox.y1=tempbbox.y0+amount,tempbbox.y1+amount
        i.set_position(tempbbox)

def hshift(listax,amount):
    """Shift axes an amount horizontally, ammount is between 0 and 1"""
    for i in listax.flatten():
        tempbbox=i.get_position()
        tempbbox.x0,tempbbox.x1=tempbbox.x0+amount,tempbbox.x1+amount
        i.set_position(tempbbox)

def matchHeight(ax0,ax1):
    """Set ax0 height position to match ax1"""
    tempbbox=ax1.get_position()
    tempbbox1=ax0.get_position()
    diff=tempbbox.y1-tempbbox.y0
    tempbbox1.y1=tempbbox1.y1+diff
    ax0.set_position(tempbbox1)
    
def matchDirection(ax0,ax1,direction='top'):
    """Set ax0 side position to match ax1"""
    tempbbox=ax0.get_position()
    tempbbox1=ax1.get_position()
    if direction=='top':
        tempbbox.y1=tempbbox1.y1
    elif direction=='bottom':
        tempbbox.y0=tempbbox1.y0
    elif direction=='left':
        tempbbox.x0=tempbbox1.x0
    elif direction=='right':
        tempbbox.x1=tempbbox1.x1
    ax0.set_position(tempbbox)
    
def setHeight(ax0,val):
    tempbbox=ax0.get_position()
    tempbbox.y1=tempbbox.y0+val
    ax0.set_position(tempbbox)

def setWidth(ax0,val):
    tempbbox=ax0.get_position()
    tempbbox.x1=tempbbox.x0+val
    ax0.set_position(tempbbox)
    
class TextMover:
    """Move text using the arrows in a matplotlib plot"""
    def __init__(self,text,step=.005):
        self.text=text
        self.figure=text.figure
        self.step=step
        self.sid=self.figure.canvas.mpl_connect('key_press_event',self.move)
        self.animation=animation.ArtistAnimation(self.text.figure,[(self.text,)])
    def move(self,event):
        if event.key not in {'left','right','up','down','enter'}:
            return
        cx,cy=self.text.get_position()
        if event.key=='left':
            self.text.set_x(cx-self.step)
        elif event.key=='right':
            self.text.set_x(cx+self.step)
        elif event.key=='up':
            self.text.set_y(cy+self.step)
        elif event.key=='down':
            self.text.set_y(cy-self.step)
        elif event.key=='enter':
            self.figure.canvas.mpl_disconnect(self.sid)
            self.text.set_animated(0)
            self.figure.canvas.draw()
            

class Slicer:
    
    def __init__(self,data,cmap=None,vmin=None,vmax=None,x=None,y=None,num=None,view_axes=(-2,-1),grid_spec_kw=None,image_kwargs=None):
        """
        2D image viewer with nD data input

        Parameters
        ----------
        data : np.ndarray
            Multidimensional array. The displayed axes are determined by 'view_axes'. The other axes can be controlled by spinboxes.
        cmap : str or `~matplotlib.colors.Colormap`, default: :rc:`image.cmap`
            The Colormap instance or registered colormap name used to map scalar data
            to colors.
        
            This parameter is ignored if *X* is RGB(A).
        vmin, vmax : float, optional
            When using scalar data and no explicit *norm*, *vmin* and *vmax* define
            the data range that the colormap covers. By default, the colormap covers
            the complete value range of the supplied data. It is an error to use
            *vmin*/*vmax* when a *norm* instance is given (but using a `str` *norm*
            name together with *vmin*/*vmax* is acceptable).
        
            This parameter is ignored if *X* is RGB(A).
        x : np.ndarray, optional
            1d or 2d array of coordinates for x-axis of the viewing axes
        x : np.ndarray, optional
            1d or 2d array of coordinates for y-axis of the viewing axes
        num : int or str or `.Figure` or `.SubFigure`, optional
            A unique identifier for the figure.
        
            If a figure with that identifier already exists, this figure is made
            active and returned. An integer refers to the ``Figure.number``
            attribute, a string refers to the figure label.
        
            If there is no figure with the identifier or *num* is not given, a new
            figure is created, made active and returned.  If *num* is an int, it
            will be used for the ``Figure.number`` attribute, otherwise, an
            auto-generated integer value is used (starting at 1 and incremented
            for each new figure). If *num* is a string, the figure label and the
            window title is set to this value.  If num is a ``SubFigure``, its
            parent ``Figure`` is activated.
        view_axes : tuple, optional
            Axes used for x,y coordinates on the displayed image. The default is (-2,-1).
        gridspec_kw : dict, optional
            Dict with keywords passed to the `~matplotlib.gridspec.GridSpec`
            constructor used to create the grid the subplots are placed on.
        """
        default_gridspec=dict(width_ratios=(1,.25),height_ratios=(1,.25))
        if grid_spec_kw is not None:
            default_gridspec.update(grid_spec_kw)
        if image_kwargs is None:
            image_kwargs=dict()
        self.fig,self.ax=kmpl.subplots(2,2,num=num,figsize=(5.6,5.6),gridspec_kw=default_gridspec)
        self.fig.subplots_adjust(top=0.975,
                                    bottom=0.1,
                                    left=0.145,
                                    right=0.98,
                                    hspace=0.11,
                                    wspace=0.115)
        
        if vmin is None:
            vmin=data.min()
        if vmax is None:
            vmax=data.max()
        
        self.data=data
        self.view_axes=tuple(i%data.ndim for i in view_axes) #force to range from 0 to ndim
        self.current=[0 for i in range(data.ndim)] #index of dataset, default is to use index 0 for all axes
        for i in self.view_axes:
            self.current[i]=slice(None,None) #update the viewing axes to be a slice
        self.comparison=None #other instance of this class
        
        self.x=x
        self.y=y
        self.dlh=[] #list holding horizontal lines
        self.dlv=[] #list holding vertical lines
        dl1=self.addHorizontal()
        dl2=self.addVertical()
        
        self.colormesh=dl1.colormesh #draggable lines determine whether the displayed image should be colormesh, they also create the 2d x and y coordinates based on the input x and y arrays
        tempdata=self.data[tuple(self.current)]
        if self.view_axes[1]<self.view_axes[0]:
            tempdata=tempdata.T
        if self.colormesh:
            self.img=self.ax[0,0].pcolormesh(dl1.x,dl1.y,tempdata,cmap=cmap,vmin=vmin,vmax=vmax,**image_kwargs)
        else:
            self.img=self.ax[0,0].imshow(tempdata,cmap,vmin=vmin,vmax=vmax,**image_kwargs) 
            
        xmin,xmax=dl1.x.min(),dl1.x.max()
        ymin,ymax=dl1.y.min(),dl1.y.max()
        vmin,vmax=self.img.get_clim()
        shift=(vmax-vmin)*.05 #5% margin
        self.ax[0,0].sharex(self.ax[1,0])
        self.ax[0,0].sharey(self.ax[0,1])
        self.ax[0,0].set_xlim(xmin,xmax)
        self.ax[0,0].set_ylim(ymin,ymax)
        # self.ax[1,0].set_xlim(xmin,xmax)
        self.ax[1,0].set_ylim(vmin-shift,vmax+shift)
        # self.ax[0,1].set_ylim(ymin,ymax)
        self.ax[0,1].set_xlim(vmin-shift,vmax+shift)
        
        self.ax[1,1].axis('off')
        self.ax[0,0].xaxis.set_tick_params(bottom=False,labelbottom=False)
        self.ax[0,1].yaxis.set_tick_params(left=False,labelleft=False)
        
        self._connect()
        
    def _connect(self):
        """Create and add appropriate actions and controls to the toolbar"""
        for a_label in ['home','back','forward']: #remove these actions. They crowd out the important ones.
            a=self.fig.canvas.toolbar._actions[a_label]
            self.fig.canvas.toolbar.removeAction(a) 
        a1=QtWidgets.QAction("+V",self.fig.canvas.toolbar)
        a2=QtWidgets.QAction("+H",self.fig.canvas.toolbar)
        self.widgets={}
        for i,j in enumerate(self.current): #iterate through axes
            if j==0: #default was to set the values to 0, this only creates a widget for the axes that are not the view axes
                b=QtWidgets.QSpinBox()
                b.setMinimum(0)
                b.setMaximum(self.data.shape[i]-1)
                self.widgets[i]=b
        self.fig.canvas.toolbar.addAction(a1)
        self.fig.canvas.toolbar.addAction(a2)
        a1.triggered.connect(self.addVertical)
        a2.triggered.connect(self.addHorizontal)
        self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel("["))
        for i in range(self.data.ndim):
            if i in self.widgets:
                self.fig.canvas.toolbar.addWidget(self.widgets[i])
                self.widgets[i].valueChanged.connect(self._setIndex)
            else:
                self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel(":"))
            if i!=self.data.ndim-1:
                self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel(","))
        self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel("]"))
        self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel("scale:"))
        vmin=QtWidgets.QDoubleSpinBox()
        vmax=QtWidgets.QDoubleSpinBox()
        for i,j in zip([vmin,vmax],self.img.get_clim()):
            i.setMinimum(-9999.99)
            i.setMaximum(9999.99)
            i.setValue(j)
            i.setMaximumWidth(40)
            i.setButtonSymbols(2)
            self.fig.canvas.toolbar.addWidget(i)
        vmin.valueChanged.connect(lambda x: self.set_clim(vmin=x))
        self.fig.canvas.toolbar._actions['vmin']=vmin
        self.fig.canvas.toolbar._actions['vmax']=vmax
        vmax.valueChanged.connect(lambda x: self.set_clim(vmax=x))
            
        
    def addVertical(self):
        """Add vertical draggable line"""
        data=self.data[tuple(self.current)]
        if self.view_axes[1]<self.view_axes[0]:
            data=data.T
        dl=_DraggableLine(data,self.ax[0,0],self.ax[0,1],self.x,self.y,orientation='vertical',data_orientation='vertical')
        if self.comparison is not None:
            dl.addDataAxis(self.comparison.ax[0,1],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        self.dlv.append(dl)
        self._drawcanvas()
        return dl
        
    def addHorizontal(self):
        """Add horizontal draggable line"""
        data=self.data[tuple(self.current)]
        if self.view_axes[1]<self.view_axes[0]:
            data=data.T
        dl=_DraggableLine(data,self.ax[0,0],self.ax[1,0],self.x,self.y)
        if self.comparison is not None:
            dl.addDataAxis(self.comparison.ax[1,0],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        self.dlh.append(dl)
        self._drawcanvas()
        return dl
    
    def _setIndex(self):
        """Set the displayed image and data"""
        current=[0 for i in self.current]
        for i in self.widgets:
            current[i]=self.widgets[i].value()
        for i in self.view_axes:
            current[i]=slice(None,None)
        self.current=current
        QtCore.QTimer.singleShot(200,self._updateData)
        
    def _updateData(self):
        data=self.data[tuple(self.current)]
        if self.view_axes[1]<self.view_axes[0]:
            data=data.T
        if not self.colormesh:
            self.img.set_data(data)
        else:
            self.img.set_array(data.ravel()) #for pcolormesh, to update the data, you exclude the last row and column, then unravel to be a 1d array
        for dl in self.dlh+self.dlv:
            dl.updateData(data)
        self._drawcanvas()
        
    def setData(self,data):
        if data.shape!=self.data.shape:
            raise ValueError("New data must shape of stored data {}.".format(self.data.shape))
        self.data=data
        self._updateData()
        
    def setIndex(self,indices):
        """Set the indices of the displayed image. For the axes you don't want to change (or the viewing axes), just use None."""
        if len(indices)!=self.data.ndim:
            raise ValueError("Indices length does not match data dimensions.")
        for i in range(self.data.ndim):
            if i in self.widgets:
                if indices[i] is not None:
                    self.widgets[i].setValue(indices[i])
        self._setIndex()
        
    def getIndex(self):
        indices=[]
        for i in range(self.data.ndim):
            if i in self.widgets:
                indices.append(self.widgets[i].value())
            else:
                indices.append(None)
        return indices
    
    def _drawcanvas(self):
        """Redraws all associated figures, but ensures they are all only redrawn once"""
        redrawn_figs=[]
        for dl in self.dlv+self.dlh:
            for fig in dl.figs:
                if fig not in redrawn_figs:
                    fig.canvas.draw()
                    redrawn_figs.append(fig)
                    
    def set_clim(self,vmin=None,vmax=None):
        """Set the limits of the imags"""
        self.img.set_clim(vmin,vmax)
        self._drawcanvas()
        
    
    def compare(self,other,join=True,direction='both'):
        f"""
        Compare Slicer plots. This connects two slicer plots together and overlays the slice data on each others' slice axes.
        If join is True, then the existing draggable lines will connect and move together.

        Parameters
        ----------
        other : {self.__class__}
            Another instance of this class.
        join : bool, optional
            Connect draggable lines between plots to respond together. The default is True.

        """
        self.comparison=other
        for dl in self.dlh:
            dl.addDataAxis(other.ax[1,0],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        for dl in self.dlv:
            dl.addDataAxis(other.ax[0,1],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        if other.comparison!=self:
            other.compare(self)
        if join:
            if direction in ['both','horizontal']:
                for i,j in zip(self.dlh,other.dlh):
                    i.join(j)
            if direction in ['both','vertical']:
                for i,j in zip(self.dlv,other.dlv):
                    i.join(j)

class SlicerLog:
    
    def __init__(self,data,cmap=None,vmin=None,vmax=None,x=None,y=None,num=None,view_axes=(-2,-1),grid_spec_kw=None):
        """
        2D image viewer with nD data input

        Parameters
        ----------
        data : np.ndarray
            Multidimensional array. The displayed axes are determined by 'view_axes'. The other axes can be controlled by spinboxes.
        cmap : str or `~matplotlib.colors.Colormap`, default: :rc:`image.cmap`
            The Colormap instance or registered colormap name used to map scalar data
            to colors.
        
            This parameter is ignored if *X* is RGB(A).
        vmin, vmax : float, optional
            When using scalar data and no explicit *norm*, *vmin* and *vmax* define
            the data range that the colormap covers. By default, the colormap covers
            the complete value range of the supplied data. It is an error to use
            *vmin*/*vmax* when a *norm* instance is given (but using a `str` *norm*
            name together with *vmin*/*vmax* is acceptable).
        
            This parameter is ignored if *X* is RGB(A).
        x : np.ndarray, optional
            1d or 2d array of coordinates for x-axis of the viewing axes
        x : np.ndarray, optional
            1d or 2d array of coordinates for y-axis of the viewing axes
        num : int or str or `.Figure` or `.SubFigure`, optional
            A unique identifier for the figure.
        
            If a figure with that identifier already exists, this figure is made
            active and returned. An integer refers to the ``Figure.number``
            attribute, a string refers to the figure label.
        
            If there is no figure with the identifier or *num* is not given, a new
            figure is created, made active and returned.  If *num* is an int, it
            will be used for the ``Figure.number`` attribute, otherwise, an
            auto-generated integer value is used (starting at 1 and incremented
            for each new figure). If *num* is a string, the figure label and the
            window title is set to this value.  If num is a ``SubFigure``, its
            parent ``Figure`` is activated.
        view_axes : tuple, optional
            Axes used for x,y coordinates on the displayed image. The default is (-2,-1).
        gridspec_kw : dict, optional
            Dict with keywords passed to the `~matplotlib.gridspec.GridSpec`
            constructor used to create the grid the subplots are placed on.
        """
        default_gridspec=dict(width_ratios=(1,.25),height_ratios=(1,.25))
        if grid_spec_kw is not None:
            default_gridspec.update(grid_spec_kw)
        self.fig,self.ax=kmpl.subplots(2,2,num=num,figsize=(5.6,5.6),gridspec_kw=default_gridspec)
        self.fig.subplots_adjust(top=0.975,
                                    bottom=0.1,
                                    left=0.145,
                                    right=0.98,
                                    hspace=0.11,
                                    wspace=0.115)
        self.dax=kmpl.Tools.split_shared_ax(self.ax[0,0],'top')
        self.vax=kmpl.Tools.split_shared_ax(self.ax[0,1],'top')
        
        if vmin is None:
            vmin=data.min()
        if vmax is None:
            vmax=data.max()
        
        self.data=data
        self.view_axes=view_axes
        self.current=[0 for i in range(data.ndim)] #index of dataset, default is to use index 0 for all axes
        for i in self.view_axes:
            self.current[i]=slice(None,None) #update the viewing axes to be a slice
        self.comparison=None #other instance of this class
        
        self.x=x
        self.y=y
        self.dlh=[] #list holding horizontal lines
        self.dlv=[] #list holding vertical lines
        
        dl1=self.addHorizontal()
        dl2=self.addVertical()
        
        self.colormesh=dl1.colormesh #draggable lines determine whether the displayed image should be colormesh, they also create the 2d x and y coordinates based on the input x and y arrays
        tempdata=self.data[tuple(self.current)]
        self.img=[]
        for ax in self.dax:
            if self.colormesh:
                self.img.append(ax.pcolormesh(dl1.x,dl1.y,tempdata,cmap=cmap,vmin=vmin,vmax=vmax))
            else:
                self.img.append(ax.imshow(tempdata,cmap,vmin=vmin,vmax=vmax))
            
        xmin,xmax=dl1.x.min(),dl1.x.max()
        ymin,ymax=dl1.y.min(),dl1.y.max()
        vmin,vmax=self.img[0].get_clim()
        shift=(vmax-vmin)*.05 #5% margin
        self.dax[1].sharex(self.ax[1,0])
        self.dax[0].sharey(self.vax[0])
        self.dax[1].sharey(self.vax[1])
        self.dax[0].set_xlim(xmin,xmax)
        self.dax[0].set_ylim(ymin,(ymax-ymin)/2)
        self.dax[1].set_ylim((ymax-ymin)/2,ymax)
        
        # self.ax[1,0].set_xlim(xmin,xmax)
        self.ax[1,0].set_ylim(vmin-shift,vmax+shift)
        # self.ax[0,1].set_ylim(ymin,ymax)
        self.vax[1].set_xlim(vmin-shift,vmax+shift)
        
        self.ax[1,1].axis('off')
        self.dax[1].xaxis.set_tick_params(bottom=False,labelbottom=False)
        self.dax[0].xaxis.set_tick_params(bottom=False,labelbottom=False)
        self.vax[0].yaxis.set_tick_params(left=False,labelleft=False)
        self.vax[1].yaxis.set_tick_params(left=False,labelleft=False)
        
        self._connect()
        
    def _connect(self):
        """Create and add appropriate actions and controls to the toolbar"""
        for a_label in ['home','back','forward']: #remove these actions. They crowd out the important ones.
            a=self.fig.canvas.toolbar._actions[a_label]
            self.fig.canvas.toolbar.removeAction(a)
        a1=QtWidgets.QAction("+V",self.fig.canvas.toolbar)
        a2=QtWidgets.QAction("+H",self.fig.canvas.toolbar)
        self.widgets={}
        for i,j in enumerate(self.current): #iterate through axes
            if j==0: #default was to set the values to 0, this only creates a widget for the axes that are not the view axes
                b=QtWidgets.QSpinBox()
                b.setMinimum(0)
                b.setMaximum(self.data.shape[i]-1)
                self.widgets[i]=b
        self.fig.canvas.toolbar.addAction(a1)
        self.fig.canvas.toolbar.addAction(a2)
        a1.triggered.connect(self.addVertical)
        a2.triggered.connect(self.addHorizontal)
        self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel("["))
        for i in range(self.data.ndim):
            if i in self.widgets:
                self.fig.canvas.toolbar.addWidget(self.widgets[i])
                self.widgets[i].valueChanged.connect(self._setIndex)
            else:
                self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel(":"))
            if i!=self.data.ndim-1:
                self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel(","))
        self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel("]"))
        self.fig.canvas.toolbar.addWidget(QtWidgets.QLabel("scale:"))
        vmin=QtWidgets.QDoubleSpinBox()
        vmax=QtWidgets.QDoubleSpinBox()
        for i,j in zip([vmin,vmax],self.img[0].get_clim()):
            i.setMinimum(-9999.99)
            i.setMaximum(9999.99)
            i.setValue(j)
            i.setMaximumWidth(40)
            i.setButtonSymbols(2)
            self.fig.canvas.toolbar.addWidget(i)
        vmin.valueChanged.connect(lambda x: self.set_clim(vmin=x))
        self.fig.canvas.toolbar._actions['vmin']=vmin
        self.fig.canvas.toolbar._actions['vmax']=vmax
        vmax.valueChanged.connect(lambda x: self.set_clim(vmax=x))
        
    def addVertical(self):
        """Add vertical draggable line"""
        dl=_DraggableLine(self.data[tuple(self.current)],self.dax,self.vax,self.x,self.y,orientation='vertical',data_orientation='vertical')
        if self.comparison is not None:
            dl.addDataAxis(self.comparison.ax[0,1],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        self.dlv.append(dl)
        self._drawcanvas()
        return dl
        
    def addHorizontal(self):
        """Add horizontal draggable line"""
        dl=_DraggableLine(self.data[tuple(self.current)],self.dax,self.ax[1,0],self.x,self.y)
        if self.comparison is not None:
            dl.addDataAxis(self.comparison.ax[1,0],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        self.dlh.append(dl)
        self._drawcanvas()
        return dl
    
    def _setIndex(self):
        """Set the displayed image and data"""
        current=[0 for i in self.current]
        for i in self.widgets:
            current[i]=self.widgets[i].value()
        for i in self.view_axes:
            current[i]=slice(None,None)
        self.current=current
        QtCore.QTimer.singleShot(200,self._updateData)
        
    def _updateData(self):
        data=self.data[tuple(self.current)]
        for img in self.img:
            if not self.colormesh:
                img.set_data(data)
            else:
                img.set_array(data.ravel()) #for pcolormesh, to update the data, you exclude the last row and column, then unravel to be a 1d array
        for dl in self.dlh+self.dlv:
            dl.updateData(data)
        self._drawcanvas()
        
    def setData(self,data):
        if data.shape!=self.data.shape:
            raise ValueError("New data must shape of stored data {}.".format(self.data.shape))
        self.data=data
        self._updateData()
        
    def setIndex(self,indices):
        """Set the indices of the displayed image. For the axes you don't want to change (or the viewing axes), just use None."""
        if len(indices)!=self.data.ndim:
            raise ValueError("Indices length does not match data dimensions.")
        for i in range(self.data.ndim):
            if i in self.widgets:
                if indices[i] is not None:
                    self.widgets[i].setValue(indices[i])
        self._setIndex()
        
    def getIndex(self):
        indices=[]
        for i in range(self.data.ndim):
            if i in self.widgets:
                indices.append(self.widgets[i].value())
            else:
                indices.append(None)
        return indices
                
    
    def _drawcanvas(self):
        """Redraws all associated figures, but ensures they are all only redrawn once"""
        redrawn_figs=[]
        for dl in self.dlv+self.dlh:
            for fig in dl.figs:
                if fig not in redrawn_figs:
                    fig.canvas.draw()
                    redrawn_figs.append(fig)
    
    def set_clim(self,vmin=None,vmax=None):
        for img in self.img:
            img.set_clim(vmin,vmax)
        self._drawcanvas()
    
    def compare(self,other,join=True,direction='both'):
        f"""
        Compare Slicer plots. This connects two slicer plots together and overlays the slice data on each others' slice axes.
        If join is True, then the existing draggable lines will connect and move together.

        Parameters
        ----------
        other : {self.__class__}
            Another instance of this class.
        join : bool, optional
            Connect draggable lines between plots to respond together. The default is True.

        """
        self.comparison=other
        for dl in self.dlh:
            dl.addDataAxis(other.ax[1,0],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        for dl in self.dlv:
            dl.addDataAxis(other.ax[0,1],linestyle='--',color=rgb_tint(dl.linekwargs['color'],1.2))
        if other.comparison!=self:
            other.compare(self)
        if join:
            if direction in ['both','horizontal']:
                for i,j in zip(self.dlh,other.dlh):
                    i.join(j)
            if direction in ['both','vertical']:
                for i,j in zip(self.dlv,other.dlv):
                    i.join(j)

def scientific(ax):
    ax.ticklabel_format(axis='y',style='sci',scilimits=(0,1))    
    ax.figure.canvas.draw()
    
def logify(ax,axis='x'):
    if axis=='x' or axis=='both':
        xmin,_=ax.get_xlim()
        if xmin<=0:
            ax.set_xlim(xmin=.01)
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(_ticker.ScalarFormatter())
    if axis=='y'or axis=='both':
        ymin,_=ax.get_ylim()
        if ymin<=0:
            ax.set_ylim(ymin=.01)
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(_ticker.ScalarFormatter())
        
class OOMFormatter(_ticker.ScalarFormatter):
    def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
        """Order of magnitude formatter"""
        self.oom = order
        self.fformat = fformat
        super().__init__(useOffset=offset,useMathText=mathText)
    def _set_orderOfMagnitude(self, nothing=None):
        self.orderOfMagnitude = self.oom
    def _set_format(self, vmin=None, vmax=None):
        self.format = self.fformat
        if self._useMathText:
            self.format = '$%s$' % mpl.ticker._mathdefault(self.format)

def addGrid(fig,vlines=50,hlines=50):
    tempgrid=mpl.gridspec.GridSpec(1,1,bottom=0,left=0,top=1,right=1)
    gridax=fig.add_subplot(tempgrid[:,:])
    gridax.grid(lw=.5,color='grey',alpha=.5)
    gridax.xaxis.set_ticks(np.linspace(0,1,vlines))
    gridax.yaxis.set_ticks(np.linspace(0,1,hlines))
    gridax.patch.set_alpha(0) 
    return gridax