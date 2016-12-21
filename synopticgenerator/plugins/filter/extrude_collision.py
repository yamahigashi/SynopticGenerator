""" coding: utf-8 """

import copy
import bisect
# import logging

import cv2
import numpy as np

import synopticgenerator.util as util
import synopticgenerator.shape as shape
import synopticgenerator.mathutil as mathutil
import synopticgenerator.plugins.filter.rearrange_by_config as rearrange_by_config
import synopticgenerator.plugins.filter.align_symmetry as align_symmetry
from synopticgenerator.plugins import Pipeline


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
        if self.config.get("inflate", False):
            inflated = copy.deepcopy(ctrls)
            map(lambda x: x.scale(1.2), inflated)

            inflated_points, inflated_indice = self.uniform_distribution(inflated, 1500)
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

        cluster_infos = []
        # resolve collision
        for i, cluster in enumerate(x_means.clusters):

            cluster.data *= [self.aspect_ratio_normalizer, self.aspect_ratio_normalizer]
            cluster.center *= [self.aspect_ratio_normalizer, self.aspect_ratio_normalizer]
            indice = np.unique(np.array(inflated_indice)[cluster.index])
            targets = np.array(ctrls)[indice]

            info = ClusterInformation(self.environ, cluster, targets)
            cluster_infos.append(info)

            content = self.analyze_cluster(content, info, targets)
            # self.resolve_collision(targets)
            # content = self.analyze_cluster(content, cluster, targets)

        for info in cluster_infos:
            print "info", info.upper_free(cluster_infos), info.lower_free(cluster_infos)

        if self.config.get('draw_debug', False):
            self.draw_debug(pointcloud_list, x_means.labels)

        return content

    def analyze_cluster(self, content, info, targets):
        sorted_by_y = sorted(targets, key=lambda x: x.center[1])

        if info.is_inside_central:
            center_ctrls = [ctrl for ctrl in shape.filter_has_attr_center_and_central(self.environ, sorted_by_y)]
            content = self.align_center(content, center_ctrls)

        if info.has_even_lr:
            lr_ctrls = [ctrl for ctrl in shape.filter_has_attr_not_center(self.environ, sorted_by_y)]
            content = self.align_symmetry(content, lr_ctrls)

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

            color = list(map(lambda x: x, (b, g, r)))

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

    def align_center(self, content, ctrls):
        config = {
            "arrangement": [],
            "arrange_direction": "down"
        }

        for ctrl in ctrls:
            config["arrangement"].append([ctrl])

        sub_module = rearrange_by_config.create(config, self.environ)
        content = sub_module.execute(content)
        return content

    def align_symmetry(self, content, ctrls):
        config = {
            "controls": ctrls
        }
        sub_module = align_symmetry.create(config, self.environ)
        content = sub_module.execute(content)

        return content


class ClusterInformation(object):

    def __init__(self, env, cluster, targets):
        # type: (Dict[str, Any], mathutil.XMeans.Cluster, List[shape.Shape]) -> None 
        self.env = env
        self.raw_cluster = cluster
        self.targets = targets

        # self.x_min = cluster.data.min(axis=0)[0]
        # self.x_max = cluster.data.max(axis=0)[0]
        # self.y_min = cluster.data.min(axis=0)[1]
        # self.y_max = cluster.data.max(axis=0)[1]
        self.x_min = min([x.top_left[0] for x in targets])
        self.x_max = max([x.top_right[0] for x in targets])
        self.y_min = min([x.bottom_left[1] for x in targets])
        self.y_max = max([x.top_left[1] for x in targets])
        self.center = shape.Vec2(*cluster.center)

        print self.x_min, self.x_max, self.y_min, self.y_max, self.center

        self.is_inside_central = util.is_point_inside_central_region(
            self.env, shape.Vec2(*cluster.center))

        self.has_even_lr = shape.contain_location_even_left_right(
            self.env, targets)

        self.c_count, self.l_count, self.r_count = shape.count_groupby_location(
            self.env, targets)

        self.c_rate = self.c_count / len(targets)
        self.l_rate = self.l_count / len(targets)
        self.r_rate = self.r_count / len(targets)

    def upper_free(self, others):
        # type: List[ClusterInformation] -> bool

        for other in others:
            if self == other:
                continue

            if not self.y_max < other.y_min:
                continue

            if not self.x_min < other.center.x and not other.center.x < self.x_max:
                continue

            return False

        else:
            return True

    def lower_free(self, others):
        # type: List[ClusterInformation] -> bool

        for other in others:
            if self == other:
                continue

            if not other.y_min < self.y_max:
                continue

            if not self.x_min < other.center.x and not other.center.x < self.x_max:
                continue

            return True

        else:
            return False


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return ExtrudeCollision(config, environ)
