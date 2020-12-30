#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

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
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import checksame_inputdict
    checksame_inputdict(inputdict_loglin, inputdict_log)
    

def solvefulldsge(p):
    inputdict = getinputdict_full(p)

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import discretelineardsgefull
    inputdict = discretelineardsgefull(inputdict)


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
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    getmodel_inputdict(inputdict)

    # compute analytical fx, fxp, fy, fyp matrices
    # don't cancel params so do full replace of variables
    inputdict['fxefy_cancelparams'] = False
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import getfxefy_inputdict
    inputdict = getfxefy_inputdict(inputdict)

    # convert fx, fxy, fy, fyp matrices to functions (makes it quicker to do conversion)
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import funcstoeval_inputdict
    inputdict = funcstoeval_inputdict(inputdict)

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
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict)

    # get policy function
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import polfunc_inputdict
    inputdict = polfunc_inputdict(inputdict)

    # add shocks
    inputdict['pathsimperiods'] = numperiods
    inputdict['shocksddict'] = {'epsilon': 0.1}
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from getshocks_func import getshockpath_inputdict
    inputdict = getshockpath_inputdict(inputdict)

    # simulate path
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from simlineardsge_func import simpathlinear_inputdict
    inputdict = simpathlinear_inputdict(inputdict)

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
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bayes_func import Omega_fromsdvec
    Omega = Omega_fromsdvec(['SIGMA_epsilon'])
    # get tuple of Omega_func, Omega_params
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bayes_func import Omega_convertfunc
    Omega_func_paramnames = Omega_convertfunc(Omega)

    # get log-likelihood function
    # input parameters into this function and return log-likelihood (without priors)
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bayes_func import getbayes_dsge_logl_aux
    loglikelihoodfunc = functools.partial(getbayes_dsge_logl_aux, inputdict, getreplacedict_bayesian, data, varnames, Omega_funcparamnames = Omega_func_paramnames)

    # }}}

    # get prior function and info:{{{
    priorlist_meansd = [['beta', 0.9, 0.05], ['invgamma', 0.1, 0.05]]
    # get a priorlist based upon parameters rather than means and standard deviations
    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import getpriorlist_convert
    priorlist_parameters = getpriorlist_convert(priorlist_meansd)
    # get details on priors
    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import getpriorlistdetails_parameters
    prior_means, prior_sds, prior_lbs, prior_ubs = getpriorlistdetails_parameters(priorlist_parameters)
    # get a density function for the priors - this is NOT log
    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import getpriordensityfunc_aux
    priorfunc = functools.partial(getpriordensityfunc_aux, priorlist_parameters)
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
    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import metropolis_hastings
    results = metropolis_hastings(posteriorfunc, scalelist, prior_means, 10000, lowerboundlist = prior_lbs, upperboundlist = prior_ubs, printdetails = True, logposterior = True)
    print(np.mean(np.array(results)[1000: , :], axis = 0))
    # }}}
dobayes_dsge()
