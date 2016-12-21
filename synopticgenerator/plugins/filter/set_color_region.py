""" coding: utf-8 """


import synopticgenerator.util as util
from synopticgenerator.plugins import Pipeline


class SetColorRegion(Pipeline):
    ''' :w '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.color_table = environ.setdefault("color_table", None)
        self.region = config.setdefault("region", "regions")
        self.color = config["color"]

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        for r in content[self.region]:
            r.color = util.color(self.config["color"], self.color_table)

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return SetColorRegion(config, environ)
