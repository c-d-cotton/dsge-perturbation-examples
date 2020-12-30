#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

import numpy as np

def simul(run = False, shockpathspecify = False):
    """
    If run = True, need to specify inputdict['dynarepath'] and (if you want to use Octave) inputdict['runwithoctave'] = True
    """
    
    sys.path.append(str(__projectdir__ / Path('dsgesetup')))
    from rbc_simple import getinputdict
    inputdict = getinputdict()
    inputdict['savefolder'] = __projectdir__ / Path('python2dynare/temp/simul_shockpath/')

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    # add pathshock
    if shockpathspecify is True:
        inputdict['shockpath'] = np.array([[1,1,1] + [0] * 17]).transpose()
    else:
        inputdict['pathsimperiods'] = 20
        inputdict['pathsimperiods_noshock'] = 10
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from getshocks_func import getshockpath_inputdict
        inputdict = getshockpath_inputdict(inputdict)

    # python2dynare
    inputdict['python2dynare_simulation'] = 'simul(periods = 300);'
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from python2dynare_func import python2dynare_inputdict
    python2dynare_inputdict(inputdict)

    # run dynare
    if run is True:
        # run dynare
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from python2dynare_func import rundynare_inputdict
        rundynare_inputdict(inputdict)
        # get irfs
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from python2dynare_func import getirfs_dynare_inputdict
        getirfs_dynare_inputdict(inputdict)


# Run:{{{1
if __name__ == '__main__':
    simul(run = True, shockpathspecify = True)


