""" coding: utf-8 """

# import copy
# import bisect
# import logging

import cv2
import numpy as np

# import synopticgenerator.util as util
# import synopticgenerator.shape as shape
import synopticgenerator.cluster as clusterutil
# import synopticgenerator.mathutil as mathutil
import synopticgenerator.plugins.filter.rearrange_by_config as rearrange_by_config
from synopticgenerator.plugins import Pipeline


class ArrangeByClusterX(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def set_default_config(self):
        # type: () -> None

        self.environ.setdefault("width", 320)
        self.environ.setdefault("height", 550)

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.margin = self.config.setdefault("margin", 8)
        # self.config.setdefault('draw_debug', False)

        self.config.setdefault("threshold", 1e-4)
        self.config.setdefault('draw_debug', False)

    def execute(self, content):
        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        ctrls = self.controls or content[self.region]
        w = self.environ.get("width")
        h = self.environ.get("height")

        if w < h:
            self.aspect_ratio_normalizer = h
        else:
            self.aspect_ratio_normalizer = w

        content = self.arrange_with_clustering_by_x(content, ctrls)

        return content

    def arrange_with_clustering_by_x(self, content, ctrls):

        x_array = np.array([x.center[0] for x in ctrls], np.float64)
        # y_array = np.array([x.center[1] for x in ctrls], np.float64)

        zero_array = np.array([0. for i in range(len(x_array))])
        x_array = np.c_[x_array, zero_array]
        # y_array = np.c_[y_array, zero_array]

        x_x_means = clusterutil.x_means(self.environ, x_array, ctrls, self.aspect_ratio_normalizer)
        # y_x_means = mathutil.XMeans(random_state=1).fit(y_array)

        vertical_targets = {}  # type: Dict[int, shape.Shape]
        for i, cluster in enumerate(x_x_means.clusters):

            info = cluster.info
            sub_targets = np.array(ctrls)[cluster.index].tolist()
            if cluster.cov[0][0] < self.config.get("threshold"):
                # align x by cluster's center.x
                try:
                    vertical_targets[len(sub_targets)].append(sub_targets)
                except KeyError:
                    vertical_targets[len(sub_targets)] = [sub_targets]

                for ctrl in sub_targets:
                    move = int(cluster.center[0] - ctrl.center.x)
                    ctrl.translate((move, 0))

            print "sub", len(sub_targets), [x.name for x in sub_targets]
            info.calculate_boundingbox()
            content = info.arrange_cluster_neighbor(content)

        # for k, sub_targets in vertical_targets.iteritems():
        #     tmp = list(map(lambda x: sorted(x, key=lambda x: x.center[1]), sub_targets))
        #     transposed = list(map(list, zip(*tmp)))
        #     content = self.solve_vertical_collision(content, transposed)

        return content

    def draw_debug(self, points_input, classified_points):
        # type: (List[shape.Vec2], List[int]) -> None

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

    def solve_vertical_collision(self, content, ctrl_cols=[], direction="down"):
        # type: (Dict[str, Any], List[shape.Shape], string) -> Dict[str, Any]

        config = {
            "arrangement": [],
            "arrange_direction": direction,
            "margin": self.margin,
            "skip_horizon": True
        }

        for col in ctrl_cols:
            for ctrl in col:
                config["arrangement"].append([ctrl])

        sub_module = rearrange_by_config.create(config, self.environ)
        content = sub_module.execute(content)
        return content

    def solve_horizontal_collision(self, content, ctrl_cols=[], direction="right"):
        # type: (Dict[str, Any], List[shape.Shape], string) -> Dict[str, Any]

        config = {
            "arrangement": [],
            "arrange_direction": direction
        }

        for col in ctrl_cols:
            for i, ctrl in enumerate(col):
                try:
                    config["arrangement"][i].append(ctrl)
                except IndexError:
                    config["arrangement"].append([ctrl])

        sub_module = rearrange_by_config.create(config, self.environ)
        content = sub_module.execute(content)
        return content


def create(config, environ):
    return ArrangeByClusterX(config, environ)
