#!/usr/bin/env python
""" Repo pricer : hard coded get DF poc version """

from setuptools import setup, find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(name='quantitativeTool',version='1.0.0',
description='quantitative tools for data analysis and quantitative finance', long_description=long_description,
license='Apache-2.0',
include_package_data = True,
zip_safe=False,
packages=find_packages()
)