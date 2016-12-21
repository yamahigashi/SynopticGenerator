""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
##############################################################################
__author__ = "MATSUMOTO Takayoshi"
__credits__ = ["MATSUMOTO Takayoshi", ]
__license__ = "Modified BSD license"
__version__ = "0.0.1"
__maintainer__ = "MATSUMOTO Takayoshi"
__email__ = "yamahigashi+git@gmail.com"
__status__ = "Prototype"
__all__ = ["SoftimageHTMLWriter"]
##############################################################################

import os
import yaml
import logging

import synopticgenerator.shape as shape
import synopticgenerator.util as util

##############################################################################


class Writer(object):
    output_filename = ""
    has_lxml = False
    bounding_boxies = None

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.regions = []

        if self.config.get("template"):
            self.template = yaml.load(open(self.config["template"]))
        else:
            self.template = None
        self.version = config.setdefault("version", "2")

    def execute(self, content):
        if not content.get("regions"):
            return content

        for r in content["regions"]:
            self.regions.append(r)
        self.write(self.config["output"])

        return content

    def preprocess_read_bound(self):
        pass

    def postprocess_read_bound(self):
        pass

    def preprocess_write_bound(self):
        pass

    def postprocess_write_bound(self):
        pass

    def preprocess_write_area(self, body):
        if not self.template:
            return

        sc = body.find('script')
        sc.text = self.template["default_script"]

    def postprocess_write_area(self, body):
        if not self.template:
            return

        try:
            import lxml.etree as ET
            self.has_lxml = True
        except ImportError:
            import xml.etree.cElementTree as ET

        region_map = body.find('map')
        for r in self.template["default_regions"]:
            area = ET.SubElement(region_map, "area")
            area.set("shape", r["shape"])
            area.set("coords", r["coords"])
            area.set("title", "")
            area.set("NOHREF", "true")
            area.set("onClick", r["name"])
            area.text = ""

    def write(self, output_filename):
        try:
            import lxml.etree as ET
            self.has_lxml = True
        except ImportError:
            import xml.etree.cElementTree as ET

        self.output_filename = output_filename

        root = ET.Element("html")

        body = ET.SubElement(root, 'body')
        body.set("version", self.version)
        sc = ET.SubElement(body, "script")
        sc.set("language", self.config["language"])

        region_map = ET.SubElement(body, "map")
        region_map.set("name", "SynopticMap")
        self.preprocess_write_area(body)
        for i, b in enumerate(self.regions):
            name = b.name if b.name else "plz_replace_{}".format(str(i))

            if self.template:
                sc.text += self.template["select_formatter"].format(name=name)
            else:
                sc.text += """def {name}_onClick (in_obj, in_mousebutton, in_keymodifier): syn.select(in_mousebutton, in_keymodifier, '{name}')
""".format(name=name)

            self.write_shape(region_map, b, name)

        self.postprocess_write_area(body)

        img = ET.SubElement(body, "img")
        img.set("src", os.path.splitext(self.output_filename)[0] + ".png")
        img.set("usemap", "#SynopticMap")
        img.text = ""
        tree = ET.ElementTree(root)

        util.ensure_folder(self.output_filename)
        if self.has_lxml:
            tree.write(self.output_filename, pretty_print=True)
        else:
            tree.write(self.output_filename)

    def write_shape(self, parent, bound, name):
        try:
            import lxml.etree as ET
            self.has_lxml = True
        except ImportError:
            import xml.etree.cElementTree as ET

        if type(bound) is shape.Rect:
            shape_name, coords = self.write_rect(parent, bound, name)
        elif type(bound) is shape.RotatedRect:
            shape_name, coords = self.write_poly(parent, bound, name)
        elif type(bound) is shape.RotatedRect:
            shape_name, coords = self.write_circle(parent, bound, name)

        else:
            logging.error("not found writer for this region")

        area = ET.SubElement(parent, "area")
        area.set("shape", shape_name)
        area.set("coords", coords)
        area.set("title", "")
        area.set("NOHREF", "true")
        area.set("onClick", name + "_onClick")
        area.text = ""

    def write_rect(self, parent, control, name):
        x = control.top_left[0]
        y = control.top_left[1]
        x2 = control.bottom_right[0]
        y2 = control.bottom_right[1]
        str_coords = "%s,%s,%s,%s" % (x, y, x2, y2)

        return "rect", str_coords

    def write_poly(self, parent, control, name):
        coords = []
        for p in control.points:
            coords.extend((str(p[0]), str(p[1])))
        str_coords = ",".join(coords)

        return "poly", str_coords

    def write_circle(self, parent, control, name):
        str_coords = "%s,%s,%s" % (
            control.center[0], control.center[1], control.radius)

        return "circle", str_coords


def create(config, environ):
    return Writer(config, environ)
