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

import numpy as np

def simlinear():
    
    inputdict = importattr(__projectdir__ / Path('dsgesetup/rbc_simple.py'), 'getinputdict')()

    # add model
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgesetup_func.py'), 'getmodel_inputdict')(inputdict) 

    # get policy function
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bkdiscrete_func.py'), 'polfunc_inputdict')(inputdict)

    # add shocks
    inputdict['pathsimperiods'] = 100
    inputdict['shocksddict'] = {'epsilon_a': 0.01}
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/getshocks_func.py'), 'getshockpath_inputdict')(inputdict)

    # simulate path
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/simlineardsge_func.py'), 'simpathlinear_inputdict')(inputdict)

    # path of non log-linearized variable
    print(inputdict['expssvarpath'])

    # standard deviation of consumption
    print(np.std(inputdict['varpath'][:, inputdict['stateshockcontrolposdict']['c']]))


# Run:{{{1
if __name__ == '__main__':
    simlinear()

