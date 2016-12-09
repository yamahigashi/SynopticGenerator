""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.

# import enum
import cv2
import numpy
import math

# import synopticcreater.drawer as drawer
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi@gmail.com"
__status__ = "Prototype"
__all__ = ["region"]
##############################################################################


# RegionType = enum.Enum("rect", "poly", "circle")
# LocationType = enum.Enum("center", "left", "right")


class region(object):
    name = ""
    region_type = None
    color = None
    radius = None
    location = None  # LocationType
    # cog = None


class rect(region):
    x = 0
    y = 0
    w = 0
    h = 0

    top_left = property(doc='top left point (x, y) of rect')
    bottom_right = property(doc='bottom right point(x, y) of rect')
    bottom = property(doc='bottom point(y) of rect')
    center = property(doc='center of gravity of rect')
    area = property(doc='calc area')

    def __init__(self, cvrect):
        self.x = cvrect[0]
        self.y = cvrect[1]
        self.w = cvrect[2]
        self.h = cvrect[3]

    @top_left.getter
    def top_left(self):
        return map(int, (self.x, self.y))

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

    def scale(self, ratio):
        c = self.center
        self.w, self.h = map(lambda x: int(x * ratio), [self.w, self.h])
        self.x = int(c[0] - (self.w / 2.0))
        self.y = int(c[1] - (self.h / 2.0))

    def translate(self, xy):
        self.x += int(xy[0])
        self.y += int(xy[1])


class rotated_rect(rect):

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

        p = cv2.cv.BoxPoints(cvrotatedrect)
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


class circle(region):

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


class ellipse(region):

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
