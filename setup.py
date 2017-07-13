#!/usr/bin/env python

from __future__ import print_function

import os

from setuptools import setup


SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.md')

setup(
    name='py-tes',
    version='0.1',
    description='Library for communicating with the GA4GH Task Execution API',
    long_description=open(README).read(),
    author='Adam Struck',
    author_email='strucka@ohsu.edu',
    url="https://github.com/ohsu-comp-bio/py-tes",
    download_url="https://github.com/ohsu-comp-bio/py-tes",
    license='MIT',
    install_requires=[
    ],
    zip_safe=True
)
