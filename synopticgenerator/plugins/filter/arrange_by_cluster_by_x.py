""" coding: utf-8 """

# import copy
# import bisect
# import logging

import synopticgenerator.plugins.filter.arrange_by_cluster_by_axis as arrange_by_cluster_by_axis
from synopticgenerator.plugins import Pipeline


class ArrangeByClusterX(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def set_default_config(self):
        # type: () -> None

        self.environ.setdefault("width", 320)
        self.environ.setdefault("height", 550)

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.margin = self.config.setdefault("margin", 8)
        # self.config.setdefault('draw_debug', False)

        self.config.setdefault("threshold", 1e-4)
        self.config.setdefault('draw_debug', False)

    def execute(self, content):
        self.config["axis"] = "x"

        mod = arrange_by_cluster_by_axis.create(self.config, self.environ)
        content = mod.execute(content)

        return content


def create(config, environ):
    return ArrangeByClusterX(config, environ)
