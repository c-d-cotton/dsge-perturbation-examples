#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def getinputdict(loglineareqs = True):
    inputdict = {}

    inputdict['paramssdict'] = {'a': -0.5}

    inputdict['states'] = ['X']
    inputdict['controls'] = ['Y']
    inputdict['irfshocks'] = ['X']

    inputdict['equations'] = []

    if loglineareqs is True:
        inputdict['equations'].append('X_ss * X_dot = a * X_ss * X')
    else:
        inputdict['equations'].append('X_dot = a * (X - 0.1)')
    if loglineareqs is True:
        inputdict['equations'].append('Y_ss * Y = X_ss ** 2 * X')
    else:
        inputdict['equations'].append('Y = 0.5 * X ** 2 + 0.1')

    p = inputdict['paramssdict']

    # steady state
    p['X'] = 0.1
    p['Y'] = 0.5 * p['X'] ** 2 + 0.1

    if loglineareqs is True:
        inputdict['loglineareqs'] = True
    else:
        inputdict['logvars'] = inputdict['states'] + inputdict['controls']

    return(inputdict)


def check():
    inputdict_loglin = getinputdict(loglineareqs = True)
    inputdict_log = getinputdict(loglineareqs = False)
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_continuous_func import checksame_inputdict_cont
    checksame_inputdict_cont(inputdict_loglin, inputdict_log)
    

def dsgefull():
    inputdict = getinputdict()

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_continuous_func import continuouslineardsgefull
    continuouslineardsgefull(inputdict)


# Run:{{{1
check()
dsgefull()

