#!/usr/bin/env python3
"""
A very simple NK model setup.
Note that I need to specify a state for my codes to work so I just define Pi_tm1 even though this is not needed.
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
    p_defaults = {'PHIpi': 1.5, 'Rbar': 1.02}
    for param in p_defaults:
        if param not in p:
            p[param] = p_defaults[param]

    return(p)
    

def getss(p):
    """
    Get steady states of variables.
    """
    
    p['Rp'] = p['Rbar']
    p['Pi'] = 1
    p['I'] = p['Rp'] * p['Pi']
    p['Pim1'] = p['Pi']

    return(p)


def getinputdict(p = None, loglineareqs = True):
    inputdict = {}

    # need a state otherwise codes fail
    inputdict['states'] = ['Pim1']
    inputdict['controls'] = ['Pi', 'I', 'Rp']

    # equations:{{{
    inputdict['equations'] = []

    if loglineareqs is True:
        inputdict['equations'].append('I = Pi_p + Rp')
    else:
        inputdict['equations'].append('I = Pi_p * Rp')
    if loglineareqs is True:
        inputdict['equations'].append('I = Rp + PHIpi * Pi')
    else:
        inputdict['equations'].append('I = Rp * Pi ** PHIpi')
    if loglineareqs is True:
        inputdict['equations'].append('Rp = 0')
    else:
        inputdict['equations'].append('Rp = Rbar')
    if loglineareqs is True:
        inputdict['equations'].append('Pim1_p = Pi')
    else:
        inputdict['equations'].append('Pim1_p = Pi')
        
    # equations:}}}

    # get parameters
    inputdict['paramssdict'] = getparamssdict(p)
    # add steady state
    # here use the same dict for the parameters and the steady state
    getss(inputdict['paramssdict'])

    if loglineareqs is True:
        inputdict['loglineareqs'] = True
    else:
        inputdict['logvars'] = inputdict['states'] + inputdict['controls']

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
