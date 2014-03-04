""" coding: utf-8 """

import os
import shutil
import tempfile
from PIL import Image


def paste(image1, image2):
    """ 2枚のイメージを合成する """

    if isinstance(image1, file):
        image1_file_path = image1.name
    elif isinstance(image1, str):
        image1_file_path = image1

    if isinstance(image2, file):
        image2_file_path = image2.name
    elif isinstance(image2, str):
        image2_file_path = image2

    img2 = Image.open(image1_file_path)
    img = Image.open(image2_file_path)
    img2.paste(img, (0, 0), img.split()[3])

    tmpdir = tempfile.mkdtemp()
    f_name = os.path.basename(image1_file_path)
    output_path = os.path.join(tmpdir, os.path.splitext(f_name)[0]) + ".png"
    img2.save(output_path, "PNG")
    return output_path


class Paster(object):
    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

    def execute(self, content):
        image1 = self.config["base"]
        image2 = self.config["paste"]
        res = paste(image1, image2)
        shutil.copyfile(res, self.config["output"])
        shutil.rmtree(os.path.dirname(res))

        return content


def create(config, environ):
    return Paster(config, environ)


if __name__ == "__main__":
    import argparse
    recognizer = argparse.ArgumentParser()
    recognizer.add_argument(
        "-a", "--image1", image2="image1",
        help="image1 image", metavar="FILE", type=file)
    recognizer.add_argument(
        "-b", "--image2", image2="image2",
        help="image2 image", metavar="FILE", type=file)

    args = recognizer.parse_args()
    path = paste(args.image1, args.image2)
    print path
