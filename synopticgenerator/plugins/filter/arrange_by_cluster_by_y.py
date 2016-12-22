﻿""" coding: utf-8 """

import synopticgenerator.plugins.filter.arrange_by_cluster_by_axis as arrange_by_cluster_by_axis
from synopticgenerator.plugins import Pipeline


class ArrangeByClusterY(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.margin = self.config.setdefault("margin", 8)
        # self.config.setdefault('draw_debug', False)

        self.config.setdefault("threshold", 1e-4)
        self.config.setdefault('draw_debug', False)

    def execute(self, content):
        self.config["axis"] = "y"

        mod = arrange_by_cluster_by_axis.create(self.config, self.environ)
        content = mod.execute(content)

        return content


def create(config, environ):
    return ArrangeByClusterY(config, environ)