""" coding: utf-8 """

import os
import re
import glob

from synopticgenerator.plugins import Pipeline
import synopticgenerator.plugins.image.paste_with_transparent as paste_with_transparent
import synopticgenerator.plugins.utility.copy_file as copy_file


class ConcatImages(Pipeline):

    place_holder_controller_name = "controller_name"

    def set_default_config(self):
        # type: () -> None

        self.config.setdefault("image_pattern", None)
        self.config.setdefault("output_path", None)

    def check_config(self):
        # type: () -> None

        if not self.config.get("image_pattern"):
            raise Pipeline.ConfigInvalid("image_pattern")

    def execute(self, content):
        glob_pat = self.config["image_pattern"]
        glob_pat = re.sub("{{\ *" + self.place_holder_controller_name + "\ *}}", "*", glob_pat)

        ctrl_pat = os.path.basename(self.config["image_pattern"])
        ctrl_pat = re.sub("{{\ *" + self.place_holder_controller_name + "\ *}}", "(\w+)", ctrl_pat)
        # ctrl_expr = re.compile(ctrl_pat)

        output_path = self.config.get("output_path")
        files = glob.glob(glob_pat)
        conf = {"src": files[0], "dst": output_path}
        copy_module = copy_file.create(conf, self.environ)
        content = copy_module.execute(content)

        for src_image in files:
            conf = {
                'base': src_image,
                'paste': self.config.get("output_path"),
                'output': self.config.get("output_path")
            }

            paste_module = paste_with_transparent.create(conf, self.environ)
            content = paste_module.execute(content)

        return content


def create(config, environ):
    return ConcatImages(config, environ)
