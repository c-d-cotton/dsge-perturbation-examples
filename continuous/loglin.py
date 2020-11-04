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

def getinputdict(loglineareqs = True):
    inputdict = {}

    inputdict['paramssdict'] = {'a': -0.5}

    inputdict['states'] = ['X']
    inputdict['controls'] = ['Y']
    inputdict['irfshocks'] = ['X']

    inputdict['equations'] = []

    if loglineareqs is True:
        inputdict['equations'].append('X_ss * X_dot = a * X_ss * X')
    else:
        inputdict['equations'].append('X_dot = a * (X - 0.1)')
    if loglineareqs is True:
        inputdict['equations'].append('Y_ss * Y = X_ss ** 2 * X')
    else:
        inputdict['equations'].append('Y = 0.5 * X ** 2 + 0.1')

    p = inputdict['paramssdict']

    # steady state
    p['X'] = 0.1
    p['Y'] = 0.5 * p['X'] ** 2 + 0.1

    if loglineareqs is True:
        inputdict['loglineareqs'] = True
    else:
        inputdict['logvars'] = inputdict['states'] + inputdict['controls']

    return(inputdict)


def check():
    inputdict_loglin = getinputdict(loglineareqs = True)
    inputdict_log = getinputdict(loglineareqs = False)
    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_continuous_func.py'), 'checksame_inputdict_cont')(inputdict_loglin, inputdict_log)
    

def dsgefull():
    inputdict = getinputdict()

    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_continuous_func.py'), 'continuouslineardsgefull')(inputdict)


# Run:{{{1
check()
dsgefull()

