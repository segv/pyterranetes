import hcl as pyhcl


class Terraform():
    def __init__(self, output=None):
        self.output = output
        self.data = {}

    def _merge_in(self, values):
        def rec(a, b):
            for k in b.keys():
                new = b[k]
                if isinstance(new, dict):
                    existing = a.get(k, a)
                    if existing is a:
                        a[k] = new
                    else:
                        if isinstance(existing, dict):
                            rec(existing, new)
                        else:
                            a[k] = new
                else:
                    a[k] = new

        rec(self.data, values)

        return self

    def resource(self, type, name, block):
        self._merge_in({'resource': {type: {name: block}}})

    def data(self, type, name, block):
        self._merge_in({'data': {type: {name: block}}})

    def provider(self, name, block):
        self._merge_in({'provider': {name: block}})

    def module(self, name, block):
        self._merge_in({'module': {name: block}})

    def terraform(self, block):
        self._merge_in({'terraform': block})

    def variable(self, name, type=None, default=None, description=None):
        self._merge_in({'variable': {name: {}}})
        if type is not None:
            self._merge_in({'variable': {name: {'type': type}}})
        if default is not None:
            self._merge_in({'variable': {name: {'default': default}}})
        if description is not None:
            self._merge_in({'variable': {name: {'description': description}}})

    def output(self, name, value=None, description=None, depends_on=None, sensitive=None):
        self._merge_in({'output': {name: {}}})
        if value is not None:
            self._merge_in({'variable': {name: {'value': value}}})
        if description is not None:
            self._merge_in({'variable': {name: {'description': description}}})
        if depends_on is not None:
            self._merge_in({'variable': {name: {'depends_on': depends_on}}})
        if sensitive is not None:
            self._merge_in({'variable': {name: {'sensitive': sensitive}}})

    def local(self, name, block):
        self._merge_in({'locals': {name: block}})

    def hcl(self, hcl):
        self._merge_in(pyhcl.loads(hcl))
