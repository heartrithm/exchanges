#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="exchanges",
    version="1.2.2",
    description="Exchange APIs",
    packages=find_packages(),
    install_requires=["arrow", "requests", "requests_cache", "ujson"],
)
