from functools import total_ordering

@total_ordering
class State:
    """ State class for Astar algorithm
    ordered by F = G + H
    link to par backtrace
    """

    def __init__(self, t, pos, G, H, par):
        self.t = t
        self.pos = pos
        self.G = G
        self.F = G + H
        self.par = par # State or None
        
    def __lt__(self, other):
        return self.F < other.F
    
    def backtrace(self):
        bt = []
        x = self
        while x is not None:
            bt.append(x.pos)
            x = x.par
        return bt[::-1]


