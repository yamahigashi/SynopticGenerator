""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.

# import enum
import cv2
import numpy
import math
import logging

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

    def calculate_infringement(self, other, config={}):
        pa = Vec2(*other.center)
        pb = Vec2(*self.center)
        dist = pa - pb

        move_x = ((other.w + self.w) / 2.0 + config.get('margin', 0)) - abs(dist.x)
        move_y = ((other.h + self.h) / 2.0 + config.get('margin', 0)) - abs(dist.y)

        if 0 < move_x and 0 < move_y:
            mes = ("infringement detect at {}({}) with {}({})".format(
                other.name, other.area, self.name, self.area))
            logging.debug(mes)
        else:
            return (0, 0)

        if dist.x < 0:
            move_x *= -1
        if dist.y < 0:
            move_y *= -1

        move = Vec2(move_x, move_y)
        return move

    def avoid_collision(self, other, config={}):
        move = self.calculate_infringement(other, config)

        # round up
        move.x = 0.0 if move.x < 0 else move.x
        move.y = 0.0 if move.y < 0 else move.y

        # determine direction
        move = self.solve_direction_to_avoid(other, move, config) * -1
        self.translate(move)

    def solve_direction_to_avoid(self, move, other=None, config={}):
        solver = CollisionSolverChooser.choose(config)
        move = solver.solve(config, self, move, other)
        return move

    def which_direction_to_avoid_by_config(self, config={}):
        direction = config.get('arrange_direction')
        horizontal = None
        vertical = None
        for candidate in ["left", "right", "horizontal"]:
            if candidate in direction:
                horizontal = candidate
                break

        for candidate in ["down", "up", "vertical"]:
            if candidate in direction:
                vertical = candidate
                break

        if not horizontal and vertical:
            msg = "arrange_direction's value not match any candidate"
            msg += """ in ["left", "right", "down", "up", "horizontal", "vertical"]"""
            logging.error(msg)

        return horizontal, vertical

    def which_direction_to_avoid_by_aspect_ratio(self, ratio, config={}):
        base = config.get('aspect_ratio_baseline_for_conflict')
        rev_base = 1.0 / base

        if rev_base < ratio:
            return "vertical"

        elif ratio < base:
            return "horizontal"

        else:
            return None

    def which_direction_to_avoid_by_location_attribute(self, other, config={}):
        if (
                isinstance(other.location, LocationAttributeCenter) and
                isinstance(self.location, LocationAttributeCenter)):

            res = LocationAttributeCenter

        elif (
                isinstance(other.location, LocationAttributeCenter) and
                not isinstance(self.location, LocationAttributeCenter)):

            res = self.location

        elif (
                not isinstance(other.location, LocationAttributeCenter) and
                isinstance(self.location, LocationAttributeCenter)):

            res = LocationAttributeCenter

        elif (
                not isinstance(other.location, LocationAttributeCenter) and
                not isinstance(self.location, LocationAttributeCenter)):

            if other.location == self.location:
                res = other.location
            else:
                res = self.location

        else:
            res = LocationAttributeCenter

        if not res:
            res = LocationAttributeCenter

        return res


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

    def copy_mirror(self, env, name, x_axis=None):
        if not x_axis:
            x_axis = util.get_x_center(env)

        new_center = x_axis + (x_axis - self.center.x)
        new_x = new_center - self.w
        new_shape = Rect((new_x, self.y, self.w, self.h))
        new_shape.name = name
        if self.location:
            new_shape.location = self.location.mirror()
        return new_shape

    @top_left.getter
    def top_left(self):
        return Vec2.from_map(map(int, (self.x, self.y)))

    @top_right.getter
    def top_right(self):
        return Vec2.from_map(map(int, (self.x + self.w, self.y)))

    @bottom_left.getter
    def bottom_left(self):
        return Vec2.from_map(map(int, (self.x, self.y + self.h)))

    @bottom_right.getter
    def bottom_right(self):
        return Vec2.from_map(map(int, (self.x + self.w, self.y + self.h)))

    @center.getter
    def center(self):
        return Vec2.from_map(map(int, (self.x + self.w / 2, self.y + self.h / 2)))

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
        self.w, self.h = list(map(lambda x: int(x * ratio), [self.w, self.h]))
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

    def copy_mirror(self, env, name, x_axis=None):
        if not x_axis:
            x_axis = util.get_x_center(env)

        new_center = x_axis + (x_axis - self.center.x)
        new_x = new_center - self.w
        new_theta = self.theta * -1
        cvrotatedrect = [
            [new_x, self.y],
            [self.w, self.h],
            new_theta
        ]
        new_shape = RotatedRect(cvrotatedrect)
        new_shape.name = name
        if self.location:
            new_shape.location = self.location.mirror()
        return new_shape

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
        self.w, self.h = list(map(lambda x: int(x * ratio), [self.w, self.h]))
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

    def copy_mirror(self, env, name, x_axis=None):
        if not x_axis:
            x_axis = util.get_x_center(env)

        new_center = x_axis + (x_axis - self.center.x)
        new_shape = Circle(new_center, self.radius)
        new_shape.name = name
        if self.location:
            new_shape.location = self.location.mirror()
        return new_shape

    @top_left.getter
    def top_left(self):
        return Vec2.from_map(map(lambda x: x - self.radius, self.center))

    @bottom_right.getter
    def bottom_right(self):
        return Vec2.from_map(map(lambda x: x + self.radius, self.center))

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

    def copy_mirror(self, env, name, x_axis=None):
        if not x_axis:
            x_axis = util.get_x_center(env)

        new_center = x_axis + (x_axis - self.center.x)
        new_x = new_center - self.w
        new_theta = self.theta * -1
        cvrotatedrect = [
            [new_x, self.y],
            [self.w, self.h],
            new_theta
        ]
        new_shape = Ellipse(cvrotatedrect)
        new_shape.name = name
        if self.location:
            new_shape.location = self.location.mirror()
        return new_shape

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


class CollisionSolverChooser(object):
    """ Base class of base collision solver """

    @staticmethod
    def choose(config):
        for solver in [
            ConfigBaseCollisionSolver,
            AspectRatioBaseCollisionSolver,
            AttributeBaseCollisionSolver
        ]:

            if solver.match_rule(config):
                logging.debug("CollisionSolverChooser.choose result {}".format(solver))
                return solver()

        else:
            raise "error CollisionSolver class not ound"


# --------------------------------------------------------------------------- #
#
# --------------------------------------------------------------------------- #
class BaseCollisionSolver(object):
    """ Base class of base collision solver """

    def solve(self, config, shape, move, other=None):
        if not isinstance(move, Vec2):
            move = Vec2(move[0], move[1])

        return self.solve_direction(config, shape, move, other)


class ConfigBaseCollisionSolver(BaseCollisionSolver):

    @staticmethod
    def match_rule(config):
        return config.get('arrange_direction', False)

    def solve_direction(self, config, shape, move, othel=None):
        horizontal, vertical = shape.which_direction_to_avoid_by_config(config)

        # -------------------------------------------
        if horizontal and horizontal == "left":
            move.x = abs(move.x) * -1
        elif horizontal and horizontal == "right":
            move.x = abs(move.x)

        if horizontal and not vertical:
            move.y = 0

        # -------------------------------------------
        if vertical and vertical == "up":
            move.y = abs(move.y) * -1
        elif vertical and vertical == "down":
            move.y = abs(move.y)

        if vertical and not horizontal:
            move.x = 0

        return move


class AspectRatioBaseCollisionSolver(BaseCollisionSolver):

    @staticmethod
    def match_rule(config):
        return config.get('aspect_ratio_baseline_for_conflict', False)

    def get_fallback(self):
        return AttributeBaseCollisionSolver()
        # return ConfigBaseCollisionSolver()

    def solve_direction(self, config, shape, move, other=None):
        if move[0] == 0 and move[1] == 0:
            aspect = 1

        elif move[0] == 0:
            aspect = 0

        elif move[1] == 0:
            aspect = move[0]

        else:
            aspect = shape.which_direction_to_avoid_by_aspect_ratio(abs(move[0]) / abs(move[1]), config)

        if aspect and aspect == "horizontal":
            move.y = 0

        elif aspect and aspect == "vertical":
            move.x = 0

        else:
            # Fall back
            if other:
                horizontal = ""
                vertical = ""
                dist = Vec2(other.center[0] - shape.center[0], other.center[1] - shape.center[1])
                if dist[0] < 0:
                    horizontal = "left"
                else:
                    horizontal = "right"

                if dist[1] < 0:
                    vertical = "down"
                else:
                    vertical = "up"

                arrange_direction = config.get("arrange_direction")
                if arrange_direction:
                    delete_later = False
                else:
                    delete_later = True
                    config.setdefault("arrange_direction", "{},{}".format(horizontal, vertical))

            move = self.get_fallback().solve_direction(config, shape, move, other)

            if delete_later:
                del config["arrange_direction"]

        return move


class AttributeBaseCollisionSolver(BaseCollisionSolver):

    @staticmethod
    def match_rule(config):
        return True

    def solve_direction(self, config, shape, move, other=None):
        direction = shape.which_direction_to_avoid_by_location_attribute(other, config)
        if direction == LocationAttributeCenter:
            move.x = 0

        elif direction == LocationAttributeLeft:
            move.x = abs(move.x) * -1
            move.y = 0

        elif direction == LocationAttributeRight:
            move.x = abs(move.x)
            move.y = 0

        return move


# --------------------------------------------------------------------------- #
#
# --------------------------------------------------------------------------- #
class LocationAttribute(object):

    label = None

    def __str__(self):
        return self.label

    def __eq__(self, other):
        if isinstance(other, type):
            return type(self) == other

        return type(self) == type(other)

    def __nq__(self, other):
        return not self.__eq__(other)


class LocationAttributeCenter(LocationAttribute):

    label = "center"

    def mirror(self):
        return LocationAttributeCenter()


class LocationAttributeLeft(LocationAttribute):

    label = "left"

    def mirror(self):
        return LocationAttributeRight()


class LocationAttributeRight(LocationAttribute):

    label = "right"

    def mirror(self):
        return LocationAttributeLeft()


# --------------------------------------------------------------------------- #
#
# --------------------------------------------------------------------------- #
class Vec2(list):

    x = property()
    y = property()

    def __init__(self, x, y):
        super(Vec2, self).__init__()
        self.append(x)
        self.append(y)

    @staticmethod
    def from_map(map):
        l_ = list(map)
        x = l_[0]
        y = l_[1]
        return Vec2(x, y)

    @x.getter
    def x(self):
        return self[0]

    @y.getter
    def y(self):
        return self[1]

    @x.setter
    def x(self, value):
        self[0] = value

    @y.setter
    def y(self, value):
        self[1] = value

    # ----------------------------------------------------
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    # ----------------------------------------------------
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    # ----------------------------------------------------
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    # ----------------------------------------------------
    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
        else:
            return Vec2(self.x * other, self.y * other)

    def __imul__(self, other):
        if isinstance(other, Vec2):
            self.x *= other.x
            self.y *= other.y
            return self
        else:
            self.x *= other
            self.y *= other
            return self

    # ----------------------------------------------------
    def __div__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x / other.x, self.y / other.y)
        else:
            return Vec2(self.x / other, self.y / other)

    def __truediv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x / other.x, self.y / other.y)
        else:
            return Vec2(self.x / other, self.y / other)

    def __idiv__(self, other):
        if isinstance(other, Vec2):
            self.x /= other.x
            self.y /= other.y
            return self
        else:
            self.x /= other
            self.y /= other
            return self
