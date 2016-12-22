""" coding: utf-8 """

import logging
from synopticgenerator.plugins import Pipeline


class RoundDownBiggerRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.baseline = self.config.get("baseline", 2000)

    def execute(self, content):
        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        ctrls = self.controls or content[self.region]
        for shape in ctrls:
            ratio = self.baseline / shape.area
            if ratio < 1.0:
                logging.debug("round_up_rect: shape: {}, ratio is:{}".format(shape.name, ratio))
                shape.scale(ratio)

        return content


def create(config, environ):
    return RoundDownBiggerRegion(config, environ)
