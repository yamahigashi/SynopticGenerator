""" coding: utf-8 """

import cv2
import numpy
from PIL import Image

from synopticgenerator.drawer import ObjectDrawer
import synopticgenerator.util as util
#import synopticgenerator
from synopticgenerator.error import InvalidColorConfig


class Drawer(ObjectDrawer):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

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

    def drawpoly(self, canvas, bound, color, thickness, linetype=4, shift=0):
        #b1 = bound.top_left
        #b2 = bound.bottom_right

        # cv2.rectangel not support alpha blend, then draw on empty image
        # next blend tmp image on canvas with alpha
        if color.has_alpha:
            # prepare temporary cv2 image
            h, w, d = canvas.shape
            tmp = numpy.zeros((h, w, 3), dtype=numpy.uint8)
            #cv2.rectangle(tmp, b1, b2, color, thickness, linetype, shift)
            for i in range(len(bound.points)):
                pt1 = bound.points[i]
                pt2 = bound.points[i+1] if i < len(bound.points) -1 else bound.points[0]
                cv2.line(
                    tmp, pt1, pt2, color.get_gbr(), thickness, linetype, shift)

            # convert tmp into pil image for setting alpha
            pi = Image.fromarray(tmp)
            pi = pi.convert("RGBA")

            alphard = []
            for item in pi.getdata():
                if item[0] is 0 and item[1] is 0 and item[2] is 0:
                    alphard.append((item[0], item[1], item[2], 0))
                else:
                    alphard.append((item[0], item[1], item[2], color.a))
            pi.putdata(alphard)

            # finally, paste alpha image on pil canvas then convert into cv2
            # caution, PIL's size = (width, height) differ from
            # cv2's size (height, width)!!
            picanvas = Image.fromarray(canvas)
            picanvas.paste(pi, (0, 0), pi.split()[3])
            canvas = numpy.asarray(picanvas)[:, :, ::-1].copy()
            return canvas
        else:
            # simply, draw on canvas
            for i in range(len(bound.points)):
                pt1 = bound.points[i]
                pt2 = bound.points[i+1] if i < len(bound.points) -1 else bound.points[0]
                cv2.line(
                    canvas, pt1, pt2, color.get_gbr(), thickness, linetype, shift)
            return canvas

    def draw(self, image, bound, color):
        if self.outline:
            image = self.drawpoly(
                image, bound, self.outline_color, self.outline_thickness, 0)
        return self.drawpoly(image, bound, color, self.thickness, 2)

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
        cv2.imwrite(self.config["output"], image)

        return content


def draw(config, image, bound, color):
    r = Drawer(config, image)
    r.draw(bound, color)


def create(config, environ):
    return Drawer(config, environ)
