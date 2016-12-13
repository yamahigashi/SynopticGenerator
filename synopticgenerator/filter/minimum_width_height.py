""" coding: utf-8 """

# import logging


class MinimumWidthHeight(object):
    '''  '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)
        self.baseline = config.setdefault("baseline", 10)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        mini = self.config.get("baseline")

        for shape in content[self.region]:
            if "rect'" in str(type(shape)):
                if shape.w < mini:
                    shape.scale_x(float(mini) / shape.w)
                if shape.h < mini:
                    shape.scale_y(float(mini) / shape.h)

        return content


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return MinimumWidthHeight(config, environ)
