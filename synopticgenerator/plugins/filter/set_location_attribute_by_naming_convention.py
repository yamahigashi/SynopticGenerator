""" coding: utf-8 """

import re
import logging

# import synopticgenerator.util as util
from synopticgenerator.plugins import Pipeline
import synopticgenerator.shape as shape


class SetLocationAttributeByNamingConvention(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.config.setdefault("target", [])
        self.config.setdefault("convention", None)

    def check_config(self):
        # type: () -> None

        if not self.config.get("convention"):
            raise Pipeline.ConfigInvalid("convention")

    def read_convention(self):
        # type: () -> None

        self.convetion = self.config.get("convention")
        self.default = self.convetion.get("default", shape.LocationAttributeCenter)

        _l = self.convetion.get("left", None)
        _r = self.convetion.get("right", None)
        _c = self.convetion.get("center", None)
        if _l:
            self.convention_l = {'expr': re.compile(_l), 'attr': shape.LocationAttributeLeft}
        else:
            self.convention_l = None

        if _r:
            self.convention_r = {'expr': re.compile(_r), 'attr': shape.LocationAttributeRight}
        else:
            self.convention_r = None

        if _c:
            self.convention_c = {'expr': re.compile(_c), 'attr': shape.LocationAttributeCenter}
        else:
            self.convention_c = None

    def execute(self, content):
        self.read_convention()

        for target in self.config.get("target"):
            regions = content.get(target)
            if not regions:
                raise Pipeline.RegionNotFound(target)

            for region in regions:
                self.apply_conventions(region)

        return content

    def apply_conventions(self, ctrl):
        for convention in [self.convention_l, self.convention_r, self.convention_c]:
            if not convention:
                continue

            if convention['expr'].search(ctrl.name):
                ctrl.location = convention['attr']()
                logging.debug("setting location attribute for region: {}, location: {}".format(
                    ctrl.name, ctrl.location))

                break

        else:
            ctrl.location = self.default
            logging.debug("setting location attribute as default for region: {}, location: {}".format(
                ctrl.name, ctrl.location))


def create(config, environ):
    return SetLocationAttributeByNamingConvention(config, environ)
