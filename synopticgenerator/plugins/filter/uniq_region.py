""" coding: utf-8 """
from synopticgenerator.plugins import Pipeline


class UniqRegion(Pipeline):
    ''' :w '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        seen = set()
        seen_add = seen.add
        uniq = [x for x in content[self.region]
                if x.center not in seen and not seen_add(x.center)]
        content[self.region] = uniq

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return UniqRegion(config, environ)
