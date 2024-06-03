# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from .basic import *
from .math import *
from .plot_tools import *
from .loadsave import *
from kimpl import *
import matplotlib
# from numpy import *

try:
    matplotlib.style.use('basic')
except:
    print("Could not find 'basic' mpl style")
    
___last_updated="Jan 4, 2023"
