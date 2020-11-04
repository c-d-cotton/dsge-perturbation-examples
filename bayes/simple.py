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

import functools
import numpy as np

# Basic Setup:{{{1
def getparamssdict(p = None):
    """
    Add parameters.
    """
    if p is None:
        p = {}
    p_defaults = {'RHO': 0.9, 'SIGMA_epsilon': 0.1}
    for param in p_defaults:
        if param not in p:
            p[param] = p_defaults[param]

    return(p)


def getvarssdict(p):
    """
    Add steady state of variables.
    """
    p['Xm1'] = 1
    p['Y'] = 1

    return(p)


def getinputdict_noparamssdict(loglineareqs = True):
    """
    This is the inputdict without the steady state included.
    """
    inputdict = {}

    inputdict['equations'] = []
    if loglineareqs is True:
        inputdict['equations'].append('Xm1_p = RHO * Xm1 + epsilon')
    else:
        inputdict['equations'].append('log(Xm1_p) = RHO * log(Xm1) + epsilon')

    if loglineareqs is True:
        inputdict['equations'].append('Y = Xm1_p')
    else:
        inputdict['equations'].append('Y = Xm1_p')


    inputdict['controls'] = ['Y']
    inputdict['states'] = ['Xm1']
    inputdict['shocks'] = ['epsilon']

    if loglineareqs is True:
        inputdict['loglineareqs'] = True
    else:
        inputdict['logvars'] = inputdict['states'] + inputdict['controls']

    return(inputdict)


# Full Model:{{{1
def getinputdict_full(p = None, loglineareqs = True):
    inputdict = getinputdict_noparamssdict(loglineareqs = loglineareqs)

    inputdict['paramssdict'] = getparamssdict(p)
    inputdict['varssdict'] = getvarssdict(inputdict['paramssdict'])

    return(inputdict)



def checks():
    p = getparamssdict()
    inputdict_loglin = getinputdict_full(p, loglineareqs = True)
    inputdict_log = getinputdict_full(p, loglineareqs = False)
    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'checksame_inputdict')(inputdict_loglin, inputdict_log)
    

def solvefulldsge(p):
    inputdict = getinputdict_full(p)

    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bkdiscrete_func.py'), 'discretelineardsgefull')(inputdict)


def solvefulldsge_test():
    solvefulldsge()


# Bayesian Estimation:{{{1
def getinputdict_bayesian():
    """
    Run this function before doing any evaluation

    inputdict without solving for parameters
    Note that we have specified an empty parameter dict here
    """
    inputdict = getinputdict_noparamssdict()

    # get model
    # we haven't solved for the steady state so allow for missingparams
    inputdict['missingparams'] = True
    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgesetup_func.py'), 'getmodel_inputdict')(inputdict)

    # compute analytical fx, fxp, fy, fyp matrices
    # don't cancel params so do full replace of variables
    inputdict['fxefy_cancelparams'] = False
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'getfxefy_inputdict')(inputdict)

    # convert fx, fxy, fy, fyp matrices to functions (makes it quicker to do conversion)
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgediff_func.py'), 'funcstoeval_inputdict')(inputdict)

    return(inputdict)


def getreplacedict_bayesian_aux(paramnames, paramvalues):
    """
    This function returns the replacedict I need to convert fxe_f, fy_f etc. into nfxe, nfy etc.
    """
    p = {}
    for i in range(len(paramnames)):
        p[paramnames[i]] = paramvalues[i]

    p = getparamssdict(p)
    p = getvarssdict(p)

    return(p)


def getsimdata(numperiods = 100):
    """
    To get simulated data, we simulate out the system of equations.
    """
    inputdict = getinputdict_full()

    # complete inputdict
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsgesetup_func.py'), 'getmodel_inputdict')(inputdict)

    # get policy function
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bkdiscrete_func.py'), 'polfunc_inputdict')(inputdict)

    # add shocks
    inputdict['pathsimperiods'] = numperiods
    inputdict['shocksddict'] = {'epsilon': 0.1}
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/getshocks_func.py'), 'getshockpath_inputdict')(inputdict)

    # simulate path
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/simlineardsge_func.py'), 'simpathlinear_inputdict')(inputdict)

    varnames = ['Xm1', 'Y']
    varnames = ['Y']
    data = inputdict['varpath'][:, [inputdict['stateshockcontrolposdict'][varnames[i]] for i in range(len(varnames))]]

    return(varnames, data)

    
def dobayes_dsge():
    # get same every time
    np.random.seed(41)

    # get likelihood function:{{{

    # get inputdict with fxe_f etc. functions
    inputdict = getinputdict_bayesian()

    # get replacedict function
    paramnames = ['RHO', 'SIGMA_epsilon']
    getreplacedict_bayesian = functools.partial(getreplacedict_bayesian_aux, paramnames)

    # get data
    # in T x N format
    varnames, data = getsimdata(numperiods = 1000)

    # get shock variance matrix
    # not needed if standard deviations are included in equations i.e. SIGMA_epsilon * epsilon
    Omega = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bayes_func.py'), 'Omega_fromsdvec')(['SIGMA_epsilon'])
    # get tuple of Omega_func, Omega_params
    Omega_func_paramnames = importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bayes_func.py'), 'Omega_convertfunc')(Omega)

    # get log-likelihood function
    # input parameters into this function and return log-likelihood (without priors)
    loglikelihoodfunc = functools.partial(importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bayes_func.py'), 'getbayes_dsge_logl_aux'), inputdict, getreplacedict_bayesian, data, varnames, Omega_funcparamnames = Omega_func_paramnames)

    # }}}

    # get prior function and info:{{{
    priorlist_meansd = [['beta', 0.9, 0.05], ['invgamma', 0.1, 0.05]]
    # get a priorlist based upon parameters rather than means and standard deviations
    priorlist_parameters = importattr(__projectdir__ / Path('submodules/python-math-func/bayesian_func.py'), 'getpriorlist_convert')(priorlist_meansd)
    # get details on priors
    prior_means, prior_sds, prior_lbs, prior_ubs = importattr(__projectdir__ / Path('submodules/python-math-func/bayesian_func.py'), 'getpriorlistdetails_parameters')(priorlist_parameters)
    # get a density function for the priors - this is NOT log
    priorfunc = functools.partial(importattr(__projectdir__ / Path('submodules/python-math-func/bayesian_func.py'), 'getpriordensityfunc_aux'), priorlist_parameters)
    # get scalelist based upon sds
    scalelist = [0.5 * sd for sd in prior_sds]

    def posteriorfunc(values):
        """
        Get the posterior function incorporating both the priors and the log-likelihood
        Note that we log the prior function
        """
        return(np.log(priorfunc(values)) + loglikelihoodfunc(values))
    # }}}

    # implement metropolis-hastings:{{{
    results = importattr(__projectdir__ / Path('submodules/python-math-func/bayesian_func.py'), 'metropolis_hastings')(posteriorfunc, scalelist, prior_means, 10000, lowerboundlist = prior_lbs, upperboundlist = prior_ubs, printdetails = True, logposterior = True)
    print(np.mean(np.array(results)[1000: , :], axis = 0))
    # }}}
dobayes_dsge()
