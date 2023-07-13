from collections import defaultdict
import itertools as it
cfi = it.chain.from_iterable
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
            yield from filter(lambda s: s is not self, pcd[p])
    def get_connected_pins(self, p) -> list:
        return NotImplemented
    def propagate_current(self, *Is) -> list:
        return NotImplemented
    @classmethod
    def get_component(klass, sid):
        return klass.register[sid]
    @classmethod
    def get_sources(klass):
        for v in klass.register.values():
            if type(v) is terminal and v.voltage > 0:
                yield v.p1
    @staticmethod
    def get_terminal_voltage(node):
        try:
            return next(filter(lambda c: type(c) is terminal, pcd[node])).voltage
        except StopIteration:
            return None

class terminal(component):     # voltage
    def get_connected_pins(self, p):
        #if p == 'start':
        return [self.p1]
        #return []
    def propagate_current(self, i):
        return [1]

class wire(component):
    def get_connected_pins(self, p):
        if p == self.p1: return [self.p2]
        else: return [self.p1]
    def propagate_current(self, i1, i2):
        if i1 == 0: return [i2, i2]
        else: return [i1, i1]

class diode(wire):
    def get_connected_pins(self, p):
        if p == self.p1: return [self.p2]
        else: return []
    def propagate_current(self, i1, i2):
        return [i1, i1]

class transistor(component):
    def get_connected_pins(self, p):
        if p == self.p1 or p == self.p2: return [self.p3]
        else: return []
    def propagate_current(self, i1, i2, i3):
        if i2 == 1:
            return [i1, i2, i1]

class button(wire):      # TODO
    pass

class resistor(wire):          # resistance
    pass

class lamp(wire):
    def propagate_current(self, i1, i2):
        r = super().propagate_current(i1, i2)
        if r[0]:
            print('light on')
        return r

def get_all_paths(pin, history=[]):
    new_history = history + [pin]
    if component.get_terminal_voltage(pin) == 0 or component in history[:-1]:
        return [new_history]
    return cfi(get_all_paths(p, new_history) for p in cfi(c.get_connected_pins(pin) for c in pcd[pin]) if p not in new_history[-2:])

from pprint import pprint

terminal(0, voltage=1)
terminal(1, voltage=1)
terminal(2, voltage=5)
transistor(2, 0, 3)
transistor(3, 1, 4)
lamp(4, 5)
resistor(5, 6)
terminal(6, voltage=0)

#print(list(component.get_sources()))
#print(list(get_all_paths(0)))
#print(component.get_terminal_voltage(3))
#print(pcd)
#print(list(component.get_component(4).get_connections()))
#pprint(list(get_all_paths(0)))
print(list(cfi(map(get_all_paths, component.get_sources()))))
