""" coding: utf-8 """

import logging
from synopticgenerator.plugins import Pipeline


class RoundUpSmallerRegion(Pipeline):
    ''' :w '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)
        self.baseline = config.get("baseline", 175)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        for shape in content[self.region]:
            ratio = self.baseline / shape.area
            if 1.0 < ratio:
                logging.debug("round_up_rect: shape: {}, ratio is:{}".format(shape.name, ratio))
                shape.scale(ratio)

        return content


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return RoundUpSmallerRegion(config, environ)
