#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/11 下午2:03:50

import setuptools

# with open("README.md", "r") as fh:
    # long_description = fh.read()

setuptools.setup(
    name="micropython-am7020",
    version="1.0.0",
    author="Zack Huang",
    author_email="zack@atticedu.com",
    description="AT Command library dedicated to am7020 http mqtt",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/JiekangHuang/am7020_raspberry",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
