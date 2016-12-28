""" coding: utf-8 """

import cv2
import logging

import synopticgenerator.util as util
import synopticgenerator.shape as shape
from synopticgenerator.plugins import Pipeline

from synopticgenerator.plugins.drawer import ObjectDrawer
import synopticgenerator.plugins.drawer.rectangle as rectangle
import synopticgenerator.plugins.drawer.polygon as polygon
import synopticgenerator.plugins.drawer.circle as circle
from synopticgenerator.error import InvalidColorConfig


class DrawByType(ObjectDrawer):

    def set_default_config(self):
        # type: () -> None

        self.target = self.config.setdefault("target", "regions")
        self.outline = self.config.setdefault("outline", True)
        self.thickness = self.config.setdefault("thickness", 3)
        self.outline_thickness = self.config.setdefault("outline_thickness", 6)

        color_table = self.environ.setdefault("color_table", None)
        color = self.config.setdefault("color", None)
        if color:
            self.color = util.color(color, color_table)
        else:
            self.color = None
        self.outline_color = util.color(
            self.config.setdefault("outline_color", "111, 111, 111"),
            color_table)

    def initialize_drawer(self):
        # type: () -> None

        self.rect_drawer = rectangle.Drawer(self.config, self.environ)
        self.poly_drawer = polygon.Drawer(self.config, self.environ)
        self.circle_drawer = circle.Drawer(self.config, self.environ)

    def execute(self, content):
        if not content.get(self.target):
            raise Pipeline.RegionNotFound(self.target)

        self.initialize_drawer()

        canvas = self.config["canvas"]
        image = cv2.imread(canvas)
        for r in content[self.target]:
            if not self.color and not r.color:
                raise InvalidColorConfig()
            if self.color:
                image = self.draw(image, r, self.color)
            else:
                image = self.draw(image, r, r.color)

        util.ensure_folder(self.config["output"])
        cv2.imwrite(self.config["output"], image)

        return content

    def draw(self, image, bound, color):
        if type(bound) is shape.Rect:
            return self.rect_drawer.draw(image, bound, color)
        elif type(bound) is shape.RotatedRect:
            return self.poly_drawer.draw(image, bound, color)
        elif type(bound) is shape.RotatedRect:
            return self.circle_drawer.draw(image, bound, color)

        else:
            logging.error("not found drawer for this region")
            return image


def create(config, environ):
    return DrawByType(config, environ)
