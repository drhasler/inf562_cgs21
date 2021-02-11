from collections import deque

class PrecedenceGraph:
    def __init__(self, src, dst):
        """
        groups: [ ([bots], is_cycle) ]
        P precedence: NEED P[i] to go before i arrives 
        S succedence: NEED i to go before S[i] arrives
        """
        n = len(src)
        D = { x:i for i,x in enumerate(src) }

        self.P = [ D.get(dst[i]) for i in range(n) ]
        self.S = [None] * n
        for i,p in enumerate(self.P):
            if p is not None: self.S[p] = i

        self.groups = []
        seen = set()
        for bot in range(n):
            if bot in seen: continue
            g = deque([bot])

            head = self.P[bot]
            while head != None and head != bot:
                g.appendleft(head)
                head = self.P[head]
            if head != bot:
                tail = self.S[bot]
                while tail != None:
                    g.append(tail)
                    tail = self.S[tail]
            self.groups.append( (list(g), head==bot) ) # T/F is_cycle
            seen |= set(g)

        # assert( sum(len(g) for g,c in self.groups) == n)

