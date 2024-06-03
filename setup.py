# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 14:11:20 2023

@author: TSM
"""

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.0'
PACKAGE_NAME = 'KellysTools'
AUTHOR = 'Kelly Wilson'
AUTHOR_EMAIL = 'kelmaxx@gmail.com'
URL = ''

LICENSE = 'Apache License 2.0'
DESCRIPTION = 'A collection of tools I normally use'
LONG_DESCRIPTION = "" #(HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'kimpl',
      'matplotlib',
      'numpy',
      'PyQt5',
      'lmfit',
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      include_package_data=True,
      package_data={'KellysTools':['*.wav']},
      zip_safe=False
      )