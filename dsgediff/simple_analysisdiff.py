#!/usr/bin/env python3
# PYTHON_PREAMBLE_START_STANDARD:{{{

# Christopher David Cotton (c)
# http://www.cdcotton.com

# modules needed for preamble
import importlib
import os
from pathlib import Path
import sys

# Get full real filename
__fullrealfile__ = os.path.abspath(__file__)

# Function to get git directory containing this file
def getprojectdir(filename):
    curlevel = filename
    while curlevel is not '/':
        curlevel = os.path.dirname(curlevel)
        if os.path.exists(curlevel + '/.git/'):
            return(curlevel + '/')
    return(None)

# Directory of project
__projectdir__ = Path(getprojectdir(__fullrealfile__))

# Function to call functions from files by their absolute path.
# Imports modules if they've not already been imported
# First argument is filename, second is function name, third is dictionary containing loaded modules.
modulesdict = {}
def importattr(modulefilename, func, modulesdict = modulesdict):
    # get modulefilename as string to prevent problems in <= python3.5 with pathlib -> os
    modulefilename = str(modulefilename)
    # if function in this file
    if modulefilename == __fullrealfile__:
        return(eval(func))
    else:
        # add file to moduledict if not there already
        if modulefilename not in modulesdict:
            # check filename exists
            if not os.path.isfile(modulefilename):
                raise Exception('Module not exists: ' + modulefilename + '. Function: ' + func + '. Filename called from: ' + __fullrealfile__ + '.')
            # add directory to path
            sys.path.append(os.path.dirname(modulefilename))
            # actually add module to moduledict
            modulesdict[modulefilename] = importlib.import_module(''.join(os.path.basename(modulefilename).split('.')[: -1]))

        # get the actual function from the file and return it
        return(getattr(modulesdict[modulefilename], func))

# PYTHON_PREAMBLE_END:}}}

def analysisdiff():
    
    inputdict = importattr(__projectdir__ / Path('dsgesetup/rbc_simple.py'), 'getinputdict')()

    # add model
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgesetup_func.py'), 'getmodel_inputdict')(inputdict) 

    Et_eqs = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'convertstringlisttosympy')(inputdict['equations_noparams'])

    # solve for fxe, fxep, fy, fyp
    fxe, fxep, fy, fyp = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'dsgeanalysisdiff')(Et_eqs, inputdict['states'] + inputdict['shocks'], inputdict['controls'])

    print('fxe1:')
    print(fxe)
    print('fy1:')
    print(fy)

    # solve for fx, fxe, fy
    fx, fxp, fy, fyp, fe, fep = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'dsgeanalysisdiff_split')(Et_eqs, inputdict['states'], inputdict['controls'], inputdict['shocks'])
    fxe, fxep = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'convertjoinxe')(fx, fxp, fe, fep)

    print('fxe2:')
    print(fxe)
    print('fy2:')
    print(fy)

    print('fx1:')
    print(fx)

    # verify split works ok
    fx, fxp, fe, fep = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'convertsplitxe')(fxe, fxep, len(inputdict['states']))

    print('fx2:')
    print(fx)


# Run:{{{1
if __name__ == '__main__':
    analysisdiff()

