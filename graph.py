from collections import namedtuple, defaultdict

connection = namedtuple('connection', 'from_ to')

class DirectedGraph:
    def __init__(self, cd=None):
        if cd is None:
            self.cd = defaultdict(set)      # Connections dictionary
        else:
            self.cd = defaultdict(set, cd)

    def __str__(self):
        return f'DirectedGraph({dict(self.cd)})'

    def add_conn(self, a, b):
        self.cd[a].add(b)

    def get_conns(self, a):
        return self.cd[a]

    def union(self, other):
        keys = set(self.cd.keys()).union(set(other.cd.keys()))
        return DirectedGraph({k: self.cd[k].union(other.cd[k]) for k in keys})

    @staticmethod
    def from_list_of_lists(ll):
        g = DirectedGraph()
        for l in ll:
            for a, b in zip(l, l[1:]):
                g.add_conn(a, b)
        return g
