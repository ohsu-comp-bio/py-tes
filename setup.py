#!/usr/bin/env python

from __future__ import print_function

import os

from setuptools import setup


SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.md')

setup(
    name='tes',
    version='0.1',
    description='Library for communicating with the GA4GH Task Execution API',
    long_description=open(README).read(),
    author='Adam Struck',
    author_email='strucka@ohsu.edu',
    url="https://github.com/ohsu-comp-bio/py-tes",
    download_url="https://github.com/ohsu-comp-bio/py-tes",
    license='MIT',
    install_requires=[
        "attrs>=17.2.0",
        "polling>=0.3.0",
        "requests>=2.18.1",
    ],
    zip_safe=True
)
