""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.

# import enum
import cv2
import numpy
import math

import synopticgenerator.util as util
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi@gmail.com"
__status__ = "Prototype"
__all__ = ["Shape"]
##############################################################################


# RegionType = enum.Enum("rect", "poly", "circle")
# LocationType = enum.Enum("center", "left", "right")


class Shape(object):
    name = ""
    region_type = None
    color = None
    radius = None
    location = None  # LocationType
    # cog = None


class Rect(Shape):
    x = 0
    y = 0
    w = 0
    h = 0

    top_left = property(doc='top left point (x, y) of rect')
    top_right = property(doc='top right point (x, y) of rect')
    bottom_left = property(doc='bottom left point(x, y) of rect')
    bottom_right = property(doc='bottom right point(x, y) of rect')
    bottom = property(doc='bottom point(y) of rect')
    center = property(doc='center of gravity of rect')
    area = property(doc='calc area')
    points = property(doc='corner points')

    def __init__(self, cvrect):
        self.x = cvrect[0]
        self.y = cvrect[1]
        self.w = cvrect[2]
        self.h = cvrect[3]

    @top_left.getter
    def top_left(self):
        return map(int, (self.x, self.y))

    @top_right.getter
    def top_right(self):
        return map(int, (self.x + self.w, self.y))

    @bottom_left.getter
    def bottom_left(self):
        return map(int, (self.x, self.y + self.h))

    @bottom_right.getter
    def bottom_right(self):
        return map(int, (self.x + self.w, self.y + self.h))

    @center.getter
    def center(self):
        return map(int, (self.x + self.w / 2, self.y + self.h / 2))

    @bottom.getter
    def bottom(self):
        return self.center[1] + (self.h / 2.)

    @area.getter
    def area(self):
        return self.w * self.h / 2.0

    @points.getter
    def points(self):
        return (self.top_left, self.top_right, self.bottom_right, self.bottom_left)

    def scale(self, ratio):
        c = self.center
        self.w, self.h = map(lambda x: int(x * ratio), [self.w, self.h])
        self.x = int(c[0] - (self.w / 2.0))
        self.y = int(c[1] - (self.h / 2.0))

    def scale_x(self, ratio):
        c = self.center
        self.w = int(self.w * ratio)
        self.x = int(c[0] - (self.w / 2.0))

    def scale_y(self, ratio):
        c = self.center
        self.h = int(self.h * ratio)
        self.y = int(c[1] - (self.h / 2.0))

    def translate(self, xy):
        self.x += int(xy[0])
        self.y += int(xy[1])

    def scatter_points(self, seed):

        # divide rect into two triangles and scatter points on each surface
        if numpy.random.rand(1) < 0.5:
            triangle = (self.top_left, self.top_right, self.bottom_left)

        else:
            triangle = (self.top_right, self.bottom_left, self.bottom_right)

        return uniform_on_triangle(triangle, seed)


class RotatedRect(Rect):

    x = 0
    y = 0
    w = 0
    h = 0
    theta = 0
    points = []

    center = property(doc='center of gravity of rect')
    area = property(doc='calc area')

    def __init__(self, cvrotatedrect):
        self.x = cvrotatedrect[0][0]
        self.y = cvrotatedrect[0][1]
        self.w = cvrotatedrect[1][0]
        self.h = cvrotatedrect[1][1]
        self.theta = cvrotatedrect[2]

        if util.is_opencv_version_below_2():
            p = cv2.cv.BoxPoints(cvrotatedrect)
        else:
            p = cv2.boxPoints(cvrotatedrect)
        p = numpy.int0(p)
        self.points = [(x[0], x[1]) for x in p]
        # self.drawer = drawer.polygon
        # print self.points

    @center.getter
    def center(self):
        x = 0
        y = 0
        for p in self.points:
            x += p[0]
            y += p[1]

        return (x / len(self.points), y / len(self.points))

    @area.getter
    def area(self):
        return self.w * self.h / 2.0

    def scale(self, ratio):
        c = self.center
        self.w, self.h = map(lambda x: int(x * ratio), [self.w, self.h])
        self.x = int(c[0] - (self.w / 2.0))
        self.y = int(c[1] - (self.h / 2.0))


class Circle(Shape):

    top_left = property(doc='top left point (x, y) of rect')
    bottom_right = property(doc='bottom right point(x, y) of rect')
    bottom = property(doc='bottom point(y) of circle')
    area = property(doc='calc area')

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    @top_left.getter
    def top_left(self):
        return map(lambda x: x - self.radius, self.center)

    @bottom_right.getter
    def bottom_right(self):
        return map(lambda x: x + self.radius, self.center)

    @bottom.getter
    def bottom(self):
        return self.center[1] + self.radius

    @area.getter
    def area(self):
        return self.radius * self.radius * math.pi

    def scale(self, ratio):
        self.radius *= math.sqrt(ratio)

    def translate(self, xy):
        self.center[0] += int(xy[0])
        self.center[1] += int(xy[1])

    def scatter_points(self, seed):
        # TODO:
        return self.center


class Ellipse(Shape):

    area = property(doc='calc area')
    bottom = property(doc='bottom point(y) of ellipse')

    # def __init__(self, center, radius):
    def __init__(self, cvrotated):
        self.cvrotated = cvrotated
        self.x = cvrotated[0][0]
        self.y = cvrotated[0][1]
        self.w = cvrotated[1][0]
        self.h = cvrotated[1][1]
        self.theta = cvrotated[2]
        self.center = cvrotated[0]

    @area.getter
    def area(self):
        return self.w / 2 * self.h / 2 * math.pi

    def scale(self, ratio):
        self.w *= math.sqrt(ratio)
        self.h *= math.sqrt(ratio)

    @bottom.getter
    def bottom(self):
        return self.center[1] + (self.h / 2.)

    def translate(self, xy):
        self.x += int(xy[0])
        self.y += int(xy[1])

    def scatter_points(self, seed):
        # TODO:
        return self.center


def uniform_on_triangle(triangle, seed):
    numpy.random.seed(seed=seed)
    eps1, eps2 = numpy.random.rand(2)

    sqrt_r1 = math.sqrt(eps1)

    px = (
        (1.0 - sqrt_r1) * triangle[0][0]
        + sqrt_r1 * (1.0 - eps2) * triangle[1][0]
        + sqrt_r1 * eps2 * triangle[2][0]
    )

    py = (
        (1.0 - sqrt_r1) * triangle[0][1]
        + sqrt_r1 * (1.0 - eps2) * triangle[1][1]
        + sqrt_r1 * eps2 * triangle[2][1]
    )

    return (px, py)
