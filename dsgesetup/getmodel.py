#!/usr/bin/env python3
"""
This function just returns a model dictionary from the basic inputs.
This dictionary doesn't actually run any computations.
"""
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

# Running the getmodel function:{{{1
def getmodel():
    from rbc_simple import getinputdict
    inputdict = getinputdict()

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    return(inputdict)


# Run:{{{1
if __name__ == '__main__':
    getmodel()
