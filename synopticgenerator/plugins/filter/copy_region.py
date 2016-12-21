""" coding: utf-8 """

import copy
import synopticgenerator.log as log
from synopticgenerator import Pipeline


class CopyRegion(Pipeline):
    ''' :w '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.src = config["src"]
        self.dst = config["dst"]

    def execute(self, content):
        if not content.get(self.src):
            raise RegionNotFound(self.src)
        if content.get(self.dst):
            log.warn("already exists region {}".format(self.dst))
            #raise RegionNotFound(self.dst)

        content[self.dst] = copy.deepcopy(content.get(self.src))

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return CopyRegion(config, environ)
