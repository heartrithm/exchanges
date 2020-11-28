#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="exchanges",
    version="1.1.7",
    description="Exchange APIs",
    packages=find_packages(),
    install_requires=["requests", "ujson"],
)
