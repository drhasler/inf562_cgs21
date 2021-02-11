""" usage/driver """
import os
from src.instance import Instance, INSTANCE_DIR
from src.solver import Solver1
from src.check import check_solution


def MinimizeMakespan(I, save=False):
    """ I fname | Instance """
    if isinstance(I, str):
        I = Instance.from_file(I)

    sv = Solver1()
    ans = sv.solve(I, pad=20, th=.01) # th circulation density
    sol = { 'instance': I.name, 'steps': ans }

    assert( check_solution(I, sol) )

    if save:
        fp = open(f'solutions/{I.name}.sol.json','w')
        json.dump(sol, fp)
    return sol

def MinimizeTotalWork(I, save=False):
    return MinimizeMakespan(I, save)

def CheckSolution(sol):
    """ sol name or """
    if isinstance(sol, str):
        if sol[-4:] != '.json':
            sol += '.sol.json'

        fp = open(f'solutions/{sol}')
        sol = json.load(fp)


    name = sol['instance']
    I = Instance.from_file(name)
    return check_solution(I, sol)

if __name__ == '__main__':
    name = 'election_109'

    sol = MinimizeMakespan(name)
    print(CheckSolution(sol))
