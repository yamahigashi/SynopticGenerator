""" coding: utf-8 """

import imp
import os
import logging


##############################################################################
_moduleFactories = {}  # type: Dict[str, module]


def reload_module():
    pass


def load_module(module_name, plugin_base_path=[]):
    if module_name in _moduleFactories:
        return _moduleFactories[module_name]

    basepath, name = module_name.rsplit(".", 1)
    basepath = basepath.replace(".", "/")

    plugin_path = [os.path.join(dirname, basepath) for dirname
                   in plugin_base_path]

    modinfo = imp.find_module(name, plugin_path)
    mod = imp.load_module(name, *modinfo)
    _moduleFactories[module_name] = mod

    return mod


def ensure_folder(filename):
    if "/" not in filename and "\\" not in filename:
        return

    dname = os.path.dirname(filename)
    if not os.path.exists(dname):
        logging.info("make folder {}".format(dname))
        os.mkdir(dname)


class Color(object):
    has_alpha = property(doc='has alpha')

    def __init__(self, *value):
        self.r = value[0]
        self.g = value[1]
        self.b = value[2]
        self.a = value[3] if len(value) is 4 else 255

    def __repr__(self):
        return (self.r, self.g, self.b, self.a)

    def __str__(self):
        return "({self.r}, {self.g}, {self.b}, {self.a})".format(self=self)

    def __getitem__(self, k):
        if k == 0:
            return self.r
        elif k == 1:
            return self.g
        elif k == 2:
            return self.b
        elif k == 3:
            return self.a
        else:
            raise IndexError()

    @has_alpha.getter
    def has_alpha(self):
        return self.a is not 255

    def get_gbr(self):
        return (self.b, self.g, self.r, self.a)


def color(string, color_table=None):
    ''' parse string, return color (r, g, b) tuple.

    Arguments:
        string -- string, represent color
        color_table -- (optional) dict {'color_name': string("r, g, b")}

    Returns: tuple (int, int, int)
    '''

    if color_table and string in color_table:
        return color(color_table[string])

    import argparse
    s = string.split(',')
    if len(s) is not 3 and len(s) is not 4:
        mes = "%r is not valid color or not in color table, 'r, g, b, (a optional)'" % string
        raise argparse.ArgumentTypeError(mes)

    def check_range(v):
        if v < 0 or 255 < v:
            mes = "%r is not valid color, 'r, g, b'" % string
            raise argparse.ArgumentTypeError(mes)

    r = int(s[0])
    g = int(s[1])
    b = int(s[2])
    a = int(s[3]) if len(s) is 4 else 255
    check_range(r)
    check_range(g)
    check_range(b)
    check_range(a)

    return Color(r, g, b, a)


def is_opencv_version_below_2():
    import cv2
    return int(cv2.__version__.split('.')[0]) <= 2


def get_x_center(env):
    # type: (Dict) -> float

    width = env.get("width")
    if not width:
        # TODO
        raise

    x_center = env.get("x_center")
    if not x_center:
        x_center = width / 2

    return x_center


def get_distance_from_cog(env, point):
    # type: (Dict, shape.Vec2) -> float
    """ get distance from center of background """

    x = get_x_center(env)
    y = env.get("height") / 2.0

    return abs(x - point[0]) + abs(y - point[1])


def is_point_inside_central_region(env, point):
    # type: (Dict, shape.Vec2) -> bool

    width = env.get('width')
    if not width:
        return False

    x_center = get_x_center(env)

    margin_rate = 0.10
    margin = width * (margin_rate / 2)
    min = x_center - margin
    max = x_center + margin

    if point.x < min:
        return False
    elif max < point.x:
        return False

    return True


def is_point_inside_lower_region(env, point, margin_rate=0.25):
    # type: (Dict, shape.Vec2, float) -> bool

    height = env.get('height')
    if not height:
        return False

    min = height * (1 - margin_rate)
    max = height

    if point.y < min:
        return False
    elif max < point.y:
        return False

    return True


def is_point_inside_upper_region(env, point, margin_rate=0.25):
    # type: (Dict, shape.Vec2, float) -> bool

    height = env.get('height')
    if not height:
        return False

    min = 0
    max = height * margin_rate

    if point.y < min:
        return False
    elif max < point.y:
        return False

    return True
