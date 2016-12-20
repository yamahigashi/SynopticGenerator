""" coding: utf-8 """

import re
import logging

import synopticgenerator.util as util
import synopticgenerator.shape as shape
from synopticgenerator import Pipeline


class AlignSymmetry(Pipeline):
    ''' clustering given ctrl as cog points by k-means. '''

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.region = config.setdefault("region_name", "regions")
        self.controls = config.setdefault("controls", None)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        ctrls = self.controls or content[self.region]

        lr_ctrls = [ctrl for ctrl in self.filter_has_attr_not_center(ctrls)]
        content = self.align_symmetry(content, lr_ctrls)

        return content

    def align_symmetry(self, content, ctrls):

        location_expression = self.environ.get("location_expression")
        location_labels = self.environ.get("location_label")
        ll = location_labels.get("left")
        rl = location_labels.get("right")
        cl = location_labels.get("center")

        loc_expr = re.sub(
            "{{\s+location\s+}}",
            "(?P<location_label>({}|{}|{}))".format(ll, rl, cl),
            location_expression)
        loc_expr = "(.*){}(.*)".format(loc_expr)
        expr = re.compile(loc_expr)

        def repl(match_obj):
            s = list(match_obj.string)
            for i in range(match_obj.start("location_label"), match_obj.end("location_label")):
                s[i] = "location_label_was_here"
            return "".join(s)

        symmetry_pair = {}
        for ctrl in ctrls:
            n = expr.sub(repl, ctrl.name)
            try:
                symmetry_pair[n].append(ctrl)
            except KeyError:
                symmetry_pair[n] = [ctrl]
            # config["arrangement"].append([ctrl])

        for key in symmetry_pair.keys():
            row = symmetry_pair[key]
            if not len(row) == 2:
                msg = "skip row align_symmetry"
                logging.warn(msg)
                continue

            bg_center = util.get_x_center(self.environ)
            cog_x, cog_y = (row[0].center + row[1].center) / 2.0
            off_x = bg_center - cog_x

            for ctrl in row:
                ctrl.translate((off_x, cog_y - ctrl.center.y))

        return content

    def filter_has_attr_center_and_central(self, ctrls):
        # type: (list[shape.Shape]) -> list[shape.Shape]
        for ctrl in ctrls:
            if hasattr(ctrl, "location") and ctrl.location != shape.LocationAttributeCenter:
                continue

            pos = shape.Vec2(*ctrl.center)
            if not util.is_point_inside_central_region(self.environ, pos):
                continue

            yield ctrl

    def filter_has_attr_not_center(self, ctrls):
        # type: (list[shape.Shape]) -> list[shape.Shape]

        for ctrl in ctrls:
            if not hasattr(ctrl, "location"):
                continue

            if ctrl.location == shape.LocationAttributeCenter:
                continue

            yield ctrl

    def contain_location_even_left_right(self, ctrls):
        # type: (list[shape.Shape]) -> boolean
        c_count = 0
        l_count = 0
        r_count = 0

        for ctrl in ctrls:
            if not hasattr(ctrl, "location"):
                continue

            if ctrl.location == shape.LocationAttributeLeft:
                l_count += 1
            elif ctrl.location == shape.LocationAttributeRight:
                r_count += 1
            else:
                c_count += 1

        mes = "contain_location_even_left_right = c({}), l({}), r({})".format(
            c_count, l_count, r_count)
        logging.debug(mes)

        if l_count == r_count:
            return True
        elif l_count < r_count:
            return (float(l_count) / r_count) > 0.8
        elif r_count < l_count:
            return (float(r_count) / l_count) > 0.8
        else:
            return False


class RegionNotFound(Exception):

    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return AlignSymmetry(config, environ)
