""" coding: utf-8 """

import copy
import bisect
# import logging

import cv2
import numpy as np

import synopticgenerator.util as util
import synopticgenerator.shape as shape
import synopticgenerator.mathutil as mathutil
# import synopticgenerator.cluster as clusterutil

import synopticgenerator.plugins.filter.rearrange_by_config as rearrange_by_config
import synopticgenerator.plugins.filter.align_symmetry as align_symmetry
import synopticgenerator.plugins.filter.arrange_by_cluster_by_axis as arrange_by_cluster_by_axis

from synopticgenerator.plugins import Pipeline


class ExtrudeCollision(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.margin = self.config.setdefault("margin", 8)
        self.config.setdefault("inflate", False)
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

        # gather cog points
        cog_points_list = np.array([x.center for x in ctrls], np.float32)

        # inflate ctrls
        if self.config.get("inflate"):
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

        map(lambda x: x.analyze_adjacents(cluster_infos), cluster_infos)
        sorted(cluster_infos, key=lambda x: util.get_distance_from_cog(self.environ, x.center))

        # align cluster by distance from center of background
        for info in cluster_infos:
            content = self.arrange_cluster(content, info)
            content = self.arrange_cluster_neighbor(content, info)
            content = self.solve_collision(content, info)

        if self.config.get('draw_debug'):
            self.draw_debug(pointcloud_list, x_means.labels)

        return content

    def arrange_with_clustering_by_x(self, content, targets):
        pass

    def arrange_cluster(self, content, info):
        sorted_by_y = sorted(info.targets, key=lambda x: x.center[1])

        if info.is_inside_central:

            if info.upper_free:
                direction = "up"
                sorted_by_y.reverse()

            elif info.lower_free:
                direction = "down"

            else:
                direction = "down"

            if 0.7 < info.c_rate:
                center_ctrls = [ctrl for ctrl in shape.filter_only_central(self.environ, sorted_by_y)]
                content = self.solve_vertical_collision(content, [center_ctrls], direction=direction)
                print "solve_vertical_collision", len(center_ctrls), [x.name for x in center_ctrls]

                center_ctrls = [ctrl for ctrl in shape.filter_has_attr_center_and_central(self.environ, sorted_by_y)]
                content = self.align_center(content, sorted_by_y)
                print "align_center", [x.name for x in center_ctrls]

            else:
                center_ctrls = [ctrl for ctrl in shape.filter_has_attr_center_and_central(self.environ, sorted_by_y)]
                content = self.align_center(content, center_ctrls)

        if info.has_even_lr:
            lr_ctrls = [ctrl for ctrl in shape.filter_has_attr_not_center(self.environ, info.targets)]
            print "has_even_lr", [c.name for c in lr_ctrls]
            content = self.align_symmetry(content, lr_ctrls)

        # update
        info.calculate_boundingbox()

        return content

    def arrange_cluster_neighbor(self, content, info):
        # type: (Dict[str, object], ClusterInformation) -> Dict[str, object]

        for neighbor in info.adjacents:
            u, d, l, r = info.is_infringement(neighbor)
            if neighbor.is_inside_central:
                if u:
                    neighbor.translate(shape.Vec2(0, info.get_infringement(neighbor, "top")))
                if d:
                    neighbor.translate(shape.Vec2(0, info.get_infringement(neighbor, "bottom")))

            else:
                if l:
                    neighbor.translate(shape.Vec2(info.get_infringement(neighbor, "left"), 0))
                if r:
                    neighbor.translate(shape.Vec2(info.get_infringement(neighbor, "right"), 0))

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

    def uniform_distribution(self, ctrls, point_count):
        # type: (List[shape.Shape], int) -> (List[shape.Vec2], List[int])

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

    def solve_collision(self, content, cluster):
        # type: (Dict[str, object], ClusterInformation) -> None

        config = {"margin": self.config.get("margin")}
        if not cluster.lower_free and not cluster.upper_free:

            if cluster.c_rate < 0.5:
                if cluster.has_even_lr:
                    config["arrange_direction"] = "horizontal"

                elif cluster.l_rate < cluster.r_rate:
                    config["arrange_direction"] = "left"

                elif cluster.r_rate < cluster.l_rate:
                    config["arrange_direction"] = "right"

                else:
                    config = self.config

            else:
                # TODO
                pass
                # return content

        elif (
                util.is_point_inside_upper_region(self.environ, cluster.center) or
                util.is_point_inside_lower_region(self.environ, cluster.center)):

            if cluster.c_rate < 0.5:
                if cluster.has_even_lr:
                    config["arrange_direction"] = "horizontal"

                elif cluster.l_rate < cluster.r_rate:
                    config["arrange_direction"] = "left"

                elif cluster.r_rate < cluster.l_rate:
                    config["arrange_direction"] = "right"

                else:
                    config = self.config

            else:
                # TODO
                pass
                # return content

        else:
            content = self.solve_collision_as_grid(content, cluster)
            return content

        print config, [x.name for x in cluster.targets]

        all = sorted(cluster.targets, key=lambda x: x.area)
        while all:
            target = all.pop()
            for b in all:
                protrude = b.calculate_infringement(target, config=config)
                protrude = b.solve_direction_to_avoid(protrude, other=target, config=config)

                print target.top_right[0], b.top_left[0], b.name, protrude

                b.translate(protrude)

        return content

    def solve_collision_as_grid(self, content, cluster):
        # type: (Dict[str, object], ClusterInformation) -> Dict[str, object]

        if len(cluster.targets) < 3:
            return content

        config = self.config
        config.update({"axis": "x,y", "controls": cluster.targets})

        mod = arrange_by_cluster_by_axis.create(config, self.environ)
        content = mod.execute(content)

        return content

    def solve_vertical_collision(self, content, ctrl_cols=[], direction="down"):
        # type: (Dict[str, Any], List[shape.Shape], string) -> Dict[str, Any]

        config = {
            "arrangement": [],
            "arrange_direction": direction,
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

    def align_center(self, content, ctrls):
        # type: (Dict[str, Any], List[shape.Shape]) -> Dict[str, Any]

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
        # type: (Dict[str, Any], List[shape.Shape]) -> Dict[str, Any]

        config = {
            "controls": ctrls
        }
        sub_module = align_symmetry.create(config, self.environ)
        content = sub_module.execute(content)

        return content


def create(config, environ):
    return ExtrudeCollision(config, environ)
