from bisect import bisect, insort
from collections import defaultdict

__all__ = ['History']

def get_dir(x,y):
    """ assume |x-y| = 1
    enum direction x to y """
    (i,j),(I,J) = x,y
    if i == I: return 1 if j<J else 2
    else: return 3 if i<I else 4

class History:
    """ History class for recording moves and 
    checking if moves are possible """
    def __init__(self, starts):
        self.hist = { x: [(0,0,b)] for b,x in enumerate(starts) }
        # (i,j) -> [(t,dir,bot)] sorted
        # if b1 leaves and b2 arrives
        # [ (t,-d1,b1) (t,d2,b2) ]

    def can_stay(self, t,x):
        """ can stay at x from t onwards """
        if x in self.hist:
            h = self.hist[x]
            return h[-1][0] < t
        return True

    def possible(self, t,x,y, bot=None):
        """ is (t-1,x) -> (t,y) possible? """
        dxy = get_dir(x,y)

        if y in self.hist:
            h = self.hist[y]
            i = bisect(h, (t,10,0))
            if i > 0:
                ot,od,ob = h[i-1]
                if ob != bot:
                    if ot < t and od >= 0: # somebody is there
                        return False
                    if ot == t and od != -dxy: # didnt leave in good direction
                        return False

        if x in self.hist:
            h = self.hist[x]
            i = bisect(h, (t,10,0))
            if i > 0:
                ot,od,ob = h[i-1]
                if ob != bot and ot == t and od != dxy:
                    return False # didnt arrive in good direction

        return True

    def record_one(s, t,x,y, bot):
        """ record (t-1,x) -> (t,y) """
        if x == y: return
        if y not in s.hist:
            s.hist[y] = []

        d = get_dir(x,y)
        insort(s.hist[x], (t,-d, bot))
        insort(s.hist[y], (t, d, bot))

    def record_backtrace(self, bt, bot):
        """ add backtrace to history """
        for t,(x,y) in enumerate(zip(bt,bt[1:]),1):
            self.record_one(t,x,y,bot)

    def export(self, reverse=False):
        def get_dir(x,y):
            (i,j),(I,J) = (y,x) if reverse else (x,y)
            if i == I: return 'W' if J<j else 'E'
            else: return 'N' if I<i else 'S'
        
        bots = defaultdict(list)
        for x,h in self.hist.items():
            for t,d,b in h:
                if d >= 0: bots[b].append((t,x))
        ans = defaultdict(dict)
        for b,h in bots.items():
            h.sort()
            for (_,x),(t,y) in zip(h,h[1:]):
                ans[t][str(b)] = get_dir(x,y)
        ans = list(ans.items())
        ans.sort()
        ans = list( y for x,y in ans )
        if reverse: ans = ans[::-1]
        return ans

    def pos_bots(self):
        """ returns dict( bot -> [(t,x)] )
        """
        pos_bots = defaultdict(list)
        for k,v in self.hist.items():
            for t,d,b in v:
                if d >= 0:
                    pos_bots[b].append((t,k))
        for v in pos_bots.values():
            v.sort()
        return pos_bots

