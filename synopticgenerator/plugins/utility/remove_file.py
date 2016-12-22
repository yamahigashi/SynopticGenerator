""" coding: utf-8 """


import logging

from synopticgenerator.plugins import Pipeline


class FileRemover(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.files = self.config.setdefault("file", [])

    def check_config(self):
        # type: () -> None

        if not self.files:
            raise Pipeline.ConfigInvalid("file")

    def _remove(self, f):
        try:
            import send2trash
            logging.info("send 2 trash: {0}".format(f))
            send2trash.send2trash(f)

        except ImportError:
            import os
            logging.warn("REMOVE file: {0}".format(f))
            os.remove(f)

        except NameError:
            import os
            logging.warn("REMOVE file: {0}".format(f))
            os.remove(f)

    def execute(self, content):
        if isinstance(self.files, list):
            for f in self.files:
                self._remove(f)
        else:
            self._remove(self.files)

        return content


def create(config, environ):
    return FileRemover(config, environ)
