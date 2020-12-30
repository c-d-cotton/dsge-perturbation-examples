#!/usr/bin/env python3
"""
This doesn't seem to work as I expected. I guess using simul with the standard deviation of a shock specified does not work. Instead, you seem to need to specify a shock path.
"""
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def simul(run = True):
    
    sys.path.append(str(__projectdir__ / Path('dsgesetup')))
    from rbc_simple import getinputdict
    inputdict = getinputdict()
    inputdict['savefolder'] = __projectdir__ / Path('python2dynare/temp/simul_shocksd/')

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    # add shocksddict
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from getshocks_func import getshocksddict_inputdict
    inputdict = getshocksddict_inputdict(inputdict)

    # python2dynare
    inputdict['python2dynare_simulation'] = 'simul(periods = 200);'
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
    simul(run = True)



