""" coding: utf-8 """

from synopticgenerator import Pipeline


class ConcatRegion(Pipeline):
    ''' :w '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.a = config["region_a"]
        self.b = config["region_b"]
        self.store = config["store"]

    def execute(self, content):
        if not content.get(self.a):
            raise RegionNotFound(self.a)
        if not content.get(self.b):
            raise RegionNotFound(self.b)

        cat = []
        cat.extend(content.get(self.a))
        cat.extend(content.get(self.b))

        content[self.store] = cat

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return ConcatRegion(config, environ)
