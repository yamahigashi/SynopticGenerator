""" coding: utf-8 """

import re
import logging

# import synopticgenerator.util as util


class SetLocationAttributeByNamingConvention(object):
    ''' :w '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.convetion = config["convention"]
        self.default = self.convetion.get("default", "center")

        _l = self.convetion.get("left", None)
        _r = self.convetion.get("right", None)
        _c = self.convetion.get("center", None)
        if _l:
            self.convention_l = {'expr': re.compile(_l), 'attr': 'left'}
        else:
            self.convention_l = None

        if _r:
            self.convention_r = {'expr': re.compile(_r), 'attr': 'right'}
        else:
            self.convention_r = None

        if _c:
            self.convention_c = {'expr': re.compile(_c), 'attr': 'center'}
        else:
            self.convention_c = None

    def execute(self, content):
        for target in self.config.get("target", []):
            regions = content.get(target)
            if not regions:
                raise RegionNotFound(target)

            for region in regions:
                self.apply_conventions(region)

        return content

    def apply_conventions(self, region):
        for convention in [self.convention_l, self.convention_r, self.convention_c]:
            if not convention:
                continue

            if convention['expr'].match(region.name):
                region.location = convention['attr']
                logging.debug("setting location attribute for region: {}, location: {}".format(
                    region.name, region.location))

                break

        else:
            region.location = self.default
            logging.debug("setting location attribute as default for region: {}, location: {}".format(
                region.name, region.location))


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return SetLocationAttributeByNamingConvention(config, environ)
