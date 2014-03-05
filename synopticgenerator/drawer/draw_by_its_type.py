""" coding: utf-8 """

import cv2
import logging

#import numpy
#from PIL import Image

import synopticgenerator.util as util
#import synopticgenerator.log as log
import synopticgenerator.region as region

from synopticgenerator.drawer import ObjectDrawer
import synopticgenerator.drawer.rectangle as rectangle
import synopticgenerator.drawer.polygon as polygon
import synopticgenerator.drawer.circle as circle
from synopticgenerator.error import InvalidColorConfig


class DrawByType(ObjectDrawer):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.rect_drawer = rectangle.Drawer(config, environ)
        self.poly_drawer = polygon.Drawer(config, environ)
        self.circle_drawer = circle.Drawer(config, environ)

        self.target = config.setdefault("target", "regions")
        self.outline = config.setdefault("outline", True)
        self.thickness = config.setdefault("thickness", 3)
        self.outline_thickness = config.setdefault("outline_thickness", 6)

        color_table = environ.setdefault("color_table", None)
        color = config.setdefault("color", None)
        if color:
            self.color = util.color(color, color_table)
        else:
            self.color = None
        self.outline_color = util.color(
            config.setdefault("outline_color", "111, 111, 111"),
            color_table)

    def execute(self, content):
        if not content.get(self.target):
            return content

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
        if type(bound) is region.rect:
            return self.rect_drawer.draw(image, bound, color)
        elif type(bound) is region.rotated_rect:
            return self.poly_drawer.draw(image, bound, color)
        elif type(bound) is region.rotated_rect:
            return self.circle_drawer.draw(image, bound, color)

        else:
            logging.error("not found drawer for this region")
            return image


def create(config, environ):
    return DrawByType(config, environ)
