#!/usr/bin/env python3
"""
A very simple NK model setup.
Note that I need to specify a state for my codes to work so I just define Pi_tm1 even though this is not needed.
"""
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

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
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import checksame_inputdict
    checksame_inputdict(inputdict_loglin, inputdict_log)
    
# Run:{{{1
if __name__ == '__main__':
    check()
