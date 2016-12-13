""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################
import os
import cv2

import synopticgenerator.region as region
import synopticgenerator.util as util
import logging
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi+git@gmail.com"
__status__ = "Prototype"
##############################################################################


class SearchContours(object):
    # color = (172, 86, 221)

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.sub_modules = []
        self.store = config.setdefault("store", "regions")
        self.color_table = environ.setdefault("color_table", None)
        self.cutoff = environ.setdefault("cutoff_area", 9)

    def set_submodules(self, sub_modules):
        self.sub_modules = sub_modules

    def get_contours(self, image_path):
        self.image_path = image_path
        target_image = cv2.imread(self.image_path)

        # グレースケール
        im_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        # 2値化
        th1 = cv2.adaptiveThreshold(
            im_gray, 133, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 0)
        # ADAPTIVE_THRESH_MEAN_C
        # ADAPTIVE_THRESH_GAUSSIAN_C

        # 輪郭検出
        contours, hierarchy = cv2.findContours(
            # th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            th1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        return [c for c in contours if cv2.contourArea(c) > self.cutoff]

    def choose_region_by_area(self, cir, box, rot):
        ''' fuzzy finder for deternime shape type by its area.'''

        if cir.area < box.area and cir.area < rot.area:
            return cir

        if rot.area < box.area * 0.8:
            return rot

        return box

    def search_bounding_boxies(self, image_path):
        contours = self.get_contours(image_path)
        regions = []
        for con in contours:
            cv2.approxPolyDP(con, 3, True)
            center, radius = cv2.minEnclosingCircle(con)
            cir = region.circle(center, radius)
            cvrot = cv2.fitEllipse(con)
            eli = region.ellipse(cvrot)
            box = region.rect(cv2.boundingRect(con))
            rot = region.rotated_rect(cv2.minAreaRect(con))

            logging.debug("area: cir={}, box={}, rot={}, eli={}".format(
                cir.area, box.area, rot.area, eli.area))

            regions.append(self.choose_region_by_area(cir, box, rot))

        return regions

    def search_min_area_rect(self, image_path):
        contours = self.get_contours(image_path)
        regions = []
        for con in contours:
            cv2.approxPolyDP(con, 3, True)
            # box = region.rect(cv2.boundingRect(con))
            box = region.rotated_rect(cv2.minAreaRect(con))
            regions.append(box)

        return regions

    def execute(self, content):
        regions = []
        controller_name = self.config.get("controller_name")
        if controller_name and 'str' in str(type(controller_name)):
            naming = True

        for image in self.config["image"]:
            if not os.path.exists(image):
                logging.error("file not found: {}".format(image))
                continue

            x = self.search_bounding_boxies(image)
            if self.config.get("color"):
                for r in x:
                    r.color = util.color(self.config["color"], self.color_table)

            if naming:
                for r in x:
                    r.name = controller_name

            regions.extend(x)

        if content.get(self.store):
            content[self.store].extend(regions)
        else:
            content[self.store] = regions

        for smod in self.sub_modules:
            sub_res = smod.execute(content)
            if isinstance(sub_res, dict):
                content.update(sub_res)
            elif not isinstance(sub_res, list):
                content.append(sub_res)
            else:
                content.extend(sub_res)

        return content


def create(config, environ):
    return SearchContours(config, environ)


# def do(path):
#     c = create()
#     #return c.search_bounding_boxies(path)
#     return c.search_min_area_rect(path)
