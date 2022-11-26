#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="exchanges",
    version="1.3.8",
    description="Exchange APIs",
    packages=find_packages(),
    install_requires=["arrow", "cachetools", "loguru", "ratelimiter", "requests", "ujson"],
)
