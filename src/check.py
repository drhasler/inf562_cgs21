""" Solution checking
"""

from .instance import Instance
import os
import json
from itertools import starmap

def check_solution(I: Instance, sol: dict):
    """
    checks solution in
    O(nbots + nobs + total work)
    """

    obs = set( I.obstacles )
    cur =  { bot: x for bot,x in enumerate(I.starts) }
    dcur = { x: bot for bot,x in enumerate(I.starts) }

    _delta = dict( zip("NSEW",
        ( (-1, 0), ( 1, 0), ( 0,1), ( 0,-1), )))
    def read(bot, direction):
        return int(bot), _delta[direction]

    for si,step in enumerate(sol['steps'],1):
        nxt = {}
        dnxt = {}

        step = dict( starmap(read, step.items()) )

        for b,(x,y) in step.items():
            i,j = cur[b]
            np = (i+x, j+y)

            # if b in (1015,6979):
            # print(b, np)

            nxt[b] = np
            if np in dnxt:
                o = dnxt[np]
                print(f' collision bot{b} bot{o} pos{np} t{si}')
                print(cur[b], nxt[b], cur[o])
                return False
            dnxt[np] = b

            if np in obs: # obstacle
                print(f'obstacle bot{b} pos{np} t{si}')
                return False
        
        for b,p in nxt.items():
            if p in dcur:
                o = dcur[p]
                if o not in nxt:
                    print(f'b{b} crashed into b{o} pos{p} t{si}')
                    print(cur[b], cur[o])
                    return False
                elif step[b] != step[o]:
                    print(f'b{b} hit outgoing b{o} pos{p} t{si}')
                    print(cur[b], nxt[b], nxt[o])
                    return False

        for b,p in nxt.items():
            del dcur[cur[b]]
        cur.update(nxt)
        dcur.update(dnxt)

    for b in range(I.nbots):
        if cur[b] != I.targets[b]:
            print(f"bot{b} missed target {cur[b]}{I.targets[b]}")
            return False

    return True

if __name__ == '__main__':
    DIRNAME = 'solutions'
    fnames  = os.listdir(DIRNAME)

    for fname in fnames:
        print(fname)
        sol = json.load(
            open(os.path.join(DIRNAME, 'sol1.json'))
        )
        I = Instance.from_file(fname)
        if check_solution(I, sol):
            M = len(sol['steps'])
            TW = sum(map(len, sol['steps']))
            print(M, TW)
