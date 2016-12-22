""" coding: utf-8 """
from synopticgenerator.plugins import Pipeline


class ObjectDrawer(Pipeline):

    # def __init__(self, config, image):
    def __init__(self, config, env):
        super(ObjectDrawer, self).__init__(config, {})
        # self.canvas = image
