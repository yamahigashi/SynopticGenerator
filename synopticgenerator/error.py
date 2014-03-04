""" coding: utf-8 """
# Copyright 2014, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################


class InvalidColorConfig(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return "config 'color' not supplied on \
                region nor drawer.rectangle:{}".format(repr(self.value))
