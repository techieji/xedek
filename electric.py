from collections import defaultdict, deque
import itertools as it
cfi = it.chain.from_iterable
import time
from graph import DirectedGraph
from functools import reduce

RUNNING = False

class component:
    '''Superclass of all electrical components.

    Takes an arbitrary number of pins and attributes and turns it into an easily
    accessible form. Example:

       >>> c = component(1, 4, 7, radius=2)
       >>> c.p1, c.p2, c.p3
       (1, 4, 7)
       >>> c.radius
       2
    '''
    # Class attrs are set in component.reset_class
    def __init__(self, *ps, **attrs):
        self.sid = component.sid      # TODO investigate whether the sid is going up after resets
        self.ps = ps
        self.attrs = attrs
        self.fec = None
        component.sid += 1
        component.register[self.sid] = self
        for p in ps: component.pcd[p].add(self)
        for _i, v in enumerate(ps):
            i = _i + 1
            setattr(self, f'p{i}', v)
            setattr(self, f'v{i}', property(lambda self, name=f'p{i}': components.pct[getattr(self, name)]))
        self.on = False
        for k, v in attrs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f'{type(self).__name__}({" ".join(map(str, self.ps))} | {str(self.attrs)})'

    def get_connections(self):
        '''Gets all connected components.

        Gets all neighboring components to the current component. Example:

           >>> c1 = component(1, 2)
           >>> c2 = component(2, 3)
           >>> c3 = component(3, 4)
           >>> a, b = c2.get_connections()
           >>> assert a is c1 and b is c2
        '''
        for p in self.ps:
            yield from filter(lambda s: s is not self, component.pcd[p])

    def get_connected_pins(self, p) -> list:
        '''Gets the pins connected to the current pin and are part of this component. Example:

            >>> t = transistor(1, 2, 3)
            >>> t.get_connected_pins(1)
            [3]
            >>> t.get_connected_pins(2)
            [3]
            >>> t.get_connected_pins(3)
            []

        Should be overridden in subclasses.
        '''
        raise NotImplementedError

    def propagate_current(self, *Is) -> list:
        '''Determines which pins current will flow through given the current flowing into
        certain pins. Example:

            >>> t = transistor(1, 2, 3)
            >>> t.propagate_current(1, 1, 0)
            [1, 1, 1]
            >>> t.propagate_current(1, 0, 0)
            [1, 0, 0]

        Should be overridden in subclasses.
        '''
        raise NotImplementedError

    def _propagate_current(self):
        # Automatically called propagate_current using currents from pct
        # Regular propagate current, but it also updates pct
        cl = self.propagate_current(*map(component.pct.get, self.ps))
        for p, c in zip(self.ps, cl):
            component.pct[p] = c

    @classmethod
    def get_component(klass, sid):       # TODO: change classmethod to staticmethod
        '''Looks up a component in the register based on the given ID. Example:

            >>> w = wire(0, 1)
            >>> c = component.get_component(1)
            >>> c is w
            True
        '''
        return klass.register[sid]
    
    @classmethod
    def get_sources(klass):
        '''Gets the pin locations of all positive terminals. Example:

            >>> t = terminal(0, voltage=5)
            >>> w = wire(0, 2)
            >>> list(component.get_sources())
            [0]
        '''
        for v in klass.register.values():
            if type(v) is terminal and v.voltage > 0:
                yield v.p1
    
    @classmethod
    def reset_class(klass):
        '''Resets all class attributes'''
        assert klass is component
        klass.sid = 1
        klass.register = {}
        klass.pcd = defaultdict(lambda: set())    # Pin component dictionary
        klass.pct = defaultdict(lambda: 0)        # Pin current table
        lamp.lamp_sid = 1
    
    @staticmethod
    def get_terminal_voltage(node):
        '''Returns the voltage of the terminal at the given pin if such a terminal exists.
            Example:

            >>> t = terminal(0, voltage = 5)
            >>> v = component.get_terminal_voltage(0)
            >>> v
            5
        '''

        try:
            return next(filter(lambda c: type(c) is terminal, component.pcd[node])).voltage
        except StopIteration:
            return None

class terminal(component):     # voltage
    '''Class for both positive terminals and ground.'''
        
    def get_connected_pins(self, p):
        #if p == 'start':
        return [self.p1]
        #return []
    
    def propagate_current(self, i):
        return [1]

class wire(component):
    '''Class for wires, which allow current to flow from one point to another.'''

    def get_connected_pins(self, p):
        if p == self.p1: return [self.p2]
        else: return [self.p1]
    
    def propagate_current(self, i1, i2):
        if i1 == 0: return [i2, i2]
        else: return [i1, i1]

class diode(wire):
    '''Class for diodes, which act like one-directional wires.'''

    def get_connected_pins(self, p):
        if p == self.p1: return [self.p2]
        else: return []
    
    def propagate_current(self, i1, i2):
        return [i1, i1]

class transistor(component):
    '''Class for transistors, which allow current to flow from the collector to the emitter 
    and from the base to the emitter if the base is in contact with positive current.

        >>> t = transistor(1, 2, 3)
    
    1 is the collector, 2 is the base, 3 is the emitter.
    '''

    def get_connected_pins(self, p):
        if RUNNING:
            match p:
                case self.p1:
                    return [self.p3] if self.v2 else []
                case self.p2:
                    return [self.p3]
                case self.p3:
                    return []
        if p == self.p1 or p == self.p2: return [self.p3]
        else: return []
    
    def propagate_current(self, i1, i2, i3):
        if i2 == 1:
            return [i1, i2, i1]
        return [i1, i2, i3]

class button(wire):      # TODO TODO get_connected_pins conditional on button press
    '''Class for buttons, which behave like wires when pressed but do not let current flow through
    otherwise.'''
    pass

class resistor(wire):          # resistance
    '''Class for resistors, which behave like wires but create a resistance to weaken the current.'''
    pass

class lamp(wire):      # FIXME: source and dest are same pin? Fix issue.
    lamp_sid = 1
    '''Class for lamps, which behave like resistors but also emit light when current flows through.'''
    def __init__(self, *ps, **kwargs):
        super().__init__(*ps, **kwargs)
        self.lamp_sid = lamp.lamp_sid
        lamp.lamp_sid += 1
        self.on = False
    def propagate_current(self, i1, i2):
        r = super().propagate_current(i1, i2)
        if r[0] and not self.on:
            # print(f'light {self.lamp_sid} on')
            self.on = True
        elif not r[0] and self.on:
            # print(f'light {self.lamp_sid} off')
            self.on = False
        return r

component.reset_class()

def _get_all_paths(pin, history=[]):
    '''Returns lists of all paths that positive current could travel through, going from a positive 
    terminal to the ground. Example:

        >>> t1 = terminal(0, voltage=5)
        >>> w = wire(0, 2)
        >>> l = lamp(2, 3)
        >>> t2 = terminal(3, voltage=5)
        >>> get_all_paths(0)
        [[0, 2, 3]]

    '''
    new_history = history + [pin]
    if component.get_terminal_voltage(pin) == 0 or component in history[:-1]:
        return [new_history]
    return cfi(_get_all_paths(p, new_history) for p in cfi(c.get_connected_pins(pin) for c in component.pcd[pin]) if p not in new_history)

def get_all_paths(pin):
    return DirectedGraph.from_list_of_lists(_get_all_paths(pin))

def get_all_paths_from_positive():
    return reduce(DirectedGraph.union, map(get_all_paths, component.get_sources()))

def detect_shorts(dg):     # TODO: finish
    pass

def propagate_current_at_pin(pin, paths):
    cl = component.pcd[pin]
    for c in cl:
        pl = c.get_connected_pins(pin)
        # print(pin, pl, paths.get_conns(pin))
        if set(pl).issubset(paths.get_conns(pin)) or type(c) is terminal:
            c._propagate_current()

def propagate_current_step(paths: DirectedGraph):
    for p in component.pcd.keys():
        propagate_current_at_pin(p, paths)

def propagate_current(paths: DirectedGraph):
    while True:
        propagate_current_step(paths)

def main():
    global RUNNING
    terminal(0, voltage=5)
    wire(0, 1)
    lamp(1, 2)
    wire(2, 3)
    wire(1, 3)
    wire(3, 4)
    terminal(4, voltage=0)

    print('start')
    p = get_all_paths_from_positive()
    print('running')
    RUNNING = True
    propagate_current(p)
    print('end')

if __name__ == '__main__':
    main()
