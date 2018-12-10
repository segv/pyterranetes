from p10s.values import value


class BaseContext():
    def __init__(self, input=None, output=None, data=None):
        if data is None:
            self.data = {}
        else:
            self.data = data

        if input is None:
            self.input = value('p10s', {}).get('file', None)
        else:
            self.input = input

        self.output = output

    def render(self):
        raise NotImplementedError()
