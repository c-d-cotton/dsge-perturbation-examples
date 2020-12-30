#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def irfcompare():
    
    DELTAlist = [0, 0.1, 1]
    inputdictlist = []
    for DELTA in DELTAlist:
        p = {'DELTA': DELTA}
        sys.path.append(str(__projectdir__ / Path('dsgesetup')))
        from rbc_simple import getinputdict
        inputdictlist.append( getinputdict(p = p) )

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import irfmultiplemodels
    irfmultiplemodels(DELTAlist, inputdictlist, ['A', 'C', 'K'], 'epsilon_a')


# Run:{{{1
if __name__ == '__main__':
    irfcompare()

