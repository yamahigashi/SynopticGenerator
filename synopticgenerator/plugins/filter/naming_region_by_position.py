""" coding: utf-8 """

import logging
from synopticgenerator.plugins import Pipeline


class NamingRegion(Pipeline):
    ''' apply name to region '''

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.skip_named = self.config.setdefault("skip_named", False)

    def execute(self, content):
        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        sorted_region = sorted(
            content[self.region], key=lambda x: int(x.center[1]))

        empty_name = [x for x in sorted_region if not x.name]
        if len(empty_name) != len(self.controls):
            dbg_msg = "all: {} / empty: {} / apply: {}".format(
                len(sorted_region), len(empty_name), len(self.controls))
            wrn_msg = "does not match empty region count with apply names count"

            logging.debug(dbg_msg)
            logging.warn(wrn_msg)

        for i, x in enumerate(empty_name):
            if self.skip_named and x.name:
                continue

            try:
                x.name = self.controls[i]
            except IndexError:
                logging.error(x)

        return content


def create(config, environ):
    return NamingRegion(config, environ)
