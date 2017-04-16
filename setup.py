#!/usr/bin/env python3
import sys
import setuptools
from distutils.core import setup

if sys.version_info < (3, 6, ):
    print('Sorry, TemperFM Charts requires Python 3.6+')
    exit(1)

base_package = 'temperfm_charts'
version = __import__(base_package).__version__
packages = [base_package] + ['{}.{}'.format(base_package, package)
                             for package in setuptools.find_packages(base_package)]

setup(
    name=base_package,
    description='Last.fm listening data chart generator',
    url='https://github.com/broiledmeat/temperfm_charts',
    license='Apache License, Version 2.0',
    author='Derrick Staples',
    author_email='broiledmeat@gmail.com',
    version=version,
    packages=packages,
    scripts=['scripts/temperfm'],
    requires=['temperfm', 'docopt', 'svgwrite'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)
