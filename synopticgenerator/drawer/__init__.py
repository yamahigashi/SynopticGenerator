""" coding: utf-8 """

class ObjectDrawer(object):

    def __init__(self, config, image):
        self.canvas = image


def draw(config, image, bound):
    r = RectangleDrawer(config, image)
    r.draw(bound, color)
