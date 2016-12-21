""" coding: utf-8 """


import xml.sax.saxutils as saxutils
import logging

from synopticgenerator import Pipeline


class HTMLCharacter(Pipeline):
    ''' manipulate HTML charcter '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.file = config.setdefault("file", None)
        self.mode = config.setdefault("mode", "")

    def unescape(self, fo):
        logging.info("unescape: {}".format(fo))
        if self.file:
            with open(fo, 'r') as f:
                data = f.read()
            ndata = saxutils.unescape(data)
            with open(fo, 'w') as f:
                f.write(ndata)

    def escape(self, fo):
        logging.info("escape: {}".format(fo))
        logging.error("not implemented yet")

    def execute(self, content):
        if self.mode == "escape":
            self.escape(self.file)
        elif self.mode == "unescape":
            self.unescape(self.file)
        else:
            raise

        return content


def create(config, environ):
    return HTMLCharacter(config, environ)
