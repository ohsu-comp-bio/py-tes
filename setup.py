#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

setup(
    name='py-tes',
    version='0.1.0',
    description='Library for communicating with the GA4GH Task Execution API',
    author='OHSU Computational Biology',
    author_email='CompBio@ohsu.edu',
    maintainer='Adam Struck',
    maintainer_email='strucka@ohsu.edu',
    url="https://github.com/ohsu-comp-bio/py-tes",
    license='MIT',
    packages=find_packages(),
    python_requires='>=2.6, <3',
    install_requires=[
        "attrs>=17.2.0",
        "polling>=0.3.0",
        "requests>=2.18.1",
        "PyYAML>=3.12"
    ],
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
    ],
)
