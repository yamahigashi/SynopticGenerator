""" coding: utf-8 """

import math


import synopticgenerator.region as region


class RotatedrectToRect(object):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        news = []
        for i, shape in enumerate(content[self.region]):
            if type(shape) == region.rotated_rect:
                news.append([i, self.convert(shape)])

        for to_replace in news:
            content[self.region][to_replace[0]] = to_replace[1]

        return content

    def convert(self, shape):
        c = shape.center
        cos = math.cos
        sin = math.sin

        if (90 - abs(shape.theta) < abs(shape.theta)):
            theta = math.radians(shape.theta * -1 + 90)
        else:
            theta = math.radians(shape.theta * -1)
        old_cog = shape.center

        def rotate(points, theta):
            ''' cancel rotation and treat as normal rect'''

            # the rotate matrix:
            #   cos(theta), -sin(theta)
            #   sin(theta),  cos(theta)

            x = (points[0] * cos(theta)) + (-1 * sin(theta) * points[1])
            y = (points[0] * sin(theta)) + (cos(theta) * points[1])

            return int(round(x)), int(round(y))

        diff = map(lambda x: (x[0] - c[0], x[1] - c[1]), shape.points)
        rot = map(lambda x: rotate(x, theta), diff)
        new = map(lambda x: (x[0] + c[0], x[1] + c[1]), rot)

        x = new[0][0]
        y = new[0][1]

        w = abs(rot[0][0]) * 2
        h = abs(rot[0][1]) * 2

        new_rect = region.rect([x, y, w, h])
        new_rect.name = shape.name
        new_rect.color = shape.color
        new_rect.radius = shape.radius
        new_rect.location = shape.location
        new_cog = new_rect.center
        # match_position by old centeroid
        new_rect.translate((old_cog[0] - new_cog[0], old_cog[1] - new_cog[1]))

        # self.draw_debug(new_rect.points, (1, 0, 0))
        return new_rect

    def draw_debug(self, points_input, color):
        import cv2
        import numpy as np
        # draw debug
        blank_image = np.zeros((800, 800, 3))

        for point in points_input:
            cv2.circle(blank_image, (int(point[0]), int(point[1])), 1, (0, 255, 0), -1)

        for point in points_input:
            _color = map(lambda x: int(x * 255), color)

            cv2.circle(blank_image, (int(point[0]), int(point[1])), 3, _color, -1)

        cv2.imshow("Points", blank_image)
        cv2.waitKey()


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return RotatedrectToRect(config, environ)
