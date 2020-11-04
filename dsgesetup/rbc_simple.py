#!/usr/bin/env python3
"""
A very simple RBC model setup.

If this file is run, checks will be conducted.
"""
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

# Defining the model:{{{1
def getparamssdict(p):
    if p is None:
        p = {}
    p_defaults = {'ALPHA': 0.3, 'BETA': 0.95, 'DELTA': 0.1, 'RHO': 0.9}
    for param in p_defaults:
        if param not in p:
            p[param] = p_defaults[param]

    return(p)
    

def getss(p):
    """
    Get steady states of variables.
    """
    
    v = {}
    v['Am1'] = 1
    v['A'] = 1
    v['K'] = ((p['ALPHA'] * v['A'])/(1/p['BETA'] - 1 + p['DELTA']))**(1/(1-p['ALPHA']))
    v['C'] = v['A'] * v['K'] ** p['ALPHA'] - p['DELTA'] * v['K']

    return(v)


def getinputdict(p = None, loglineareqs = True):
    """
    Direct shocks.

    Just calls the parameters in getparamssdict by default
    """
    inputdict = {}
    inputdict['controls'] = ['C', 'A']
    inputdict['states'] = ['Am1', 'K']
    inputdict['shocks'] = ['epsilon_a']

    inputdict['equations'] = []

    # euler condition
    if loglineareqs is True:
        inputdict['equations'].append('1/C_ss * -C = BETA * 1/C_ss * -C_p * (ALPHA * A_ss * K_ss ** (ALPHA - 1) + (1 - DELTA)) + BETA * 1 / C_ss * (ALPHA * A_ss * K_ss ** (ALPHA - 1) * (A_p + (ALPHA - 1) * K_p))')
    else:
        inputdict['equations'].append('1 / C = BETA * 1 / C_p * (ALPHA * A_p * K_p ** (ALPHA - 1) + (1-DELTA))')
    # resource condition
    if loglineareqs is True:
        inputdict['equations'].append('C_ss * C + K_ss * K_p = A_ss * K_ss ** ALPHA * (A + ALPHA * K) + (1 - DELTA) * K_ss * K')
    else:
        inputdict['equations'].append('C + K_p = A * K ** ALPHA + (1-DELTA) * K')
    # productivity process
    if loglineareqs is True:
        inputdict['equations'].append('Am1_p = RHO * Am1 + epsilon_a')
    else:
        inputdict['equations'].append('log(Am1_p) = RHO * log(Am1) + epsilon_a')
    # get A_t as well as A_tm1 for easier analysis
    inputdict['equations'].append('A = Am1_p')

    inputdict['paramssdict'] = getparamssdict(p)
    inputdict['varssdict'] = getss(inputdict['paramssdict'])

    if loglineareqs is True:
        inputdict['loglineareqs'] = True
    else:
        # if do not specify loglineareqs = True then convert all variables to log form
        inputdict['logvars'] = True

    return(inputdict)


# Checks:{{{1
def check():
    """
    Checks the steady state and verifies the log-linearized and log models produce identical results.
    """
    inputdict_loglin = getinputdict(loglineareqs = True)
    inputdict_log = getinputdict(loglineareqs = False)
    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'checksame_inputdict')(inputdict_loglin, inputdict_log)
    
# Run:{{{1
if __name__ == '__main__':
    check()
