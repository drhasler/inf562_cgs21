from .util import *
from .grid_proc import *

from .history import History
from .dsu import DSU
from .astar import State
from .precedence import PrecedenceGraph

from tqdm import tqdm # progress bar
from heapq import heappop, heappush
from collections import deque
from copy import deepcopy

import numpy as np

class OrderedSolver:
    def __init__(self, src, dst, obs):
        """ Ordered Solver
        finds legal paths from src to dst
        
        attrs
        hist: (i,j)->[(t,bot)] events ordered, (t,-1) when freed
        obs: obstacles
        src, dst: [(i,j)] for each bot
        """
        self.hist = History(src)
        self.obs = set( obs )
        self.src = src
        self.dst = dst
        
    def solve(self, it):
        """ solve by finding path for bots
        successively (ordered by it) """
        
        todo = []
        for bot in tqdm(it): # permutation(n): all bots
            try:
                st = self.move(bot, self.src[bot], self.dst[bot])
                bt = st.backtrace()
                self.hist.record_backtrace(bt, bot)
            except:
                todo.append(bot)
                if len(todo) > 20:
                    raise Exception
        for bot in todo: # ofc this makes sense
            st = self.move(bot, self.src[bot], self.dst[bot])
            bt = st.backtrace()
            self.hist.record_backtrace(bt, bot)
        # will raise if fail

    def move(self, bot, src, dst, maxt=100):
        """ tries to find a path for bot from src to dst
        returns State( for backtrace )
        raises if fails """

        def bake(t,pos,st=None):
            H = 1.001 * l1(pos, dst)
            G = t
            return State(t,pos,G,H,st)

        pq = [ bake(0, src) ]
        poss = self.hist.possible
        can_stay = self.hist.can_stay

        mem = set() # memoize visited states
        while pq:
            st = heappop(pq)
            x = st.pos
            t = st.t

            if t > maxt:
                print(src, dst, bot)
                raise Exception
            if x == dst and can_stay(t,x):
                return st
            if x == src: # only wait at src, to reduce nb of states
                ot = bake(t+1,x,st)
                heappush(pq,ot)

            for y in nb(*x):
                if (t+1,y) not in mem and y not in self.obs and poss(t+1,x,y):
                    mem.add((t+1,y))
                    ot = bake(t+1,y,st)
                    heappush(pq,ot)

        raise Exception


class TWSolver:
    """ solver for total work """

    def __init__(self, src, dst, obs):
        ...

    def solve(self):
        raise NotImplementedError
        PG = PrecedenceGraph(self.src, self.dst)

        for bots, is_cycle in PG.groups:
            if is_cycle:
                n = len(bots)
                if n == 1: continue # static
                p = [ path(d1[bot], d2[bot]) for bot in c ]
                for i in range(n):
                    U = set(p[i-1]) | set(p[(i+1) % n])
                    if len( set(p[i]) - U ):
                        # i goto x, pre[i] freed
                        # simple path (suc[i] > ... > pre[i])
                        # i goto dst
                        ...
                else: # not found
                    # someone get out of path
                    # simple path
                    # close cycle
                    ...
            else: # simple path
                for b in bots:
                    move( self.src[b], self.dst[b] )


class HighwaySolver:

    def __init__(self, src, dst, obs, Mhw):
        self.obs = set(obs) | set(src) | set(dst)
        self.src = src
        self.dst = dst
        self.hist = None # need to call solve
        
        self.Mhw = Mhw
        self.inb = inbounds(*Mhw.shape[:2])

    def find_path(self, src, dst):
        """ returns a path from src to dst """

        def cost(x,y): # x to y
            (i,j),(I,J) = x,y
            if not self.inb(*y): return 2
            d = (2 + (J<j)) if i==I else (0 + (i<I))
            return self.Mhw[y+(d,)]

        def bake(t,pos,G, st=None):
            (i,j),(x,y) = pos,dst
            H = 1.001 * l1(pos,dst)
            return State(t,pos,G,H,st)

        pq = [ bake(0,src,0) ]

        mem = { src: 0 } # memoize visited states
        while pq:
            st = heappop(pq)
            x = st.pos
            t = st.t
            if mem[x] < st.G: continue

            if l1(x,dst) == 1:
                ot = bake(t+1,dst,0,st)
                return ot.backtrace()
            for y in nb(*x):
                G = st.G + cost(x,y)
                if G < mem.get(y, 1000000) and not y in self.obs:
                    mem[y] = G
                    ot = bake(t+1,y,G,st)
                    heappush(pq,ot)
        raise Exception

    def find_paths(self):
        """ returns moves for every bot """
        n = len(self.src)
        moves = [ None ] * n
        for i in tqdm(range(n)):
            s = self.src[i]
            d = self.dst[i]
            p = self.find_path(s,d)[:0:-1] # stack + popfront
            moves[i] = p
        return moves

    def solve(self, th=.1, moves=None):
        """ pray that everything doesnt crash
        sending groups simultaneously to avoid blocking
        """

        self.hist = History(self.src)
        
        n = len(self.src)
        pos = self.src.copy()

        PG = PrecedenceGraph(self.src, self.dst)
        todo = PG.groups

        np.random.shuffle(todo)

        if moves is None: moves = self.find_paths()
        else: moves = deepcopy(moves)

        def add_to_alive():
            nonlocal alive
            # TODO better heuristic pls
            while len(alive) < th*n and len(todo):
                bots, is_cycle = todo.pop()
                if len(bots) == 1 and not moves[bots[0]]: continue
                alive += bots
            assert( len(alive) == len(set(alive)) )

        poss = self.hist.possible
        rec = self.hist.record_one
        
        ok,tw = 0,0
        _otw = -1
        alive,torem = [],[]
        for t in range(1,100000):
            if tw == _otw:
                # TODO perturbate / recompute paths
                raise Exception('infinite loop')
            _otw = tw
            if t % 1000 == 0:
                print(ok,len(alive),n, tw)
            for bot in torem:
                alive.remove(bot)
            torem = []
            add_to_alive() # will add moves for each bot

            if not todo and not alive: break
            for bot in alive: # TODO priority
                # print(bot, pos[bot], self.src[bot], self.dst[bot])
                x = pos[bot]
                y = moves[bot][-1]
                if poss(t,x,y, bot):
                    moves[bot].pop()
                    pos[bot] = y
                    rec(t,x,y, bot)
                    tw += 1
                    if not moves[bot]:
                        torem.append(bot)
                        ok += 1
                elif y == self.dst[bot] and self.src[bot] != x:
                    print(self.src[bot], self.dst[bot])
                    raise Exception('destination occupied')
        else: raise Exception('too many iterations')
        
        return tw,t

class Solver1:
    """ Solver1
    snap to storage: starts -> d1
    snap to storage: targets -> d2
    highway turn d1 into d2
    starts -> d1
    d1 -> d2
    d2 -> targets (reversed)
    """

    def solve(self, I, pad=20, makespan=True, **kwargs):
        I = deepcopy(I)
        I.pad(pad)
        obs = set( I.obstacles )

        Mobs = mat_of(I.obstacles, I.bbox)
        Msto = get_storage(Mobs)
        Mhw = get_highway(Mobs)

        d1, pq1 = snap_to_grid(I.starts, Msto, Mobs)
        sol1 = OrderedSolver(I.starts, d1, obs)
        sol1.solve(pq1)

        d2, pq2 = snap_to_grid(I.targets, Msto, Mobs)
        sol2 = OrderedSolver(I.targets, d2, obs)
        sol2.solve(pq2)

        if makespan:
            sol3 = HighwaySolver(d1,d2,obs,Mhw)
            mv = sol3.find_paths()

            for _ in range(10):
                try:
                    sol3.solve( **kwargs, moves=mv )
                    break
                except Exception as e:
                    print(_,e)
            else:
                raise Exception('all attempts failed')

        else: # total work
            raise NotImplementedError
            sol3 = TWSolver(...)
            sol3.solve()

        self.sol1 = sol1
        self.sol2 = sol2
        self.sol3 = sol3

        ans = ( sol1.hist.export() 
              + sol3.hist.export()
              + sol2.hist.export(reverse=True) )

        return ans

