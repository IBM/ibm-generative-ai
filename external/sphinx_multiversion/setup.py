#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="sphinx-multiversion",
    description="Add support for multiple versions to sphinx",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    author="Jan Holthuis",
    author_email="holthuis.jan@googlemail.com",
    url="https://holzhaus.github.io/sphinx-multiversion/",
    version="0.2.4",
    install_requires=["sphinx >= 2.1"],
    license="BSD",
    packages=["sphinx_multiversion"],
    entry_points={
        "console_scripts": [
            "sphinx-multiversion=sphinx_multiversion:main",
        ],
    },
)
