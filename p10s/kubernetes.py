class KubernetesObject():
    def __init__(self):
        self.data = {}

    def render(self):
        if 'kind' not in self.data:
            self.data['kind'] = self.KIND
        return self.data


class Deployment(KubernetesObject):
    KIND = 'Deployment'


class ConfigMap(KubernetesObject):
    KIND = 'ConfigMap'


class Service(KubernetesObject):
    KIND = 'Service'
