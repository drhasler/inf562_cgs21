import os
import json
import numpy as np

from .util import padl

INSTANCE_DIR = 'datasets'

class Instance:
    """ Instance attrs:
    name, bbox, nbots, nobs,
    starts, targets, obstacles: [ (i,j) ]
    """
    def __init__(self, name, starts, targets, obstacles):
        self.name = name
        
        things = np.array(starts + targets + obstacles)
        low = np.min( things, axis=0 )
        hig = np.max( things, axis=0 )
        self.bbox = tuple(hig - low + 1)
        
        ltup = lambda it: [tuple(x-low) for x in it]
        self.starts = ltup(starts)
        self.targets = ltup(targets)
        self.obstacles = ltup(obstacles)
        
        self.nbots = len(starts)
        self.nobs = len(obstacles)
    
    @classmethod
    def from_file(cls, fname):
        if fname[-4:] != 'json':
            fname = fname + '.instance.json'
        d = json.load(open(
            os.path.join(INSTANCE_DIR, fname) ))
        return cls(*map(d.get,
            ['name','starts','targets','obstacles'] ))
    
    def get_mat(self, attr=None):
        """ returns matrix with obstacles
        and? starts or targets """
        M = np.zeros(self.bbox, int)
        for x in self.obstacles:
            M[x] = 1

        if attr is not None:
            assert(attr in ['starts', 'targets'])
            for x in getattr(self, attr):
                M[x] = 2

        return M

    def pad(self, p):
        """ !! dont forget to deepcopy !! """
        h,w = self.bbox
        self.bbox = ( h+p, w+p )
        
        self.starts = padl(self.starts, p)
        self.targets = padl(self.targets, p)
        self.obstacles = padl(self.obstacles, p)

