""" coding: utf-8 """

import bisect
import cv2
import numpy as np
import synopticgenerator.mathutil as mathutil


class RealignmentPosition(object):
    ''' clustering given shape as cog points by k-means. '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)

        self.ratio_over_unbalance = 4.0
        self.ratio_very_circle = 1.5
        self.ratio_lower_end_region = 0.25

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        shapes = content[self.region]
        w = self.environ.get("width", 320)
        h = self.environ.get("height", 550)

        if w < h:
            normal_ratio = h
        else:
            normal_ratio = w

        # gather cog points
        cog_points_list = np.array([x.center for x in shapes], np.float32)
        # pointcloud_list = np.array([x.center for x in shapes], np.float32)
        # pointcloud_list = np.array([x.scatter_points(16) for x in shapes], np.float32)
        points = self.uniform_distribution(shapes, 500)
        pointcloud_list = np.array(points, np.float32)

        pointcloud_list = np.r_[pointcloud_list, cog_points_list]
        pointcloud_list /= normal_ratio

        # calculate x-means
        # x_means = mathutil.XMeansCV2(random_state=1).fit(pointcloud_list)
        x_means = mathutil.XMeans(random_state=1).fit(pointcloud_list)
        pointcloud_list *= normal_ratio

        for cluster in x_means.clusters:
            x = np.std(cluster.data[0:, 0]) * normal_ratio
            y = np.std(cluster.data[0:, 1]) * normal_ratio

            if x < y:
                is_vertical_longer = True
                ratio = y / x
            else:
                is_vertical_longer = False
                ratio = x / y

            targets = [x for i, x in enumerate(shapes) if i in cluster.index]
            if self.ratio_over_unbalance < ratio:
                if is_vertical_longer:
                    print "vertical"
                    self.align_horizontal(cluster, targets)

                else:
                    self.align_vertical(cluster, targets)

            elif ratio < self.ratio_very_circle:
                print "circle", ratio

            else:
                print "none of them", ratio
                _x = np.array([x.center[0] for x in targets], np.float32)
                # k_means_about_x = mathutil.XMeans(random_state=1).fit(_x)

                '''
                compactness, labels, centers = cv2.kmeans(
                    data=_x, K=3, bestLabels=None,
                    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10),
                    attempts=1, flags=cv2.KMEANS_RANDOM_CENTERS)
                print labels
                '''

        if self.config.get('draw_debug', True):
            self.draw_debug(pointcloud_list, x_means.labels)

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

            cv2.circle(blank_image_classified, (int(point[0]), int(point[1])), 3, color, 2)

        # cv2.imshow("Points", blank_image)
        cv2.imshow("Points Classified", blank_image_classified)
        cv2.waitKey()

    def align_horizontal(self, cluster, targets):
        for shape in targets:
            _x = cluster.center[0] - shape.center[0]
            shape.translate((_x, 0))

    # def align_horizontal_by_center(self, cluster, targets):
    #     for shape in targets:
    #         print shape.name

    def align_vertical(self, cluster, targets):
        # if it is in the lower area, align it downward or align it centeroid
        h = self.environ.get("height", 10) * (1.0 - self.ratio_lower_end_region)
        if cluster.center[1] < h:
            self.align_vertical_by_center(cluster, targets)
        else:
            self.align_vertical_by_bottom(cluster, targets)

    def align_vertical_by_center(self, cluster, targets):
        for shape in targets:
            _y = cluster.center[1] - shape.center[1]
            shape.translate((0, _y))

    def align_vertical_by_bottom(self, cluster, targets):
        y_mean = np.mean(np.array([x.bottom for x in targets]))
        for shape in targets:
            _y = y_mean - shape.bottom
            shape.translate((0, _y))

    def uniform_distribution(self, shapes, point_count):

        # 面積に応じてscatter, まずは累積面積のリスト作る
        sum_area = 0.0
        cumulative_areas = []
        for x in shapes:
            sum_area += x.area
            cumulative_areas.append(sum_area)

        def _choose(areas, end, i):
            p = np.random.uniform(0.0, sum_area)
            selected_index = bisect.bisect_left(areas, p)

            return selected_index

        points = []
        for i in range(point_count):
            points.append(shapes[_choose(cumulative_areas, sum_area, i)].scatter_points(i))

        return points


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return RealignmentPosition(config, environ)
