""" coding: utf-8 """

import os
from PIL import Image

import logging

from synopticgenerator.plugins import Pipeline


class SetSizeFromImage(Pipeline):
    ''' Set width and height for environ from given image size '''

    def set_default_config(self):
        # type: () -> None

        self.config.setdefault("image", [])

    def check_config(self):
        # type: () -> None

        if not self.config.get("image"):
            raise Pipeline.ConfigInvalid("image")

    def execute(self, content):
        w, h = [0, 0]

        for image_path in self.config["image"]:
            if not os.path.exists(image_path):
                logging.error("file not found: {0}".format(image_path))
                continue

            img = Image.open(image_path)
            x, y = img.size

            w = x if w < x else w
            h = y if h < y else h

        self.environ["width"] = w
        self.environ["height"] = h

        return content


def create(config, environ):
    return SetSizeFromImage(config, environ)
