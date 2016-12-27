""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################
import os
from collections import OrderedDict


CURRENT_PATH = os.path.dirname(__file__)
DEFAULT_PLUGIN_PATH = os.path.join(CURRENT_PATH, "plugins")


class Environment(OrderedDict):

    def __init__(self, other=None):
        # type: (OrderedDict) -> None

        super(Environment, self).__init__()

        if other is not None:
            for k, v in other.iteritems():
                self[k] = v

        self.set_default_environment()
        self.set_default_plugin_path()

    def set_default_environment(self):

        self.setdefault("location_expression", "_(L|R|C)\\d+_")
        self.setdefault("location_label", {"left": "L", "right": "R", "center": "C"})
        self.setdefault("height", 550)
        self.setdefault("width", 300)

    def set_default_plugin_path(self):
        # type: () -> None
        '''set plugin path.

        plugin loading path sequence order is
         1. current directory
         2. plugin path in config file.
         3. this module directory path for the standard plugins.
        '''

        self.setdefault("plugin_path", ["."])
        if "." not in self["plugin_path"]:
            self["plugin_path"].insert(0, ".")

        if DEFAULT_PLUGIN_PATH not in self["plugin_path"]:
            self["plugin_path"].append(DEFAULT_PLUGIN_PATH)

    def add_plugin_path(self, path):
        # type: (str) -> None

        p = path + self["plugin_path"]
        self["plugin_path"] = list(set(p))


class Config(OrderedDict):

    def __init__(self, other=None):
        # type: (OrderedDict) -> None

        super(Config, self).__init__()

        if other is not None:
            for k, v in other.iteritems():
                self[k] = v
