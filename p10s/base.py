from p10s.values import value
from p10s.utils import merge_dicts


class BaseContext():
    def __init__(self, input=None, output=None):
        if input is None:
            self.input = value('p10s', {}).get('file', None)
        else:
            self.input = input

        if output is None and self.input is not None:
            self.output = self.input.with_suffix(self.output_file_extension)
        else:
            self.output = output

    def render(self):
        raise NotImplementedError()

    def _output_stream(self):
        self.output.parent.mkdir(parents=True, exist_ok=True)
        return self.output.open("w")
