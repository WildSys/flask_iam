#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import setuptools
import os

# Load env
version = None
local_dir = os.path.abspath(os.path.dirname(__file__))
with open(f'{local_dir}/VERSION') as hdr:
    version = hdr.readline().strip()

# Package declaration
setuptools.setup(
    name='flask_iam',
    version=version,
    author='WildSys',
    author_email='contact@wildsys.io',
    description='IAM management',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'Flask>=2.1.0'
    ]
)
