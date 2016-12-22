""" coding: utf-8 """
import re
import logging

from synopticgenerator.plugins import Pipeline


class MirrorRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)
        self.config.setdefault("skip_duplicate", True)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        location_expression = self.environ.get("location_expression")
        location_labels = self.environ.get("location_label")
        ll = location_labels.get("left")
        rl = location_labels.get("right")
        cl = location_labels.get("center")

        loc_expr = re.sub(
            "{{\s+location\s+}}",
            "(?P<location_label>({}|{}))".format(ll, rl, cl),
            location_expression)

        loc_expr = "(.*){}(.*)".format(loc_expr)
        expr = re.compile(loc_expr)

        def repl(match_obj):

            s = list(match_obj.string)
            start = match_obj.start("location_label")
            end = match_obj.end("location_label")

            for i in range(start, end):
                s[i] = ""

            if match_obj.group("location_label") == ll:
                s.insert(start, rl)
            elif match_obj.group("location_label") == rl:
                s.insert(start, ll)
            else:
                msg = "location label does not match any string for {}".format(match_obj.string)
                logging.warn(msg)

            return "".join(s)

        ctrls = self.controls or content[self.region]
        names = [x.name for x in ctrls]
        new_shapes = []

        for ctrl in ctrls:
            new_name = expr.sub(repl, ctrl.name)

            if new_name in names:
                if self.config.get("skip_duplicate"):
                    msg = "mirror region: skip new name {} (for {}) already exists".format(new_name, ctrl.name)
                    logging.info(msg)

                    continue

            new_shape = ctrl.copy_mirror(self.environ, new_name)
            new_shapes.append(new_shape)

        ctrls.extend(new_shapes)

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return MirrorRegion(config, environ)
