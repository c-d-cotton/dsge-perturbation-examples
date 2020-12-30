#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

import numpy as np

def simlinear():
    
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

    # add shocks
    inputdict['pathsimperiods'] = 100
    inputdict['shocksddict'] = {'epsilon_a': 0.01}
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from getshocks_func import getshockpath_inputdict
    inputdict = getshockpath_inputdict(inputdict)

    # simulate path
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from simlineardsge_func import simpathlinear_inputdict
    inputdict = simpathlinear_inputdict(inputdict)

    # path of non log-linearized variable
    print(inputdict['expssvarpath'])

    # standard deviation of consumption
    print(np.std(inputdict['varpath'][:, inputdict['stateshockcontrolposdict']['c']]))


# Run:{{{1
if __name__ == '__main__':
    simlinear()

