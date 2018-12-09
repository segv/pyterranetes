from pathlib import Path
from p10s.utils import merge_dicts
from p10s.loads import load_file


class Values():
    def __init__(self, values):
        self.values = values

    @classmethod
    def from_files(cls, basedir):
        basedir = Path(basedir)
        if not basedir.exists():
            raise Exception("basedir {} does not exist" % basedir)
        root = basedir.resolve().root
        here = basedir

        values_files = []

        while str(here) != root:
            if (here / 'values.yaml').exists():
                values_files.insert(0, here / 'values.yaml')
            here = here.parent

        values = {}
        for file in values_files:
            merge_dicts(values, load_file(file))

        return cls(values)
