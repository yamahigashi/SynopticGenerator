""" coding: utf-8 """
# Copyright 2016, MATSUMOTO Takayoshi
# All rights reserved.
##############################################################################

# import os
import logging
# import math

import synopticgenerator.shape as shape
import synopticgenerator.util as util

try:
    import lxml.etree as ET
    has_lxml = True
except ImportError:
    import xml.etree.cElementTree as ET
    has_lxml = False

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


class Writer(object):
    output_filename = ""
    bounding_boxies = None

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.regions = []
        self.version = config.setdefault("version", "2")

    def execute(self, content):
        if not content.get("regions"):
            return content

        for r in content["regions"]:
            self.regions.append(r)

        self.bg_width = self.environ.get("width", 300)
        self.bg_height = self.environ.get("height", 600)

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
            return

    def postprocess_write_area(self, body):
            return

    def write(self, output_filename):

        self.output_filename = output_filename

        root = ET.Element("ui")
        root.set("version", "4.0")

        klass = ET.SubElement(root, 'class')
        klass.text = "mgear"
        widget = self.write_main_widget(root)
        self.write_background_image(widget)

        self.preprocess_write_area(root)
        for i, b in enumerate(self.regions):
            name = b.name if b.name else "plz_replace_{}".format(str(i))
            self.write_shape(widget, b, name)

        self.postprocess_write_area(widget)

        self.write_custom_widgets(root)
        ET.SubElement(root, "resources")
        ET.SubElement(root, "connections")

        tree = ET.ElementTree(root)
        util.ensure_folder(self.output_filename)
        if has_lxml:
            tree.write(self.output_filename, pretty_print=True, xml_declaration=True, encoding="utf-8")
        else:
            tree.write(self.output_filename, xml_declaration=True)

    def write_main_widget(self, parent):
        widget = ET.SubElement(parent, 'widget')
        widget.set("class", "QWidget")
        widget.set("name", self.environ.get("recipe_name"))
        self._write_geometry(widget, [0, 0, self.bg_width, self.bg_height])

        prop2 = ET.SubElement(widget, "property")
        prop2.set("name", "windowTitle")
        str = ET.SubElement(prop2, "string")
        str.text = "Form"

        return widget

    def write_background_image(self, parent):

        widget = ET.SubElement(parent, 'widget')
        widget.set("class", "QLabel")
        widget.set("name", "img_background")
        prop = ET.SubElement(widget, "property")
        prop.set("name", "enabled")
        propval = ET.SubElement(prop, "bool")
        propval.text = "true"

        self._write_geometry(widget, [0, 0, self.bg_width, self.bg_height])

        prop2 = ET.SubElement(widget, "property")
        prop2.set("name", "windowTitle")
        str = ET.SubElement(prop2, "string")
        str.text = "Form"

        prop3 = ET.SubElement(widget, "property")
        prop3.set("name", "pixmap")
        str = ET.SubElement(prop3, "pixmap")
        img_path = self.config.get("background")
        str.text = img_path

        return widget

    def write_shape(self, parent, bound, name):

        if type(bound) is shape.Rect:
            shape_name, coords = self.write_rect(parent, bound, name)
        elif type(bound) is shape.RotatedRect:
            return
            # shape_name, coords = self.write_RotatedRect(parent, bound, name)
        elif type(bound) is shape.Circle:
            shape_name, coords = self.write_circle(parent, bound, name)

        else:
            logging.error("not found writer for this region")

        widget = ET.SubElement(parent, "widget")
        widget.set("class", shape_name)
        widget.set("name", "w_{}".format(name))
        widget.set("native", "true")

        self._write_geometry(widget, coords)

        fill = ET.SubElement(widget, "property")
        fill.set("name", "autoFillBackground")
        yes = ET.SubElement(fill, "bool")
        yes.text = "true"

        target = ET.SubElement(widget, "property")
        target.set("name", "object")
        target.set("stdset", "0")
        strname = ET.SubElement(target, "string")
        strname.text = name

    def write_rect(self, parent, control, name):
        x = control.top_left[0]
        y = control.top_left[1]
        x2 = control.bottom_right[0] - x
        y2 = control.bottom_right[1] - y
        coords = list(map(int, [x, y, x2, y2]))

        return self.get_selector_button_class(control, "Box"), coords

    def write_poly(self, parent, control, name):
        coords = []
        for p in control.points:
            coords.extend((str(p[0]), str(p[1])))
        # str_coords = ",".join(coords)
        coords = (coords[0], coords[1], coords[-2], coords[-1])

        return self.get_selector_button_class(control, "Box"), coords

    def write_circle(self, parent, control, name):
        x = control.top_left[0]
        y = control.top_left[1]
        x2 = control.bottom_right[0] - x
        y2 = control.bottom_right[1] - y
        coords = (x, y, x2, y2)

        return self.get_selector_button_class(control, "Circle"), coords

    def get_selector_button_class(self, control, shape_name):
        if control.location == shape.LocationAttributeCenter:
            loc = "C"
        elif control.location == shape.LocationAttributeLeft:
            loc = "L"
        elif control.location == shape.LocationAttributeRight:
            loc = "R"
        else:
            loc = "C"

        selector_class = "SelectBtn_{}Fk{}".format(loc, shape_name)
        return selector_class

    def _write_geometry(self, node, coords):
        prop = ET.SubElement(node, "property")
        prop.set("name", "geometry")
        rect = ET.SubElement(prop, "rect")
        x = ET.SubElement(rect, "x")
        x.text = str(coords[0])
        y = ET.SubElement(rect, "y")
        y.text = str(coords[1])
        w = ET.SubElement(rect, "width")
        w.text = str(coords[2])
        h = ET.SubElement(rect, "height")
        h.text = str(coords[3])

    def write_custom_widgets(self, parent):
        widgets = [
            {"class": "QuickSelButton",      "extends": "QPushButton", "header": "mgear.maya.synoptic.widgets"},
            {"class": "SelectBtn_RFkBox",    "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_RIkBox",    "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_CIkBox",    "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_LFkBox",    "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_LIkBox",    "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_CFkBox",    "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_RIkCircle", "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_CIkCircle", "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "SelectBtn_LIkCircle", "extends": "QWidget",     "header": "mgear.maya.synoptic.widgets",  "container": "1"},
            {"class": "MirrorPoseButton",    "extends": "QPushButton", "header": "mgear.maya.synoptic.widgets"},
            {"class": "FlipPoseButton",      "extends": "QPushButton", "header": "mgear.maya.synoptic.widgets"},
            {"class": "resetBindPose",       "extends": "QPushButton", "header": "mgear.maya.synoptic.widgets"},
            {"class": "resetTransform",      "extends": "QPushButton", "header": "mgear.maya.synoptic.widgets"},
            {"class": "toggleCombo",         "extends": "QComboBox",   "header": "mgear.maya.synoptic.widgets"},
            {"class": "ikfkMatchButton",     "extends": "QPushButton", "header": "mgear.maya.synoptic.widgets"}
        ]

        container = ET.SubElement(parent, "customwidgets")

        for widiget_entry in widgets:
            widget = ET.SubElement(container, "customwidget")
            # for k, v in widiget_entry.iteritems():
            for k in ["class", "extends", "header", "container"]:
                v = widiget_entry.get(k, None)
                if not v:
                    continue
                prop = ET.SubElement(widget, k)
                prop.text = v


def create(config, environ):
    return Writer(config, environ)
