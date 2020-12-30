#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

def analysisdiff():
    
    sys.path.append(str(__projectdir__ / Path('dsgesetup')))
    from rbc_simple import getinputdict
    inputdict = getinputdict()

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import convertstringlisttosympy
    Et_eqs = convertstringlisttosympy(inputdict['equations_noparams'])

    # solve for fxe, fxep, fy, fyp
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import dsgeanalysisdiff
    fxe, fxep, fy, fyp = dsgeanalysisdiff(Et_eqs, inputdict['states'] + inputdict['shocks'], inputdict['controls'])

    print('fxe1:')
    print(fxe)
    print('fy1:')
    print(fy)

    # solve for fx, fxe, fy
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import dsgeanalysisdiff_split
    fx, fxp, fy, fyp, fe, fep = dsgeanalysisdiff_split(Et_eqs, inputdict['states'], inputdict['controls'], inputdict['shocks'])
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import convertjoinxe
    fxe, fxep = convertjoinxe(fx, fxp, fe, fep)

    print('fxe2:')
    print(fxe)
    print('fy2:')
    print(fy)

    print('fx1:')
    print(fx)

    # verify split works ok
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import convertsplitxe
    fx, fxp, fe, fep = convertsplitxe(fxe, fxep, len(inputdict['states']))

    print('fx2:')
    print(fx)


# Run:{{{1
if __name__ == '__main__':
    analysisdiff()

