""" coding: utf-8 """
from synopticgenerator.plugins import Pipeline


class ObjectDrawer(Pipeline):

    def __init__(self, config, image):
        self.canvas = image
