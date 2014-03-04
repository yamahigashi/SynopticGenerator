""" coding: utf-8 """
# Copyright 2014, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi+git@gmail.com"
__status__ = "Prototype"

from setuptools import setup, find_packages

setup(
    name="synopticgenerator",
    packages=find_packages(),
    install_requires=["enum34"])
