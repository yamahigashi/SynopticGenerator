""" coding: utf-8 """

from synopticgenerator.plugins import Pipeline


class ConcatRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.a = self.config.setdefault("region_a", None)
        self.b = self.config.setdefault("region_b", None)
        self.store = self.config.setdefault("store", None)

    def check_config(self):
        # type: () -> None

        if not self.a:
            raise Pipeline.ConfigInvalid("region_a")
        if not self.b:
            raise Pipeline.ConfigInvalid("region_b")
        if not self.b:
            raise Pipeline.ConfigInvalid("store")

    def execute(self, content):
        if not content.get(self.a):
            raise Pipeline.RegionNotFound(self.a)
        if not content.get(self.b):
            raise Pipeline.RegionNotFound(self.b)

        cat = []
        cat.extend(content.get(self.a))
        cat.extend(content.get(self.b))

        content[self.store] = cat

        return content


def create(config, environ):
    return ConcatRegion(config, environ)
