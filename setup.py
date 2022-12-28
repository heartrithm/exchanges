#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="exchanges",
    version="1.4",
    description="Cryptocurrency Exchange APIs",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=["arrow", "cachetools", "loguru", "requests", "ujson"],
)
