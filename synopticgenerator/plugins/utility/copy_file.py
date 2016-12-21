""" coding: utf-8 """

import shutil
import logging

from synopticgenerator.plugins import Pipeline


class FileRemover(Pipeline):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.files = config.setdefault("file", "")

    def execute(self, content):
        src = self.config["src"]
        dst = self.config["dst"]

        logging.info("copying file from {} to {}".format(src, dst))
        shutil.copy(src, dst)

        return content


def create(config, environ):
    return FileRemover(config, environ)
