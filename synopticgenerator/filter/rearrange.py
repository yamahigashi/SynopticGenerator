""" coding: utf-8 """

import copy
import bisect
import logging

import cv2
import numpy as np

# import synopticgenerator.util as util
import synopticgenerator.shape as shape
import synopticgenerator.mathutil as mathutil


class Rearrange(object):
    ''' clustering given ctrl as cog points by k-means. '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.margin = config.setdefault("margin", 8)
        # self.arrangement = config.setdefault("arrangement", [])

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        self.ctrls = content[self.region]
        w = self.environ.get("width", 320)
        h = self.environ.get("height", 550)

        # gather cog points
        cog_points_list = np.array([x.center for x in self.ctrls], np.float32)

        # resolve collision
        self.arrange(self.config.get("arrangement"))

        return content

    def draw_debug(self, points_input, classified_points):
        import random

        # draw debug
        blank_image = np.zeros((800, 800, 3))
        blank_image_classified = np.zeros((800, 800, 3))

        for point in points_input:
            cv2.circle(blank_image, (int(point[0]), int(point[1])), 1, (0, 255, 0), -1)

        max_allocation = max(classified_points)
        for point, allocation in zip(points_input, classified_points):

            random.seed(allocation)
            r = random.random()
            g = 0.0
            random.seed(max_allocation - allocation)
            b = random.random()

            color = map(lambda x: x, (b, g, r))

            cv2.circle(blank_image_classified, (int(point[0]), int(point[1])), 1, color, 2)

        # cv2.imshow("Points", blank_image)
        cv2.imshow("Points Classified", blank_image_classified)
        cv2.waitKey()

    def arrange(self, arrange_direction):
        # arrange_direction.reverse()
        ctrls_direction = []
        for i, arr in enumerate(arrange_direction):
            tmp = []
            for j, a in enumerate(arr):
                tmp.append([x for x in self.ctrls if x.name == arrange_direction[i][j]][0])

            ctrls_direction.append(tmp)
        ctrls_direction.reverse()

        target_row_bottom = None
        horizontal_baseline = None
        while ctrls_direction:
            target_row = ctrls_direction.pop()

            self.arrange_horizon(target_row, target_row_bottom, horizontal_baseline)
            target_row_bottom = max([(x.center[1] + (x.h / 2.0)) for x in target_row])
            horizontal_baseline = [x.center[0] for x in target_row]

            try:
                b = ctrls_direction[-1]
            except IndexError:
                break
            self.solve_collision(b, target_row_bottom)
            target_row_bottom = max([(x.center[1] + (x.h / 2.0)) for x in b])

    def solve_collision(self, target_row, height, rule="align_center"):
        if not height:
            return

        # solve upper bound collision
        for ctrl in target_row:
            move_y = (ctrl.h / 2.0 + self.config.get('margin') + height) - ctrl.center[1]

            # round up
            move = shape.Vec2(0, move_y)
            move.y = 0.0 if move.y < 0 else move.y

            # determine direction
            # move = self.solve_direction_to_avoid(a, ctcrl, move) * -1
            ctrl.translate(move)

    def arrange_horizon(self, target_row, height, horizontal_baseline=[], rule="align_center"):
        """
        Args:
            target_row(list): target row controllers
            height(float):  align base
            rule(str): "align_bottom", "align_center"
        """
        if not height:
            bottoms = max([(x.center[1] + (x.h / 2.0)) for x in target_row])
            return bottoms

        # align lower end
        for i, ctrl in enumerate(target_row):
            x = horizontal_baseline[i] - ctrl.center[0] if i < len(horizontal_baseline) else 0
            if 0 < i and x == 0:
                x = self.resolve_collision_a_b(target_row[i], target_row[i - 1])[0]

            y = height - ctrl.bottom
            ctrl.translate((x, y))

    def resolve_collision_a_b(self, a, b):
        pa = shape.Vec2(*a.center)
        pb = shape.Vec2(*b.center)
        dist = pa - pb

        move_x = ((a.w + b.w) / 2.0 + self.config.get('margin')) - dist.x
        move_y = ((a.h + b.h) / 2.0 + self.config.get('margin')) - dist.y

        if 0 < move_x and 0 < move_y:
            mes = ("infringement detect at {}({}) with {}({})".format(
                a.name, a.area, b.name, b.area))
            logging.debug(mes)
        else:
            return (0, 0)

        # round up
        move = shape.Vec2(move_x, move_y)
        move.x = 0.0 if move.x < 0 else move.x
        move.y = 0.0 if move.y < 0 else move.y

        # determine direction
        return move

    def solve_direction_to_avoid(self, a, b, move):
        aspect = self.which_direction_to_avoid_by_aspect_ratio(move.x / move.y)

        if aspect and aspect == "horizontal":
            move.y = 0

        elif aspect and aspect == "vertical":
            move.x = 0

        else:
            direction = self.which_direction_to_avoid_by_location_attribute(a, b)
            if direction == "center":
                move.x = 0

            elif direction == "left":
                move.x = abs(move.x) * -1
                move.y = 0

            elif direction == "right":
                move.x = abs(move.x)
                move.y = 0

        # TODO: avoid protrude out from background

        return move

    def which_direction_to_avoid_by_aspect_ratio(self, ratio):
        base = self.config.get('aspect_ratio_baseline_for_conflict')
        rev_base = 1.0 / base

        if rev_base < ratio:
            return "vertical"

        elif ratio < base:
            return "horizontal"

        else:
            return None

    def which_direction_to_avoid_by_location_attribute(self, a, b):
        if a.location == 'center' and b.location == "center":
            res = "center"

        elif a.location == "center" and b.location != "center":
            res = b.location

        elif a.location != "center" and b.location == "center":
            res = "center"

        elif a.location != "center" and b.location != "center":
            if a.location == b.location:
                res = a.location
            else:
                res = b.location

        else:
            res = "center"

        if not res:
            res = "center"

        return res


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return Rearrange(config, environ)
