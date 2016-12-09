""" coding: utf-8 """


import logging


class FileRemover(object):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.files = config.setdefault("file", "")

    def _remove(self, f):
        try:
            import send2trash
            logging.info("send 2 trash: {0}".format(f))
            send2trash.send2trash(f)
        except ImportError:
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
