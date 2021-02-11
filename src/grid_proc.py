""" Utilities for grid processing """

import numpy as np
from scipy.ndimage import binary_erosion
from tqdm import tqdm

from .util import *
from .dsu import DSU


def dist_to_border(M):
    """ arg: Mat obstacles
    returns: dict( pos -> dst ) """
    h,w = M.shape
    
    cur = [ (  i,  0) for i in range(1,h-1) ] \
        + [ (  i,w-1) for i in range(1,h-1) ] \
        + [ (  0,  j) for j in range(w) ] \
        + [ (h-1,  j) for j in range(w) ]
    
    inb = inbounds(h,w)
    
    d = 0 # BFS
    dst = { x:d for x in cur }
    while cur:
        d += 1
        nxt = []
        for x in cur:
            for y in nb(*x):
                if y not in dst and inb(*y) and M[y] != 1:
                    dst[y] = d
                    nxt.append(y)
        cur = nxt
    return dst

def reachable(M):
    """ arg: Mat obstacles
    returns: Mat reachable

    assumes top left corner reachable
    """
    h,w = M.shape
    inb = inbounds(h,w)
    def idx(i,j): return i*w + j

    dsu = DSU(h*w)

    for x in iter2(*M.shape):
        if M[x] != 1:
            for y in nb(*x):
                if inb(*y) and M[y] != 1:
                    dsu.merge(idx(*x), idx(*y))

    p = dsu.find(idx(0,0))
    R = 0*M
    for x in iter2(*R.shape):
        if dsu.find(idx(*x)) == p:
            R[x] = 1
    return R

def get_highway(Mobs):
    """ arg: Mat obstacles
    returns: Mat(h,w,4) cost of going in direction
    """

    h,w = Mobs.shape
    Mhw = 2 * np.ones( (h,w,4), int ) # NSEW
    M = np.ones_like(Mobs)

    M1 = M & (np.arange(w) % 6 == 0)
    Mhw[:,:,0] -= 1 * M1
    Mhw[:,:,1] += 100 * M1

    M1 = M & (np.arange(w) % 6 == 3)
    Mhw[:,:,0] += 100 * M1
    Mhw[:,:,1] -= 1 * M1

    M1 = M & (np.arange(h) % 16 == 0)[:,None]
    Mhw[:,:,2] -= 1 * M1
    Mhw[:,:,3] += 100 * M1

    M1 = M & (np.arange(h) % 16 == 8)[:,None]
    Mhw[:,:,2] += 100 * M1
    Mhw[:,:,3] -= 1 * M1

    # clockwise
    for i,shift in enumerate([(0,-1),(0,1),(1,0),(0,1)]):
        M1 = np.roll(Mobs, shift, (0,1))
        for x,y in np.argwhere(M1):
            Mhw[x,y,i] = 1
            Mhw[x,y,i^1] = 100

    return Mhw

def get_storage(Mobs):
    """ arg: Mat obstacles
    returns: Mat is_storage
    """

    M = reachable(Mobs)
    M = binary_erosion(M, border_value=1)
    h,w = M.shape

    M &= np.arange(w) % 3 != 0
    M &= (np.arange(h) % 8 != 0)[:,None]

    return M


def snap_to_grid(src, Msto, Mobs):
    """ maps src to storage
    avoiding obstacles

    returns dst, priority_queue
    """

    dist = dist_to_border(Mobs)

    pq = [ (dist[x],i) for i,x in enumerate(src) ]
    pq.sort(reverse=True) # priority queue
    pq = [ bot for _,bot in pq ]

    inb = inbounds(*Mobs.shape)
    def find_free(x0):
        cur = [x0]
        d = 0 # BFS
        dst = { x:d for x in cur }
        while cur:
            d += 1
            nxt = []
            for x in cur:
                if Msto[x]:
                    return x
                for y in nb(*x):
                    if y not in dst and inb(*y) and Mobs[y]==0:
                        dst[y] = d
                        nxt.append(y)
            cur = nxt
        raise Exception

    dst = [None] * len(src)
    for bot in tqdm(pq):
        dst[bot] = find_free(src[bot])
        Msto[dst[bot]] = 0

    return dst, pq[::-1]


