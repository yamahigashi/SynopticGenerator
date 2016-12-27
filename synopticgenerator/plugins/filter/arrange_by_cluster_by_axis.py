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


class ArrangeByClusterByAxis(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.margin = self.config.setdefault("margin", 8)

        self.config.setdefault("axis", None)
        self.config.setdefault("threshold", 1e-4)
        self.config.setdefault("draw_debug", False)
        self.config.setdefault("equality_tolerance", 3.0)
        # self.config.setdefault("equality_tolerance", 1e-3)

    def check_config(self):
        # type: () -> None

        axis = self.config.get("axis")

        if not axis:
            raise Pipeline.ConfigInvalid("axis")

        if "x" not in axis and "y" not in axis:
            raise Pipeline.ConfigInvalid("axis")

    def execute(self, content):
        self.axis = self.config.get("axis").split(",")

        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        ctrls = self.controls if self.controls is not None else content[self.region]
        print "ctrls", [x.name for x in ctrls]
        w = self.environ.get("width")
        h = self.environ.get("height")

        if w < h:
            self.aspect_ratio_normalizer = h
        else:
            self.aspect_ratio_normalizer = w

        if "x" in self.axis:
            content = self.arrange_with_clustering_by_x(content, ctrls)

        if "y" in self.axis:
            content = self.arrange_with_clustering_by_y(content, ctrls)

        return content

    def arrange_with_clustering_by_x(self, content, ctrls):

        x_array = np.array([x.center[0] for x in ctrls], np.float64)
        # y_array = np.array([x.center[1] for x in ctrls], np.float64)

        zero_array = np.array([0. for i in range(len(x_array))])
        x_array = np.c_[x_array, zero_array]
        # y_array = np.c_[y_array, zero_array]

        x_x_means = clusterutil.x_means(self.environ, x_array, ctrls, self.aspect_ratio_normalizer)
        # y_x_means = mathutil.XMeans(random_state=1).fit(y_array)

        target_cols = {}  # type: Dict[int, shape.Shape]
        for i, cluster in enumerate(x_x_means.clusters):

            info = cluster.info
            sub_targets = np.array(ctrls)[cluster.index].tolist()
            if cluster.cov[0][0] < self.config.get("threshold"):
                # align x by cluster's center.x
                try:
                    col = {
                        "obj": sub_targets,
                        "center": cluster.info.center[1],
                        "min": cluster.info.top,
                        "max": cluster.info.bottom,
                    }
                    target_cols[len(sub_targets)].append(col)
                except KeyError:
                    target_cols[len(sub_targets)] = [col]

                for ctrl in sub_targets:
                    move = int(cluster.center[0] - ctrl.center.x)
                    ctrl.translate((move, 0))

                print "sub", len(sub_targets), [x.name for x in sub_targets]
            info.calculate_boundingbox()
            content = info.arrange_cluster_neighbor(content)

        print "cols", target_cols
        for elem_count, col in target_cols.iteritems():

            for row in self.group_by_equality(col):

                tmp = list(map(lambda x: sorted(x, key=lambda x: x.center[1]), row))
                transposed = list(map(list, zip(*tmp)))

                print "transposed", transposed
                content = self.solve_vertical_collision(content, transposed)

        return content

    def arrange_with_clustering_by_y(self, content, ctrls):

        # x_array = np.array([x.center[0] for x in ctrls], np.float64)
        y_array = np.array([x.center[1] for x in ctrls], np.float64)

        zero_array = np.array([0. for i in range(len(y_array))])
        # x_array = np.c_[x_array, zero_array]
        y_array = np.c_[y_array, zero_array]

        # x_x_means = clusterutil.x_means(self.environ, x_array, ctrls, self.aspect_ratio_normalizer)
        y_x_means = clusterutil.x_means(self.environ, y_array, ctrls, self.aspect_ratio_normalizer)

        vertical_targets = {}  # type: Dict[int, shape.Shape]
        for i, cluster in enumerate(y_x_means.clusters):

            info = cluster.info
            sub_targets = np.array(ctrls)[cluster.index].tolist()
            print cluster.cov
            if cluster.cov[0][0] < self.config.get("threshold"):
                # align x by cluster's center.x
                try:
                    vertical_targets[len(sub_targets)].append(sub_targets)
                except KeyError:
                    vertical_targets[len(sub_targets)] = [sub_targets]

                for ctrl in sub_targets:
                    move = int(cluster.center[0] - ctrl.center.y)
                    ctrl.translate((0, move))

                print "bub", len(sub_targets), [x.name for x in sub_targets]
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

    def group_by_equality(self, cols):

        results = []
        group_id = []

        # TODO: need to rewrite in more efficient algolithm
        for i, col in enumerate(cols):

            if i == 0:
                results.append([col["obj"]])
                group_id.append(len(results) - 1)
                continue

            for j, other in enumerate(cols):

                if other == col:
                    continue

                if self.calculate_equality(col, other):
                    print "equl"
                    results[group_id[j]].append(col["obj"])
                    group_id.append(j)

            else:
                results.append([col["obj"]])
                group_id.append(len(results) - 1)

        return results

    def calculate_equality(self, a, b):

        tol = self.config.get("equality_tolerance")
        center = abs(a["center"] - b["center"]) / self.aspect_ratio_normalizer
        min = float(abs(a["min"] - b["min"])) / self.aspect_ratio_normalizer
        max = float(abs(a["max"] - b["max"])) / self.aspect_ratio_normalizer

        if tol < center or tol < min or tol < max:
            return False

        return True

    def solve_vertical_collision(self, content, ctrl_cols=[], direction="down"):
        # type: (Dict[str, Any], List[shape.Shape], string) -> Dict[str, Any]

        config = {
            "arrangement": [],
            "arrange_direction": direction,
            "margin": self.margin,
            "skip_horizon": True
        }

        for col in ctrl_cols:
            config["arrangement"].append(col)

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
    return ArrangeByClusterByAxis(config, environ)
