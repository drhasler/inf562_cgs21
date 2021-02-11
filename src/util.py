import numpy as np
from scipy.ndimage import binary_erosion

def padl(it, w: int): # padded list
    return [ (x+w,y+w) for x,y in it ]

def unpad(A, w: int): # undo np.pad
    return A[w:-w, w:-w]

def mat_of(pts, shape): # pts: [ (i,j) ]
    M = np.zeros(shape, int)
    for p in pts: M[p] = 1
    return M

def nb(i,j): # all one neighbors
    return [
        (i-1,j+0),
        (i+1,j+0),
        (i+0,j-1),
        (i+0,j+1),
    ]

def l1(x,y): # manhattan dst
    (i,j),(I,J) = x,y
    return abs(i-I) + abs(j-J)

def nxt_hop(p0, p1):
    """ returns p2
    such that p2 - p1 = p1 - p0 """
    i0,j0 = p0
    i1,j1 = p1
    return ( 2*i1-i0, 2*j1-j0 )

def iter2(h,w):
    for i in range(h):
        for j in range(w):
            yield (i,j)

def inbounds(h,w):
    def f(i,j):
        return i >= 0 and i < h and j >= 0 and j < w
    return f


