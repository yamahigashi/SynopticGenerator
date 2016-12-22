""" coding: utf-8 """

import synopticgenerator.shape as shape
from synopticgenerator.plugins import Pipeline


class MinimumWidthHeight(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.baseline = self.config.setdefault("baseline", 9)
        self.height = self.config.setdefault("height", None)
        self.width = self.config.setdefault("width", None)

    def execute(self, content):
        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        mini = self.config.get("baseline")
        height = self.config.get("height")
        width = self.config.get("width")
        ctrls = self.controls or content[self.region]

        for ctrl in ctrls:
            if isinstance(ctrl, shape.Rect):

                if width and ctrl.w < width:
                    ctrl.scale_x(float(width) / ctrl.w)
                if height and ctrl.h < height:
                    ctrl.scale_y(float(height) / ctrl.h)

                if ctrl.w < mini:
                    ctrl.scale_x(float(mini) / ctrl.w)
                if ctrl.h < mini:
                    ctrl.scale_y(float(mini) / ctrl.h)

        return content


def create(config, environ):
    return MinimumWidthHeight(config, environ)
