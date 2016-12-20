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

CURRENT_PATH = os.path.dirname(__file__)
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi+git@gmail.com"
__status__ = "Prototype"
##############################################################################


class SynopticGenerator(object):

    def __init__(self):
        self.environ = None
        self.pipelines = None

    def load(self, yaml_stream):
        config = yaml.load(yaml_stream, OrderedDictYAMLLoader)
        self.environ = config.setdefault("global", {})
        self.pipelines = config.setdefault("pipeline", [])
        self.environ["recipe_name"] = os.path.splitext(yaml_stream.name)[0]

        self.start_logging(self.environ)
        self.load_after(config)

    def load_after(self, config):
        # type: (Dict[str, object])
        ''' set plugin path

        plugin loading path sequence order is
         1. current directory
         2. plugin path in config file.
         3. this module directory path for the standard plugins.
        '''

        self.initialize_environ()
        self.environ.setdefault("plugin_path", ["."])
        if "." not in self.environ["plugin_path"]:
            self.environ["plugin_path"].insert(0, ".")
        if CURRENT_PATH not in self.environ["plugin_path"]:
            self.environ["plugin_path"].append(CURRENT_PATH)

    def initialize_environ(self):
        self.environ.setdefault("location_expression", "_(L|R|C)\\d+_")
        self.environ.setdefault("location_label", {"left": "L", "right": "R", "center": "C"})

    def start_logging(self, environ):
        # type: (Dict(str, object))
        level = environ.setdefault("log_level", "INFO")
        filename = environ.setdefault("log_file", None)
        formatter = environ.setdefault("log_format", log.DEFAULT_FORMATTER)

        log.start(filename=filename, level=level, formatter=formatter)

    def add_plugin_path(self, path):
        # type: (Dict(str, object))
        p = path + self.environ["plugin_path"]
        self.environ["plugin_path"] = list(set(p))

    def run_all(self):
        # type: () -> Dict(str, object)
        res = {}
        for k in self.pipelines.keys():
            res = self.run_line(k, res)
        return res

    def run_line(self, pipeline, content=None):
        # type: (List(Dict(str, object)), Dict(str, object)) -> Dict(str, object)
        """ run by pipeline name(filter, recognizer, publish) """

        line = self.pipelines[pipeline]
        lines = [self.instantiate(line_module) for line_module in line]
        res = content
        for l in lines:
            logging.info("execute {}".format(type(l).__module__))
            res = l.execute(res)
        return res

    def instantiate(self, line):
        # type: () -> Pipeline
        """ return SynopticGenerator plugin module instance. """

        logging.info("start instantiate %s" % line["module"])
        module = util.load_module(
            line["module"], self.environ["plugin_path"])
        config = line.setdefault("config", {})
        obj = module.create(config, self.environ)

        if hasattr(obj, "set_submodules"):
            logging.info("{} has sub modules".format(obj.__module__))
            sub_modules = line.get("sub-modules", [])
            sub_module_instances = [
                self.instantiate(smod) for smod in sub_modules]
            obj.set_submodules(sub_module_instances)

        return obj


class Pipeline(object):
    """ SynopticGenerator's pipeline base class """


def create(config_path):
    sc = SynopticGenerator()
    with open(config_path) as c:
        sc.load(c)
    sc.run_all()
