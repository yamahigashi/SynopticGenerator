""" coding: utf-8 """

import copy
import bisect
import logging

import cv2
import numpy as np

import synopticgenerator.util as util
import synopticgenerator.shape as shape
import synopticgenerator.mathutil as mathutil
from synopticgenerator.plugins import Pipeline


class RealignmentPosition(Pipeline):
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

        if self.config.get("inflate", False):
            inflated_points, inflated_indice = self.uniform_distribution(inflated, 500)
            pointcloud_list = np.array(inflated_points, np.float32)
            pointcloud_list = np.r_[pointcloud_list, cog_points_list]  # guarantee 1 point per 1 ctrl
            inflated_indice.extend([x for x in range(len(cog_points_list))])
            pointcloud_list /= self.aspect_ratio_normalizer

        else:
            pointcloud_list = np.array(cog_points_list, np.float32)
            pointcloud_list /= self.aspect_ratio_normalizer
            inflated_indice = [i for i in range(len(pointcloud_list))]

        # calculate x-means
        # x_means = mathutil.XMeansCV2().fit(pointcloud_list)
        x_means = mathutil.XMeans(random_state=1).fit(pointcloud_list)
        pointcloud_list *= self.aspect_ratio_normalizer

        # resolve collision
        for i, cluster in enumerate(x_means.clusters):
            cluster.data *= [self.aspect_ratio_normalizer, self.aspect_ratio_normalizer]
            cluster.center *= [self.aspect_ratio_normalizer, self.aspect_ratio_normalizer]
            indice = np.unique(np.array(inflated_indice)[cluster.index])
            targets = np.array(ctrls)[indice]
            self.alignment_in_cluster(cluster, targets, use_cluster_for_aspectratio=False)

        cog_points_list = np.array([x.center for x in ctrls], np.float32)
        x_means2 = mathutil.XMeans(random_state=1).fit(cog_points_list)
        for i, cluster in enumerate(x_means2.clusters):
            targets = np.array(ctrls)[cluster.index]
            self.alignment_in_cluster(cluster, targets)

        if self.config.get('draw_debug', True):
            self.draw_debug(pointcloud_list, x_means.labels)
            self.draw_debug(cog_points_list, x_means2.labels)

        return content

    def alignment_in_cluster(self, cluster, ctrls, use_cluster_for_aspectratio=True):
        if not 1 < len(ctrls):
            return

        if use_cluster_for_aspectratio:
            x = np.std(cluster.data[0:, 0])
            y = np.std(cluster.data[0:, 1])

        else:
            xarray = sorted([ctrl.center[0] for ctrl in ctrls])
            yarray = sorted([ctrl.center[1] for ctrl in ctrls])
            x = xarray[-1] - xarray[0]
            y = yarray[-1] - yarray[0]

        if x < y:
            is_vertical_longer = True
            try:
                ratio = y / x
            except ZeroDivisionError:
                ratio = y
        else:
            is_vertical_longer = False
            try:
                ratio = x / y
            except ZeroDivisionError:
                ratio = x

        if self.ratio_over_unbalance < ratio:
            if is_vertical_longer:
                print("\nvertical", ratio, x, y)
                self.align_horizontal(cluster, ctrls)

            else:
                print("\nhorizontal", ratio, x, y)
                self.align_vertical(cluster, ctrls)

        elif ratio < self.ratio_very_circle:
            print("circle", ratio, x, y)

        else:
            print("\nnone of them", ratio, x, y)
            if util.is_point_inside_central_region(self.environ, shape.Vec2(*cluster.center)):
                print("is in center")
                cluster.center[0] = util.get_x_center(self.environ)
                self.align_horizontal(cluster, ctrls, exclusive_location="center")

            if util.is_point_inside_lower_region(self.environ, shape.Vec2(*cluster.center)):
                print("is in lower")
                self.align_vertical_by_bottom(cluster, ctrls)
            # _x = np.array([x.center[0] for x in targets], np.float32)
            # k_means_about_x = mathutil.XMeans(random_state=1).fit(_x)

            '''
            compactness, labels, centers = cv2.kmeans(
                data=_x, K=3, bestLabels=None,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10),
                attempts=1, flags=cv2.KMEANS_RANDOM_CENTERS)
            print(labels)
            '''

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

            color = list(map(lambda x: x, (b, g, r)))

            cv2.circle(blank_image_classified, (int(point[0]), int(point[1])), 1, color, 2)

        # cv2.imshow("Points", blank_image)
        cv2.imshow("Points Classified", blank_image_classified)
        cv2.waitKey()

    def align_horizontal(self, cluster, targets, exclusive_location=None):
        for ctrl in targets:
            if exclusive_location and ctrl.location != exclusive_location:
                continue
            _x = cluster.center[0] - ctrl.center[0]
            print(ctrl.name, _x, cluster.center, ctrl.center)
            ctrl.translate((_x, 0))

    # def align_horizontal_by_center(self, cluster, targets):
    #     for ctrl in targets:
    #         print(ctrl.name)

    def align_vertical(self, cluster, targets):
        # if it is in the lower area, align it downward or align it centeroid
        h = self.environ.get("height", 10) * (1.0 - self.ratio_lower_end_region)
        if cluster.center[1] < h:
            self.align_vertical_by_center(cluster, targets)
        else:
            self.align_vertical_by_bottom(cluster, targets)

    def align_vertical_by_center(self, cluster, targets):
        for ctrl in targets:
            _y = cluster.center[1] - ctrl.center[1]
            ctrl.translate((0, _y))
            print("by center", ctrl.name)

    def align_vertical_by_bottom(self, cluster, targets):
        y_mean = np.mean(np.array([x.bottom for x in targets]))
        for ctrl in targets:
            _y = y_mean - ctrl.bottom
            ctrl.translate((0, _y))
            print("by bottom", ctrl.name)

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


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return RealignmentPosition(config, environ)
