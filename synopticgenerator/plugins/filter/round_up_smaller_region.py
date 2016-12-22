""" coding: utf-8 """

import logging
from synopticgenerator.plugins import Pipeline


class RoundUpSmallerRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.baseline = self.config.get("baseline", 175)

    def execute(self, content):

        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        ctrls = self.controls or content[self.region]
        for shape in ctrls:
            ratio = self.baseline / shape.area
            if 1.0 < ratio:
                logging.debug("round_up_rect: shape: {}, ratio is:{}".format(shape.name, ratio))
                shape.scale(ratio)

        return content


def create(config, environ):
    return RoundUpSmallerRegion(config, environ)
