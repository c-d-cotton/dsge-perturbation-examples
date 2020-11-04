#!/usr/bin/env python3
"""
Example of where I input only some parameters into the model and solve for the fx,fxp,fy,fyp matrices
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

import copy

# Basic Dicts:{{{1
def getparamssdict_partial():
    """
    All parameters except BETA
    """
    p = {'ALPHA': 0.3, 'DELTA': 0.1, 'RHO': 0.9}
    return(p)


def getparamssdict_fullbasic():
    p = getparamssdict_partial()
    p['BETA'] = 0.95
    return(p)


def getvarssdict(p):
    v = {}
    v['Am1'] = 1
    v['A'] = v['Am1']
    v['K'] = ((p['ALPHA'] * v['A'])/(1/p['BETA'] - 1 + p['DELTA']))**(1/(1-p['ALPHA']))
    v['C'] = v['A'] * v['K'] ** p['ALPHA'] - p['DELTA'] * v['K']

    return(v)


def getinputdict_noparamssdict(loglineareqs = True):
    """
    This is the inputdict without the steady state included.
    """
    inputdict = {}

    inputdict['equations'] = []
    if loglineareqs is True:
        inputdict['equations'].append('1/C_ss * (-C) = BETA * 1/C_ss * (ALPHA * A_ss * K_ss ** (ALPHA - 1) * (A_p + (ALPHA - 1) * K_p)) + BETA * 1/C_ss * (-C_p) * (ALPHA * A_ss * K_ss ** (ALPHA - 1) + (1 - DELTA))')
    else:
        inputdict['equations'].append('1/C = BETA * 1/C_p*(ALPHA*A_p*K_p**(ALPHA-1) + (1-DELTA))')

    if loglineareqs is True:
        inputdict['equations'].append('C_ss * C + K_ss * K_p = A_ss * K_ss ** ALPHA * (A + ALPHA * K) + (1 - DELTA) * K_ss * K')
    else:
        inputdict['equations'].append('C + K_p = A*K**ALPHA + (1-DELTA)*K')

    if loglineareqs is True:
        inputdict['equations'].append('A = Am1_p')
    else:
        inputdict['equations'].append('A = Am1_p')

    if loglineareqs is True:
        inputdict['equations'].append('Am1_p = RHO * Am1 + epsilon_a')
    else:
        inputdict['equations'].append('log(Am1_p) = RHO * log(Am1) + epsilon_a')

    inputdict['controls'] = ['C', 'A']
    inputdict['states'] = ['Am1', 'K']
    inputdict['shocks'] = ['epsilon_a']

    if loglineareqs is True:
        inputdict['loglineareqs'] = True
    else:
        inputdict['logvars'] = inputdict['states'] + inputdict['controls']

    return(inputdict)


# Full Model:{{{1
def getinputdict_full(p, loglineareqs = True):
    inputdict = getinputdict_noparamssdict(loglineareqs = loglineareqs)

    inputdict['paramssdict'] = p
    inputdict['varssdict'] = getvarssdict(inputdict['paramssdict'])

    return(inputdict)



def checks():
    p = getparamssdict_fullbasic()
    inputdict_loglin = getinputdict_full(p, loglineareqs = True)
    inputdict_log = getinputdict_full(p, loglineareqs = False)
    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'checksame_inputdict')(inputdict_loglin, inputdict_log)
    

def solvefulldsge(p):
    inputdict = getinputdict_full(p)

    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bkdiscrete_func.py'), 'discretelineardsgefull')(inputdict)


def solvefulldsge_test():
    p = getparamssdict_fullbasic()

    solvefulldsge(p)


# Partial Model:{{{1
def getpartialeval(partialeval = False, partialeval_numeval = False):
    """
    """
    inputdict = getinputdict_noparamssdict()

    if partialeval is True:
        # need to specify some parameters here since we're doing a partial eval
        p = getparamssdict_partial()
        # if we are doing a numeval then we should specify some steady state parameters
        # otherwise doing a numerical eval makes no difference
        if partialeval_numeval is True:
            p['A'] = 1
        inputdict['paramssdict'] = p
    else:
        # no need to specify parameters if not partially evaluating
        # however we could choose to specify parameters here and it wouldn't make any difference
        inputdict['paramssdict'] = {}

    # get model
    # we haven't solved for the steady state so allow for missingparams
    inputdict['missingparams'] = True
    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgesetup_func.py'), 'getmodel_inputdict')(inputdict)

    if partialeval is True:
        if partialeval_numeval is True:
            # compute numerical fx, fxp, fy, fyp matrices
            # since we don't specify fxefy_cancelparams = False then we do cancel the params we have defined
            # since we specify fxefy_f_usenumerical then when we're doing the partial conversion, we use the numerical derivatives rather than the analytical derivatives
            inputdict['fxefy_f_usenumerical'] = True
            inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'getnfxenfy_inputdict')(inputdict)
        else:
            # compute analytical fx, fxp, fy, fyp matrices
            # since we don't specify fxefy_cancelparams = False then we do cancel the params we have defined
            # however we don't cancel out any steady state variables
            inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'getfxefy_inputdict')(inputdict)
    else:
        # compute analytical fx, fxp, fy, fyp matrices
        # don't cancel params so do full replace of variables
        inputdict['fxefy_cancelparams'] = False
        inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'getfxefy_inputdict')(inputdict)

    # convert fx, fxy, fy, fyp matrices to functions (makes it quicker to do conversion)
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'funcstoeval_inputdict')(inputdict)

    return(inputdict)


def fullfrompartial(inputdict_partiallyevaluated, updatedparamssdict, skipinputdict = False):

    p = copy.deepcopy(inputdict_partiallyevaluated['paramssdict'])
    p.update(updatedparamssdict)

    # add varssdict
    v = getvarssdict(p)

    # get all parameters
    p.update(v)

    if skipinputdict is True:
        retlist = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'partialtofulleval_quick_inputdict')(inputdict_partiallyevaluated, p)
    else:
        retlist = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'partialtofulleval_inputdict')(inputdict_partiallyevaluated, p)

    return(retlist)


def fullfrompartial_test(partialeval = False, partialeval_numeval = False, skipinputdict = False):
    """
    partialeval = False: Don't need to specify any parameters initially. Do full evaluation at the end.
    partialeval = True, partialeval_numeval = False: Need to specify some parameters initially. However, don't evaluate any of the steady state parameters.
    partialeval = True, partialeval_numeval = True: Need to specify some parameters and steady state values initially which get evaluated.

    skipinputdict = False: Return the usual inputdict i.e. update the relevant parameterdict and save the numerically evaluated matrices under nfxe, nfy etc.
    skipinputdict = True: Just return the matrices directly without updating inputdict.
    """

    # if doing numerical evaluation then must have specified some parameters so set partialeval = True
    if partialeval_numeval is True:
        partialeval = True

    inputdict = getpartialeval(partialeval = partialeval, partialeval_numeval = partialeval_numeval)

    print('Before numerically eval:')
    print(inputdict['fxe'])

    if partialeval is True:
        updatedparamssdict = {'BETA': 0.95}
    else:
        # if partialeval is False, we didn't specify any parameters yet
        # so need to specify full paramssdict
        updatedparamssdict = getparamssdict_partial()
        updatedparamssdict.update({'BETA': 0.95})

    retlist = fullfrompartial(inputdict, updatedparamssdict, skipinputdict = skipinputdict)
    if skipinputdict is True:
        print('After fully evaluated:')
        print(retlist[0])
    else:
        print('After fully evaluated:')
        print(inputdict['nfxe'])
        
# Run:{{{1
fullfrompartial_test()
