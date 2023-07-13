from collections import defaultdict
import itertools as it
cfi = it.chain.from_iterable
import time

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
        self.sid = component.sid
        self.ps = ps
        self.attrs = attrs
        component.sid += 1
        component.register[self.sid] = self
        for p in ps: component.pcd[p].add(self)
        for _i, v in enumerate(ps):
            i = _i + 1
            setattr(self, f'p{i}', v)
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
        return NotImplemented

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
        return NotImplemented

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
        klass.pvt = defaultdict(lambda: 0)        # Pin voltage table
    
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

component.reset_class()

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
        if p == self.p1 or p == self.p2: return [self.p3]
        else: return []
    
    def propagate_current(self, i1, i2, i3):
        if i2 == 1:
            return [i1, i2, i1]

class button(wire):      # TODO
    '''Class for buttons, which behave like wires when pressed but do not let current flow through
    otherwise.'''
    pass

class resistor(wire):          # resistance
    '''Class for resistors, which behave like wires but create a resistance to weaken the current.'''
    pass

class lamp(wire):
    '''Class for lamps, which behave like resistors but also emit light when current flows through.'''
    def propagate_current(self, i1, i2):
        r = super().propagate_current(i1, i2)
        if r[0]:
            print('light on')
        return r

def get_all_paths(pin, history=[]):
    '''Returns lists of all paths that positive current could travel through, going from a positive 
    terminal to the ground. ADD EXAMPLE'''
    new_history = history + [pin]
    if component.get_terminal_voltage(pin) == 0 or component in history[:-1]:
        return [new_history]
    return cfi(get_all_paths(p, new_history) for p in cfi(c.get_connected_pins(pin) for c in component.pcd[pin]) if p not in new_history[-2:])

def main():
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
    #print(component.pcd)
    #print(list(component.get_component(4).get_connections()))
    #pprint(list(get_all_paths(0)))
    print(list(cfi(map(get_all_paths, component.get_sources()))))

if __name__ == '__main__':
    main()
