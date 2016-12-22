""" coding: utf-8 """
from synopticgenerator.plugins import Pipeline


class UniqRegion(Pipeline):

    def set_default_config(self):
        # type: () -> None

        self.region = self.config.setdefault("region_name", "regions")
        self.controls = self.config.setdefault("controls", None)

    def execute(self, content):
        if not content.get(self.region):
            raise RegionNotFound(self.region)

        ctrls = self.controls or content[self.region]

        seen = set()
        seen_add = seen.add
        uniq = [x for x in ctrls
                if x.center not in seen and not seen_add(x.center)]

        if self.controls:
            # TODO
            self.controls = uniq

        else:
            content[self.region] = uniq

        return content


class RegionNotFound(Exception):
    def str(self, v):
        return "Region named {} not found in content".format(v)


def create(config, environ):
    return UniqRegion(config, environ)
