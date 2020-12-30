#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def polfunc():
    
    sys.path.append(str(__projectdir__ / Path('dsgesetup')))
    from rbc_simple import getinputdict
    inputdict = getinputdict()

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    # get policy function
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import polfunc_inputdict
    inputdict = polfunc_inputdict(inputdict)

    print(inputdict['hx'])
    print(inputdict['gx'])


# Run:{{{1
if __name__ == '__main__':
    polfunc()

