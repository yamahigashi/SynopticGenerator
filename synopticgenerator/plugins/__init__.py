""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################

import os
import yaml

import synopticgenerator.util as util
from synopticgenerator.yamlordereddict import OrderedDictYAMLLoader
import synopticgenerator.log as log
import logging


class Pipeline(object):
    """ SynopticGenerator's pipeline base class """
