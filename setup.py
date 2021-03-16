#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2021/03/16 下午2:03:50

import sdist_upip
from setuptools import setup
import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
sys.path.append("..")

setup(
    name='micropython-am7020',
    version='1.0.0',
    author='Zack Huang',
    author_email='zack@atticedu.com',
    description='AT Command library dedicated to am7020 http mqtt',
    long_description='',
    url='https://github.com/JiekangHuang/MicroPython-AM7020',
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    package_dir={'micropython-am7020': 'am7020'},
    packages=['micropython-am7020']
)
