""" coding: utf-8 """

import os
import io
import tempfile
import shutil

from PIL import Image

import synopticgenerator.util as util
from synopticgenerator import Pipeline


class Transparenter(Pipeline):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.color_table = environ.setdefault("color_table", None)

    def execute(self, content):
        input_file = self.config["input"]
        color = util.color(self.config["color"], self.color_table)
        res = transparent(input_file, color)
        shutil.copyfile(res, self.config["output"])
        shutil.rmtree(os.path.dirname(res))

        return content


def transparent(f, color=util.color("255, 255, 255")):
    """ 指定パス画像の指定カラー部分透明にする """

    if isinstance(f, io.IOBase):
        file_path = f.name
    elif isinstance(f, str):
        file_path = f

    img = Image.open(file_path)
    img = img.convert("RGBA")

    r = color.r
    g = color.g
    b = color.b
    newData = []
    for item in img.getdata():
        if item[0] == r and item[1] == g and item[2] == b:
            newData.append((r, g, b, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    tmpdir = tempfile.mkdtemp()
    f_name = os.path.basename(file_path)
    output_path = os.path.join(tmpdir, os.path.splitext(f_name)[0]) + ".png"
    img.save(output_path, "PNG")
    return output_path


def create(config, environ):
    return Transparenter(config, environ)


if __name__ == "__main__":
    import argparse

    recognizer = argparse.ArgumentParser()
    recognizer.add_argument(
        "-i", "--input", dest="input_file",
        help="input file", metavar="FILE", type=file)
    recognizer.add_argument(
        "-c", "--color",
        dest="color", default="255, 255, 255", type=util.color,
        help="don't print status messages to stdout")

    args = recognizer.parse_args()
    path = transparent(args.input_file, args.color)
    print(path)
