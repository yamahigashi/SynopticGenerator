""" coding: utf-8 """
from synopticgenerator.plugins import Pipeline


class DumpRegion(Pipeline):
    ''' manipulate HTML charcter '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        for x in content[self.region]:
            print('name: {} shape: "{}", center: "{}", color: "{}"'.format(
                x.name, x.__class__.__name__, str(x.center), str(x.color)))

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return DumpRegion(config, environ)
