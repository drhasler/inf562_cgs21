
def find_path(self, src, dst):
    """ returns path respecting highways """

    def poss_moves(pos):
        i,j = pos
        moves = []
        if self.Mhw[i,j]: # grid aligned: respect the highways
            if i%8==0:
                if i%16 == 0: moves.append((0,1))
                else: moves.append((0,-1))
            if j%3==0:
                if j%6 == 0: moves.append((1,0))
                else: moves.append((-1,0))
        else: moves = [(1,0),(-1,0),(0,1),(0,-1)] # else do whatever
        return [(i+x,j+y) for x,y in moves]

    def bake(t,pos,st=None):
        (i,j),(x,y) = pos,dst
        H = abs(i-x) + abs(j-y)
        return State(t,pos,H,st)

    pq = [ bake(0, src) ]

    mem = set() # memoize visited states
    while pq:
        st = heappop(pq)
        x = st.pos
        t = st.t

        if l1(x,dst) == 1:
            ot = bake(t+1,dst,st)
            return ot.backtrace()
        for y in poss_moves(x):
            if not y in mem and not y in self.obs:
                mem.add(y)
                ot = bake(t+1,y,st)
                heappush(pq,ot)
    raise Exception

