""" coding: utf-8 """


import xml.sax.saxutils as saxutils
import logging

from synopticgenerator.plugins import Pipeline


class HTMLCharacter(Pipeline):
    ''' manipulate HTML charcter '''

    def set_default_config(self):
        # type: () -> None

        self.file = self.config.setdefault("file", None)
        self.mode = self.config.setdefault("mode", "")

    def check_config(self):
        # type: () -> None

        if not self.file:
            raise Pipeline.ConfigInvalid("file")

        if not self.mode:
            raise Pipeline.ConfigInvalid("mode")

        if "escape" not in self.mode and "unescape" not in self.mode:
            raise Pipeline.ConfigInvalid("mode is [\"escape\", \"unescape\"")

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

        return content


def create(config, environ):
    return HTMLCharacter(config, environ)
