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
    center = property(doc='center of gravity of rect')
    area = property(doc='calc area')

    @top_left.getter
    def top_left(self):
        return (self.x, self.y)

    @bottom_right.getter
    def bottom_right(self):
        return (self.x + self.w, self.y + self.h)

    @center.getter
    def center(self):
        return (self.x + self.w / 2, self.y + self.h / 2)

    @area.getter
    def area(self):
        return self.w * self.h / 2.0

    def __init__(self, cvrect):
        self.x = cvrect[0]
        self.y = cvrect[1]
        self.w = cvrect[2]
        self.h = cvrect[3]

        # self.drawer = drawer.rectangle


class rotated_rect(region):

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


class circle(region):

    top_left = property(doc='top left point (x, y) of rect')
    bottom_right = property(doc='bottom right point(x, y) of rect')
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

    @area.getter
    def area(self):
        return self.radius * self.radius * math.pi


class ellipse(region):

    area = property(doc='calc area')

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
