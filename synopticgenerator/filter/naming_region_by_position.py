""" coding: utf-8 """

import logging
from synopticgenerator import Pipeline


class NamingRegion(Pipeline):
    ''' apply name to region '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)
        self.skip_named = config.setdefault("skip_named", False)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        sorted_region = sorted(
            content[self.region], key=lambda x: int(x.center[1]))

        empty_name = [x for x in sorted_region if not x.name]
        if len(empty_name) != len(self.controls):
            logging.debug("all: {} / empty: {} / apply: {}".format(
                len(sorted_region), len(empty_name), len(self.controls)))
            logging.warn(
                "does not match empty region count with apply names count")
        for i, x in enumerate(empty_name):
            if self.skip_named and x.name:
                continue
            try:
                x.name = self.controls[i]
            except IndexError:
                print x

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return NamingRegion(config, environ)
