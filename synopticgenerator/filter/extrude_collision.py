""" coding: utf-8 """

import copy
import bisect
# import logging

import cv2
import numpy as np

import synopticgenerator.util as util
import synopticgenerator.shape as shape
import synopticgenerator.mathutil as mathutil
import synopticgenerator.filter.rearrange as rearrange
from synopticgenerator import Pipeline


class ExtrudeCollision(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)
        self.margin = config.setdefault("margin", 8)

        self.aspect_ratio_baseline_for_conflict = config.setdefault(
            "aspect_ratio_baseline_for_conflict", 0.25)

        self.ratio_over_unbalance = 4.0
        self.ratio_very_circle = 1.5
        self.ratio_lower_end_region = 0.25

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        ctrls = content[self.region]
        w = self.environ.get("width", 320)
        h = self.environ.get("height", 550)

        if w < h:
            self.aspect_ratio_normalizer = h
        else:
            self.aspect_ratio_normalizer = w

        # gather cog points
        cog_points_list = np.array([x.center for x in ctrls], np.float32)

        # inflate ctrls
        inflated = copy.deepcopy(ctrls)
        map(lambda x: x.scale(1.2), inflated)

        inflated_points, inflated_indice = self.uniform_distribution(inflated, 1)
        pointcloud_list = np.array(inflated_points, np.float32)
        pointcloud_list = np.r_[pointcloud_list, cog_points_list]  # guarantee 1 point per 1 ctrl
        inflated_indice.extend([x for x in range(len(cog_points_list))])
        pointcloud_list /= self.aspect_ratio_normalizer

        # calculate x-means
        # x_means = mathutil.XMeansCV2().fit(pointcloud_list)
        x_means = mathutil.XMeans(random_state=1).fit(pointcloud_list)
        pointcloud_list *= self.aspect_ratio_normalizer

        print len(x_means.clusters)

        # resolve collision
        for i, cluster in enumerate(x_means.clusters):

            cluster.data *= [self.aspect_ratio_normalizer, self.aspect_ratio_normalizer]
            cluster.center *= [self.aspect_ratio_normalizer, self.aspect_ratio_normalizer]
            indice = np.unique(np.array(inflated_indice)[cluster.index])
            targets = np.array(ctrls)[indice]

            content = self.analyze_cluster(content, cluster, targets)

            self.resolve_collision(targets)

        if self.config.get('draw_debug', False):
            self.draw_debug(pointcloud_list, x_means.labels)

        return content

    def analyze_cluster(self, content, cluster, targets):
        x_min = cluster.data.min(axis=0)[0]
        x_max = cluster.data.max(axis=0)[0]
        y_min = cluster.data.min(axis=0)[1]
        y_max = cluster.data.max(axis=0)[1]
        print x_min, x_max, y_min, y_max
        print cluster.center
        print [x.name for x in targets]
        print util.is_point_inside_central_region(self.environ, shape.Vec2(*cluster.center))
        sorted_by_y = sorted(targets, key=lambda x: x.center[1])

        if util.is_point_inside_central_region(self.environ, shape.Vec2(*cluster.center)):
            config = {
                "arrangement": [],
                "arrange_direction": "down"
            }

            for ctrl in sorted_by_y:
                if ctrl.location == "center" and util.is_point_inside_central_region(self.environ, shape.Vec2(*ctrl.center)):
                    config["arrangement"].append([ctrl.name])

            print config
            sub_module = rearrange.create(config, self.environ)
            content = sub_module.execute(content)

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

    def uniform_distribution(self, ctrls, point_count):

        # 面積に応じてscatter, まずは累積面積のリスト作る
        sum_area = 0.0
        cumulative_areas = []
        for x in ctrls:
            sum_area += x.area
            cumulative_areas.append(sum_area)

        def _choose(areas, end, i):
            p = np.random.uniform(0.0, sum_area)
            selected_index = bisect.bisect_left(areas, p)

            return selected_index

        points = []
        indice = []
        for i in range(point_count):
            index = _choose(cumulative_areas, sum_area, i)
            points.append(ctrls[index].scatter_points(i))
            indice.append(index)

        return points, indice

    def resolve_collision(self, ctrls):
        """
        Args:
            ctrls(np.array)
        """
        all = sorted(ctrls, key=lambda x: x.area)
        while all:
            target = all.pop()
            for b in all:
                protrude = b.calculate_infringement(target, config=self.config)
                protrude = b.solve_direction_to_avoid(protrude, other=target, config=self.config)

                b.translate(protrude)


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return ExtrudeCollision(config, environ)
