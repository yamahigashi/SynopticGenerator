""" coding: utf-8 """
from synopticgenerator.plugins import Pipeline


class DumpRegion(Pipeline):
    ''' manipulate HTML charcter '''

    def set_default_config(self):
        # type: () -> None

        self.controls = self.config.setdefault("controls", None)
        self.region = self.config.setdefault("region_name", "regions")

    def execute(self, content):
        if not content.get(self.region):
            raise Pipeline.RegionNotFound(self.region)

        ctrls = self.controls or content[self.region]
        for x in ctrls:
            print('name: {} shape: "{}", center: "{}", color: "{}"'.format(
                x.name, x.__class__.__name__, str(x.center), str(x.color)))

        return content


def create(config, environ):
    return DumpRegion(config, environ)
