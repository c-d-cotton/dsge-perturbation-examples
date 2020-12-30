#!/usr/bin/env python3
"""
A very simple RBC model setup.

If this file is run, checks will be conducted.
"""
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

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
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import checksame_inputdict
    checksame_inputdict(inputdict_loglin, inputdict_log)
    
# Run:{{{1
if __name__ == '__main__':
    check()
