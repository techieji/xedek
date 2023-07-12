from collections import defaultdict
import time

pcd = defaultdict(lambda: set())    # Pin component dictionary
pvt = defaultdict(lambda: 0)        # Pin voltage table

class component:
    sid = 1
    register = {}
    def __init__(self, *ps, **attrs):
        self.sid = component.sid
        self.ps = ps
        self.attrs = attrs
        component.sid += 1
        component.register[self.sid] = self
        for p in ps: pcd[p].add(self)
        for _i, v in enumerate(ps):
            i = _i + 1
            setattr(self, f'p{i}', v)
        self.on = False
        for k, v in attrs.items():
            setattr(self, k, v)
    def __repr__(self):
        return f'{type(self).__name__}({" ".join(map(str, self.ps))} | {str(self.attrs)})'
    def get_connections(self):
        for p in self.ps:
            yield from pcd[p]
    @classmethod
    def get_component(klass, sid):
        return klass.register[sid]

class terminal(component):     # voltage
    pass

class wire(component):
    pass

class resistor(wire):          # resistance
    pass

class lamp(wire):
    pass

def get_all_paths(component, history=[]):
    new_history = history + [component]
    if type(component) is terminal and component.voltage == 0:
        return [new_history]
    return sum((get_all_paths(c, new_history) for c in component.get_connections() if c not in new_history), [])

from pprint import pprint

terminal(0, voltage=5)
wire(0, 1)
wire(0, 2)
wire(1, 3)
wire(2, 3)
terminal(3, voltage=0)

pprint(get_all_paths(component.get_component(1)))