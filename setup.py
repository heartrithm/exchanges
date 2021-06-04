#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="exchanges",
    version="1.3.5",
    description="Exchange APIs",
    packages=find_packages(),
    install_requires=["arrow", "loguru", "requests", "ujson"],
)
