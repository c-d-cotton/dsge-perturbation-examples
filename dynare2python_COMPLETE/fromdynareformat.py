#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def main():
    """
    Direct shocks.
    """
    inputdict = {}
    inputdict['dynareequations'] = [
    '1/c - BETA * 1/c(+1)*(ALPHA*a(+1)*k(0)**(ALPHA-1) + (1-DELTA))'
    ,
    'c + k - a*k(-1)**ALPHA - (1-DELTA)*k(-1)'
    ,
    'log(a)-RHO*log(a(-1)) - epsilon_a'
    ]

    inputdict['paramssdict'] = {'ALPHA': 0.3, 'BETA': 0.95, 'DELTA': 0.1, 'RHO': 0.9}

    p = inputdict['paramssdict']
    v = {}
    v['am1'] = 1
    v['a'] = 1
    v['k'] = ((p['ALPHA'] * v['a'])/(1/p['BETA'] - 1 + p['DELTA']))**(1/(1-p['ALPHA']))
    v['c'] = v['a'] * v['k'] ** p['ALPHA'] - p['DELTA'] * v['k']

    inputdict['dynarevariables'] = ['a', 'k', 'c']
    inputdict['shocks'] = ['epsilon_a']
    inputdict['savefolder'] = __projectdir__ / Path('me/basic/short/temp/')
    inputdict['dynarevarssdict'] = v

    inputdict['dynarelogvars'] = ['a', 'k', 'c']

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import discretelineardsgefull
    discretelineardsgefull(inputdict)

# Run:{{{1
main()
