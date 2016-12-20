""" coding: utf-8 """
from synopticgenerator import Pipeline


class ObjectDrawer(Pipeline):

    def __init__(self, config, image):
        self.canvas = image
