""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
#
##############################################################################
import os
import re
import glob

import synopticgenerator.plugins.recognizer.image_to_shapes as image_to_shapes
from synopticgenerator.plugins import Pipeline
# import synopticgenerator.shape as shape
# import synopticgenerator.util as util
# import logging
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi+git@gmail.com"
__status__ = "Prototype"
##############################################################################


class ImagesToRegionFromFilename(Pipeline):
    # color = (172, 86, 221)

    place_holder_controller_name = "controller_name"

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

        self.sub_modules = []
        self.store = config.setdefault("store", "regions")

    def execute(self, content):
        glob_pat = self.config["image_pattern"]
        glob_pat = re.sub("{{\ *" + self.place_holder_controller_name + "\ *}}", "*", glob_pat)

        ctrl_pat = os.path.basename(self.config["image_pattern"])
        ctrl_pat = re.sub("{{\ *" + self.place_holder_controller_name + "\ *}}", "(\w+)", ctrl_pat)
        ctrl_expr = re.compile(ctrl_pat)

        files = glob.glob(glob_pat)
        for src_image in files:
            m = ctrl_expr.search(src_image)
            if m and m.group(1):
                ctrl_name = m.group(1)
            else:
                ctrl_name = ""

            conf = {
                'image': [src_image],
                'store': self.store,
                'controller_name': ctrl_name
            }
            reco = image_to_shapes.SearchContours(conf, self.environ)
            content = reco.execute(content)

        return content


def create(config, environ):
    return ImagesToRegionFromFilename(config, environ)


# def do(path):
#     c = create()
#     #return c.search_bounding_boxies(path)
#     return c.search_min_area_rect(path)
