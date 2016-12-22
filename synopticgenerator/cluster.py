""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.

# import logging
import numpy as np

import synopticgenerator.util as util
import synopticgenerator.mathutil as mathutil
import synopticgenerator.shape as shape


class ClusterInformations(list):

    pass


class ClusterInformation(object):

    def __init__(self, env, cluster, targets):
        # type: (Dict[str, Any], mathutil.XMeans.Cluster, List[shape.Shape]) -> None

        self.env = env
        self.raw_cluster = cluster
        self.targets = targets
        self.adjacents = []  # type: List[ClusterInformation]
        self.calculate_boundingbox()

        self.is_inside_central = util.is_point_inside_central_region(
            self.env, shape.Vec2(*cluster.center))

        self.has_even_lr = shape.contain_location_even_left_right(
            self.env, targets)

        self.c_count, self.l_count, self.r_count = shape.count_groupby_location(
            self.env, targets)

        self.c_rate = float(self.c_count) / float(len(targets))
        self.l_rate = float(self.l_count) / float(len(targets))
        self.r_rate = float(self.r_count) / float(len(targets))

    def calculate_boundingbox(self):
        # type: () -> None

        # self.left = cluster.data.min(axis=0)[0]
        # self.right = cluster.data.max(axis=0)[0]
        # self.top = cluster.data.min(axis=0)[1]
        # self.bottom = cluster.data.max(axis=0)[1]

        self.left = min([x.top_left[0] for x in self.targets])
        self.right = max([x.top_right[0] for x in self.targets])
        self.top = min([x.top_left[1] for x in self.targets])
        self.bottom = max([x.bottom_left[1] for x in self.targets])
        self.center = shape.Vec2(*self.raw_cluster.center)

    def analyze_adjacents(self, others):
        # type: (List[ClusterInformation]) -> None

        self.set_adjacents(others)
        self.upper_free = self.is_upper_free(others)
        self.lower_free = self.is_lower_free(others)

    def set_adjacents(self, others):
        # type: List[ClusterInformation] -> None

        def calc_dist(target_center):
            diff = self.center - target_center
            return abs(diff.x) + abs(diff.y)

        dists = map(calc_dist, [x.center for x in others])
        neighbor_dist_value = sorted(dists)[1:(len(dists) + 1) / 2]
        neighbor_indice = [dists.index(x) for x in neighbor_dist_value]
        self.adjacents = [others[x] for x in neighbor_indice]

    def is_upper_free(self, others):
        # type: List[ClusterInformation] -> bool

        if util.is_point_inside_upper_region(self.env, self.center):
            return False

        for other in others:
            if self == other:
                continue

            if not self.top < other.bottom:
                continue

            if not self.left < other.center.x and not other.center.x < self.right:
                continue

            return False

        else:
            return True

    def is_lower_free(self, others):
        # type: List[ClusterInformation] -> bool

        if util.is_point_inside_lower_region(self.env, self.center):
            return False

        for other in others:
            if self == other:
                continue

            if not other.top < self.bottom:
                continue

            if not self.left < other.center.x and not other.center.x < self.right:
                continue

            return True

        else:
            return False

    def is_infringement(self, other):
        # type: ClusterInformation -> list[bool, bool, bool, bool]

        # shortcut
        m = self.env.get("margin", 8)

        up = (self.top - m) < other.bottom and other.bottom < (self.bottom + m)
        down = (other.top - m) < self.bottom and self.bottom < (other.bottom + m)
        right = (other.left - m) < self.right and self.right < (other.right + m)
        left = (self.left - m) < other.right and other.right < (self.right + m)

        side = ((self.left < other.center.x and other.center.x < self.right) or
                (self.left < other.center.x and other.center.x < self.right))

        updown = ((self.top < other.center.y and other.center.y < self.bottom) or
                  (self.top < other.center.y and other.center.y < self.bottom))

        upper = up and side
        lower = down and side
        right_side = right and updown
        left_side = left and updown

        return upper, lower, right_side, left_side

    def get_infringement(self, other, direction):
        # type: (ClusterInformation, string) -> float

        m = self.env.get("margin", 8)

        if direction == "top":
            res = self.top - other.bottom - m

        elif direction == "bottom":
            res = self.bottom - other.top + m

        elif direction == "left":
            res = other.right - self.left - m
            print other.bottom, self.top

        elif direction == "right":
            res = other.left - self.right + m
            print other.bottom, self.top

        else:
            raise

        return res

    def translate(self, move):
        # type: shape.Vec2 -> None
        map(lambda x: x.translate(move), self.targets)
        self.calculate_boundingbox()

    def arrange_cluster_neighbor(self, content):
        # type: (Dict[str, object], ClusterInformation) -> Dict[str, object]

        for neighbor in self.adjacents:
            u, d, l, r = self.is_infringement(neighbor)
            if neighbor.is_inside_central:
                if u:
                    neighbor.translate(shape.Vec2(0, self.get_infringement(neighbor, "top")))
                if d:
                    neighbor.translate(shape.Vec2(0, self.get_infringement(neighbor, "bottom")))

            else:
                if l:
                    neighbor.translate(shape.Vec2(self.get_infringement(neighbor, "left"), 0))
                if r:
                    neighbor.translate(shape.Vec2(self.get_infringement(neighbor, "right"), 0))

        return content


# ----------------------------------------------------------------------------
#
# utility
#
# ----------------------------------------------------------------------------
def x_means(env, point_array, ctrls, size_normalizer=1.0):
    # type: (Dict[str, object], np.array, float, shape.Shape) -> mathutil.XMeans.Cluster

    point_array = point_array / size_normalizer
    results = mathutil.XMeans(random_state=1).fit(point_array)
    infos = []

    for cluster in results.clusters:
        cluster.data *= [size_normalizer, size_normalizer]
        cluster.center *= [size_normalizer, size_normalizer]

        targets = np.array(ctrls)[cluster.index].tolist()

        info = ClusterInformation(env, cluster, targets)
        infos.append(info)

        setattr(cluster, "info", info)

    for info in infos:
        info.set_adjacents(infos)

    return results
