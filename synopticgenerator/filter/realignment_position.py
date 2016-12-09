""" coding: utf-8 """

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

        # gather cog points
        cog_points_list = np.array([x.center for x in shapes], np.float32)

        # calculate x-means
        x_means = mathutil.XMeans(random_state=1).fit(cog_points_list)

        for cluster in x_means.clusters:
            x = np.std(cluster.data[0:, 0])
            y = np.std(cluster.data[0:, 1])

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

        if self.config.get('draw_debug', True):
            self.draw_debug(cog_points_list, x_means.labels)

        return content

    def draw_debug(self, points_input, classified_points):
        # draw debug
        blank_image = np.zeros((800, 800, 3))
        blank_image_classified = np.zeros((800, 800, 3))

        for point in points_input:
            cv2.circle(blank_image, (int(point[0]), int(point[1])), 1, (0, 255, 0), -1)

        for point, allocation in zip(points_input, classified_points):
            if allocation == 0:
                color = (255, 0, 0)

            elif allocation == 1:
                color = (0, 0, 255)

            elif allocation == 2:
                color = (0, 255, 0)

            elif allocation == 3:
                color = (255, 255, 0)

            else:
                color = (255, 255, 255)

            cv2.circle(blank_image_classified, (int(point[0]), int(point[1])), 3, color, -1)

        cv2.imshow("Points", blank_image)
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


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return RealignmentPosition(config, environ)
