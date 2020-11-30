#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="exchanges",
    version="1.2.1",
    description="Exchange APIs",
    packages=find_packages(),
    install_requires=["requests", "ujson"],
)
