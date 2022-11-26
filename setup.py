#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="exchanges",
    version="1.3.9",
    description="Cryptocurrency Exchange APIs",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=["arrow", "cachetools", "loguru", "ratelimiter", "requests", "ujson"],
)
