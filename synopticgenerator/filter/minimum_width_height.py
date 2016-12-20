""" coding: utf-8 """

import synopticgenerator.shape as shape
from synopticgenerator import Pipeline


class MinimumWidthHeight(Pipeline):
    '''  '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.baseline = config.setdefault("baseline", 9)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        mini = self.config.get("baseline")

        for ctrl in content[self.region]:
            if isinstance(ctrl, shape.Rect):
                if ctrl.w < mini:
                    ctrl.scale_x(float(mini) / ctrl.w)
                if ctrl.h < mini:
                    ctrl.scale_y(float(mini) / ctrl.h)

        return content


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return MinimumWidthHeight(config, environ)
