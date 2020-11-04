#!/usr/bin/env python3
"""
I embed the standard deviation of the shocks into the equations do I don't need to define Omega here.

Basic RBC model.
The econometrician observes ygrowth and cgrowth with some error. If we don't have observation error then we can only use one of ygrowth and cgrowth since they become non-independent.
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

import functools
import numpy as np

# Basic Setup:{{{1
def getparamssdict(p = None):
    """
    Add parameters.
    """
    if p is None:
        p = {}
    p_defaults = {'ALPHA': 0.3, 'DELTA': 0.1, 'RHO': 0.9, 'sigma_a': 0.1, 'BETA': 0.95, 'sigma_cobs': 0.001, 'sigma_yobs': 0.001}
    for param in p_defaults:
        if param not in p:
            p[param] = p_defaults[param]

    return(p)


def getvarssdict(p):
    v = {}
    v['Am1'] = 1
    v['A'] = v['Am1']
    v['K'] = ((p['ALPHA'] * v['A'])/(1/p['BETA'] - 1 + p['DELTA']))**(1/(1-p['ALPHA']))
    v['C'] = v['A'] * v['K'] ** p['ALPHA'] - p['DELTA'] * v['K']
    v['Y'] = v['A'] * v['K'] ** p['ALPHA']

    v['Ym1'] = v['Y']
    v['Ygr'] = 1
    v['Cm1'] = v['C']
    v['Cgr'] = 1

    return(v)


def getinputdict_noparamssdict(loglineareqs = True):
    """
    This is the inputdict without the steady state included.
    """
    inputdict = {}

    inputdict['controls'] = ['C', 'A', 'Y', 'Ygr', 'Cgr']
    inputdict['states'] = ['Am1', 'K', 'Ym1', 'Cm1']
    inputdict['shocks'] = ['epsilon_a', 'epsilon_cobs', 'epsilon_yobs']

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
        inputdict['equations'].append('Am1_p = RHO * Am1 + sigma_a * epsilon_a')
    else:
        inputdict['equations'].append('log(Am1_p) = RHO * log(Am1) + sigma_a * epsilon_a')

    if loglineareqs is True:
        inputdict['equations'].append('Y = A + ALPHA * K')
    else:
        inputdict['equations'].append('Y = A * K ** ALPHA')

    if loglineareqs is True:
        inputdict['equations'].append('Ygr = Y - Ym1 + sigma_yobs * epsilon_yobs')
    else:
        inputdict['equations'].append('Ygr = Y / Ym1 * exp(epsilon_yobs) ** sigma_yobs')

    if loglineareqs is True:
        inputdict['equations'].append('Ym1_p = Y')
    else:
        inputdict['equations'].append('Ym1_p = Y')

    if loglineareqs is True:
        inputdict['equations'].append('Cgr = C - Cm1 + sigma_cobs * epsilon_cobs')
    else:
        inputdict['equations'].append('Cgr = C / Cm1 * exp(epsilon_cobs) ** sigma_cobs')

    if loglineareqs is True:
        inputdict['equations'].append('Cm1_p = C')
    else:
        inputdict['equations'].append('Cm1_p = C')

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
    v = getvarssdict(p)

    p.update(v)

    return(p)


def getrealdata():
    import pandas as pd
    import statsmodels.api as sm

    # getting y

    dftemp = importattr(__projectdir__ / Path('submodules/python-data-func/fred_func.py'), 'loadfred')(__projectdir__ / Path('bayes/data/fred/GDPC1.csv'), 'Q', varname = 'real_gdp_billions')
    # rearrange columns
    dfq = dftemp[['time', 'real_gdp_billions']]

    dftemp = importattr(__projectdir__ / Path('submodules/python-data-func/fred_func.py'), 'loadfred')(__projectdir__ / Path('bayes/data/fred/PCECC96.csv'), 'Q', varname = 'real_cons_billions')
    dfq = dfq.merge(dftemp, on = ['time'], how = 'outer')

    def detrendquarterlyvar(series):
        # remove empty values
        series = series.dropna()

        # compute HP-filter for quarterly data
        cycle, trend = sm.tsa.filters.hpfilter(series, lamb = 1600)

        # detrend
        stationary = series / trend

        return(stationary)

    # detrend series to remove growth which I didn't include in the model
    dfq['Y'] = detrendquarterlyvar(dfq['real_gdp_billions'])
    dfq['C'] = detrendquarterlyvar(dfq['real_cons_billions'])

    # define Ygr = Y / Ym1, Cgr = C / Cm1 which are the variables we match in the data
    # need to take logs since I'm matching log-linearized variables
    dfq['Ygr'] = np.log(dfq['Y']) - np.log(dfq['Y'].shift(1))
    dfq['Cgr'] = np.log(dfq['C']) - np.log(dfq['C'].shift(1))

    # limit to 1960Q1 - 1999Q4
    dfq = dfq[dfq['time'] >= 1960 * 4]
    dfq = dfq[dfq['time'] < 2000 * 4]

    # limit to only Ygr, Cgr
    dfq = dfq[['Ygr', 'Cgr']]

    dfq = dfq.to_numpy()

    return(dfq)
    

def getsimdata(varnames, numperiods = 100):
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
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/getshocks_func.py'), 'getshockpath_inputdict')(inputdict)

    # simulate path
    inputdict = importattr(__projectdir__ / Path('submodules/dsge-perturbation/simlineardsge_func.py'), 'simpathlinear_inputdict')(inputdict)

    data = inputdict['varpath'][:, [inputdict['stateshockcontrolposdict'][varnames[i]] for i in range(len(varnames))]]

    return(data)

    
def dobayes_dsge(usesimdata = False):
    # get same every time
    np.random.seed(41)

    # get likelihood function:{{{

    # get inputdict with fxe_f etc. functions
    inputdict = getinputdict_bayesian()

    # get replacedict function
    paramnames = ['RHO', 'BETA', 'ALPHA']
    getreplacedict_bayesian = functools.partial(getreplacedict_bayesian_aux, paramnames)

    # get data
    # in T x N format
    varnames = ['Ygr', 'Cgr']
    if usesimdata is True:
        data = getsimdata(varnames, numperiods = 160)
    else:
        data = getrealdata()

    # get log-likelihood function
    # input parameters into this function and return log-likelihood (without priors)
    loglikelihoodfunc = functools.partial(importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bayes_func.py'), 'getbayes_dsge_logl_aux'), inputdict, getreplacedict_bayesian, data, varnames)

    # }}}

    # get prior function and info:{{{
    # I impose a relatively strict prior on BETA (the second element) since otherwise Metropolis-Hastings picks a very high BETA
    priorlist_meansd = [['beta', 0.9, 0.05], ['normal', 0.95, 0.005], ['normal', 0.3, 0.05]]
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
    results = importattr(__projectdir__ / Path('submodules/python-math-func/bayesian_func.py'), 'metropolis_hastings')(posteriorfunc, scalelist, prior_means, 1000, lowerboundlist = prior_lbs, upperboundlist = prior_ubs, printdetails = True, logposterior = True, raiseerror = False)
    print(np.mean(np.array(results)[100: , :], axis = 0))
    # }}}


