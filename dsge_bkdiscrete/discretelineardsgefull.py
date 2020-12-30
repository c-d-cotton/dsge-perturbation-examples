#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def polfunc():
    
    sys.path.append(str(__projectdir__ / Path('dsgesetup')))
    from rbc_simple import getinputdict
    inputdict = getinputdict()

    inputdict['savefolder'] = __projectdir__ / Path('dsge_bkdiscrete/temp_bkfull/')

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import discretelineardsgefull
    inputdict = discretelineardsgefull(inputdict) 


# Run:{{{1
if __name__ == '__main__':
    polfunc()

