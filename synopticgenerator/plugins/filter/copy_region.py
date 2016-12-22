""" coding: utf-8 """

import copy
import synopticgenerator.log as log
from synopticgenerator.plugins import Pipeline


class CopyRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.src = self.config.setdefault("src", None)
        self.dst = self.config.setdefault("dst", None)

    def check_config(self):
        if not self.config.get("src"):
            raise Pipeline.ConfigInvalid("src")

    def execute(self, content):
        if not content.get(self.src):
            raise Pipeline.RegionNotFound(self.src)

        if content.get(self.dst):
            log.warn("already exists region {}".format(self.dst))

        content[self.dst] = copy.deepcopy(content.get(self.src))

        return content


def create(config, environ):
    return CopyRegion(config, environ)
