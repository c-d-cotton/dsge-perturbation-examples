#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def getinputdict():
    inputdict = {}

    inputdict['paramssdict'] = {'a': -1.5, 'b': 0.4}

    inputdict['states'] = ['x']
    inputdict['controls'] = ['z', 'y', 'random']
    inputdict['irfshocks'] = ['x']

    inputdict['equations'] = [
    'x_dot = x + y'
    ,
    'y = a * x'
    ,
    'z_dot = b * z'
    ,
    'random = 0'
    ]

    inputdict['varssdict'] = {'x': 0, 'y': 0, 'z': 0, 'random': 0}

    return(inputdict)


def full():
    inputdict = getinputdict()

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_continuous_func import continuouslineardsgefull
    continuouslineardsgefull(inputdict)


# Run:{{{1
full()
