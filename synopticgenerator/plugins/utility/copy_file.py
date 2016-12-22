""" coding: utf-8 """

import shutil
import logging

from synopticgenerator.plugins import Pipeline


class FileRemover(Pipeline):

    def set_default_config(self):
        # type: () -> None
        self.files = self.config.setdefault("file", "")
        self.src = self.config.setdefault("src", None)
        self.dst = self.config.setdefault("dst", None)

    def check_config(self):
        # type: () -> None

        if not self.src:
            raise Pipeline.ConfigInvalid("src")
        if not self.dst:
            raise Pipeline.ConfigInvalid("dst")

    def execute(self, content):
        logging.info("copying file from {} to {}".format(self.src, self.dst))
        shutil.copy(self.src, self.dst)

        return content


def create(config, environ):
    return FileRemover(config, environ)
