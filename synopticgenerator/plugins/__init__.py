""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################
import abc


class Pipeline(object):
    """ SynopticGenerator's pipeline base class """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, content):
        # type: (Dict[str, object]) -> Dict[str, object]
        pass

    # @abc.abstractmethod
    def set_default_config(self):
        # type: () -> None
        pass
