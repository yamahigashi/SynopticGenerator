""" coding: utf-8 """


import synopticgenerator.util as util
from synopticgenerator.plugins import Pipeline


class SetColorRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.color_table = self.environ.setdefault("color_table", None)

        self.region = self.config.setdefault("region", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.color = self.config.setdefault("color", None)

    def check_config(self):
        if not self.config.get("color"):
            raise Pipeline.ConfigInvalid("color")

    def execute(self, content):
        ctrls = self.controls or content[self.region]

        if not ctrls:
            raise Pipeline.RegionNotFound(self.region)

        for r in ctrls:
            r.color = util.color(self.config["color"], self.color_table)

        return content


def create(config, environ):
    return SetColorRegion(config, environ)
