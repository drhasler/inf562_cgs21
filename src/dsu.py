import numpy as np
from collections import defaultdict

class DSU:
    """ Disjoint Set Union """
    def __init__(self, n):
        self.dsu = [-1] * n
    
    def find(self, x):
        if self.dsu[x] < 0: return x
        self.dsu[x] = self.find(self.dsu[x])
        return self.dsu[x]
    
    def merge(self, x, y):
        # make x parent of y
        x,y = self.find(x), self.find(y)
        if x == y: return
        self.dsu[x] += self.dsu[y]
        self.dsu[y] = x 

    def get_groups(self):
        n = len(self.dsu)
        D = defaultdict(list)
        for i in range(n):
            p = self.find(i)
            D[p].append(i)
        return D
