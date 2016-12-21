""" coding: utf-8 """

# import logging
import copy

import cv2
import numpy as np

# import synopticgenerator.util as util
import synopticgenerator.shape as shape
# import synopticgenerator.mathutil as mathutil
from synopticgenerator import Pipeline


class Rearrange(Pipeline):
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

        # resolve collision
        self.arrange(self.config.get("arrangement", []))

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
        ctrls_direction_ = copy.copy(ctrls_direction)
        if not ctrls_direction:
            return

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

            self.solve_collision(target_row, b, target_row_bottom)
            target_row_bottom = max([(x.center[1] + (x.h / 2.0)) for x in b])

        self.solve_protrude(ctrls_direction_)

    def solve_collision(self, target_row, next_row, height, rule="align_center"):
        if not height:
            return

        # solve upper bound collision
        for ctrl in next_row:
            move_y = (ctrl.h / 2.0 + self.config.get('margin') + height) - ctrl.center[1]

            # round up
            move = shape.Vec2(0, move_y)
            move.y = 0.0 if move.y < 0 else move.y

            # determine direction
            move = ctrl.solve_direction_to_avoid(move, config=self.config)
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

        arrange_direction = self.config.get("arrange_direction")

        # align lower end
        for i, ctrl in enumerate(target_row):

            x = horizontal_baseline[i] - ctrl.center[0] if i < len(horizontal_baseline) else 0
            y = height - ctrl.bottom

            if 0 == i:
                ctrl.translate((x, y))

            target = target_row[i - 1]
            if 0 < i and x == 0:

                dist_x = ctrl.center[0] - target.center[0]

                if arrange_direction and "left" in arrange_direction:
                    if 0 < dist_x:
                        ctrl.translate((dist_x * -1, 0))

                elif arrange_direction and "right" in arrange_direction:
                    if dist_x < 0:
                        ctrl.translate((dist_x * -1, 0))

                protrude = target.calculate_infringement(ctrl, self.config)
                protrude = target.solve_direction_to_avoid(protrude, config=self.config)
                x = protrude[0]
                ctrl.translate((x, y))

            elif 0 < i:
                ctrl.translate((x, y))

    def solve_protrude(self, ctrls_direction):
        w = self.environ.get("width", 320)
        h = self.environ.get("height", 550)
        m = self.config.get("margin", 8)

        # left side
        # 1. select row that has maximum width in rows
        l = min([min(b.top_left[0] for b in a) for a in ctrls_direction])
        r = max([max(b.top_right[0] for b in a) for a in ctrls_direction])
        t = min([min(b.top_left[1] for b in a) for a in ctrls_direction])
        b = max([max(b.bottom_right[1] for b in a) for a in ctrls_direction])

        # 2. whether if that row protrude our canvas background
        x = 0
        y = 0

        if l < m:
            x = (l - m) * -1

        if (w - m) < r:
            x = (r - (w - m)) * -1

        if b < m:
            y = (b - m) * -1

        if (h - m) < t:
            y = (t - (h - m)) * -1

        # 3. if protrude, translate rows
        for row in ctrls_direction:
            for ctrl in row:
                ctrl.translate((x, y))


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return Rearrange(config, environ)
