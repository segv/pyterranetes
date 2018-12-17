import sys
import os
from pathlib import Path
import runpy

from p10s.base import BaseContext
from p10s.values import values


class Output():
    def __init__(self, basedir):
        self.basedir = basedir
        self.contexts = []

    def render(self):
        pwd = os.getcwd()
        os.chdir(str(self.basedir))
        try:
            for c in self.contexts:
                c.render()
        finally:
            os.chdir(pwd)


class Generator():
    def add_pyterranetes_dir(self, root):
        here = root
        count = 0
        while True:
            maybe = here / 'pyterranetes'
            if maybe.exists() and maybe.is_dir():
                sys.path.insert(0, "%s/" % (maybe))
                break
            if str(here) == here.root:
                break
            here = here.parent

            if count > 20:
                raise Exception("Directroy tree too deep. aborting")
            count += 1

    def p10s_files(self, root):
        if root.is_file():
            yield root
        else:
            for dirname, sub_dirs, files in os.walk(str(root)):
                for file in files:
                    path = Path(file)
                    if path.suffix == '.p10s':
                        yield Path(os.path.join(dirname, file))

    def compile(self, root):
        root = Path(root).resolve()
        if root.is_file():
            basedir = root.parent
        else:
            basedir = root
        self.add_pyterranetes_dir(basedir)

        outputs = []
        for path in self.p10s_files(root):
            with values({'p10s': {'file': path}}):
                output = Output(basedir=path.parent.resolve())
                pwd = os.getcwd()
                os.chdir(str(path.parent))
                globals = runpy.run_path(str(path))
                os.chdir(pwd)
                for value in globals.values():
                    if isinstance(value, BaseContext):
                        output.contexts.append(value)
                outputs.append(output)

        return outputs

    def generate(self, root):
        for output in self.compile(root):
            output.render()
