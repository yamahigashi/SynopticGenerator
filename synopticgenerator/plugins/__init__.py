""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################
import abc

from synopticgenerator.environment import Environment, Config


class Pipeline(object):
    """ SynopticGenerator's pipeline base class """

    __metaclass__ = abc.ABCMeta

    def __init__(self, config, environ, *args, **kwargs):
        # type: (Config, Environment, *str, **str) -> None

        self.config = config
        self.environ = environ
        self.set_default_config()
        self.check_config()
        self.after_set_config()

    def after_set_config(self):
        # type: () -> None

        pass

    @abc.abstractmethod
    def execute(self, content):
        # type: (Dict[str, object]) -> Dict[str, object]
        pass

    # @abc.abstractmethod
    def set_default_config(self):
        # type: () -> None
        pass

    # @abc.abstractmethod
    def check_config(self):
        # type: () -> None
        pass

    class ConfigInvalid(Exception):

        def str(self, key):
            return "Configuration \"{}\" is not propery set".format(key)

    class RegionNotFound(Exception):

        def str(self, v):
            return "Region named {} not found in content".format(v)
