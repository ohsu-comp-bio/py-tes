#!/usr/bin/env python

import io
import os
import re

from setuptools import setup, find_packages


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="py-tes",
    version=find_version("tes", "__init__.py"),
    description="Library for communicating with the GA4GH Task Execution API",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="OHSU Computational Biology",
    author_email="CompBio@ohsu.edu",
    maintainer="Kyle Ellrott",
    maintainer_email="kellrott@gmail.com",
    url="https://github.com/ohsu-comp-bio/py-tes",
    license="MIT",
    packages=find_packages(),
    python_requires=">=2.7, <4",
    install_requires=[
        "attrs>=17.4.0",
        "future>=0.16.0",
        "python-dateutil==2.6.1",
        "requests>=2.18.1"
    ],
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
)
