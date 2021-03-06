#!/usr/bin/env python3
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')


# Definitions:{{{1
def getparamexogdict():
    """
    This dictionary contains all variables that are just numbers i.e. they are not determined by other parameter values.
    This is important since I use this function to get param values when initialising the initial function but then delete parameters that I want to estimate. So if I include variables that are functions of parameters that get deleted prior to estimation, these variables will have the wrong value.
    """
    paramssdict = {'ALPHA': 0.3, 'BETA': 0.95, 'DELTA': 0.1, 'RHO': 0.9, 'SIGMA': 0.1, 'ME_c': 0.01, 'ME_y': 0.01}
    return(paramssdict)

def addparamendogdict(p):
    """
    Now, I add all endogenous parameters to paramssdict (the exogenous parameters).
    Thus, I include any parameters that depend on other parameters.
    I.e. this is where I would add BETA = 1 - ALPHA.
    """
    p['a'] = 1
    p['k'] = ((p['ALPHA'] * p['a'])/(1/p['BETA'] - 1 + p['DELTA']))**(1/(1-p['ALPHA']))
    p['y'] = p['a'] * p['k'] ** p['ALPHA']
    p['c'] = p['y'] - p['DELTA'] * p['k']

    return(p)


def getestimatevars():
    estimatevars = ['ALPHA', 'DELTA', 'ME_c', 'ME_y']
    return(estimatevars)


def getbounddicts(estimatevars):
    lowerbounddict = {'ALPHA': 0.00001, 'DELTA': 0, 'ME_c': 0, 'ME_y': 0}
    upperbounddict = {'ALPHA': 0.99999, 'DELTA': 1, 'ME_c': 0.05, 'ME_y': 0.05}

    return(lowerbounddict, upperbounddict)

# Basic Model:{{{1
def getbasicmodel(paramssdict):
    import numpy as np

    # returndict
    r = {}

    r['controls'] = ['c', 'y']
    r['states'] = ['a', 'k']
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import getposdicts
    r['stateposdict'], r['controlposdict'], r['allposdict'] = getposdicts(r['states'], r['controls'])

    # matrices for later
    r['Et_eqs_string'] = [
    '1/c - BETA * 1/c_p*(ALPHA*a_p*k_p**(ALPHA-1) + (1-DELTA))'
    ,
    'c + k_p - y - (1-DELTA)*k'
    ,
    'log(a_p)-RHO*log(a)'
    ,
    'y - a * k**ALPHA'
    ]

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import convertstringlisttosympy
    r['Et_eqs'] = convertstringlisttosympy(r['Et_eqs_string'])

    # check variables specified correctly
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import checkeqs
    checkeqs(r['Et_eqs'], r['controls'] + r['states'], params = list(paramssdict))

    # get varssdict in terms of parameters
    r['varssdict'] = addparamendogdict(paramssdict)

    # convert vars and varssdict
    # convert all states and controls into logs (unusual not to have levels vars)
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import convertlogvariables
    r['Et_eqs'], r['varssdict'] = convertlogvariables(r['Et_eqs'], samenamelist = r['states'] + r['controls'], varssdict = r['varssdict'])

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import dsgeanalysisdiff
    r['fx'], r['fxp'], r['fy'], r['fyp'] = dsgeanalysisdiff(r['Et_eqs'], r['states'], r['controls'])

    return(r)


def addABCD(r):
    """
    Add the ABCD matrices for the state space form.
    """
    import numpy as np

    # add theoretical statespace
    r['B'] = np.zeros([len(r['stateposdict']), 1])
    r['B'][r['stateposdict']['a'], 0] = r['varssdict']['SIGMA']

    r['D'] = np.zeros([len(r['controlposdict']), 1])

    # now add statespace for only observed variables
    r['observedy'] = ['c', 'y']

    # match the rows for C2 to the observed vars from C
    r['C2rows'] = [r['controlposdict'][var] for var in r['observedy']]
    r['C2'] = r['C'][r['C2rows'], :]

    # add measurement error
    r['D2'] = np.zeros([len(r['observedy']), len(r['observedy'])])
    for i in range(0, len(r['observedy'])):
        r['D2'][i, i] = r['varssdict']['ME_' + r['observedy'][i]]

    # adjust dimensions of B2 and D2 to account for all shocks
    r['B2'] = np.concatenate((r['B'], np.zeros(np.shape(r['D2']))), axis = 1)
    r['D2'] = np.concatenate((np.zeros(np.shape(r['B'])), r['D2']), axis = 1)

    return(r)


# Model with all variables specified:{{{1
def allparams_solve(paramssdict):
    # returndict
    r = getbasicmodel(paramssdict)

    # get replacedict
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import getfullreplacedict
    r['replacedict'] = getfullreplacedict([r['varssdict']], variables = r['states'] + r['controls'])

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import numeval_full
    r['nfx'], r['nfxp'], r['nfy'], r['nfyp'] = numeval_full(r['fx'], r['fxp'], r['fy'], r['fyp'], r['replacedict'])

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import gxhx
    r['C'], r['A'] = gxhx(r['nfx'], r['nfxp'], r['nfy'], r['nfyp'])

    return(r)


# Getting data:{{{1
def getrealdata():
    import numpy as np
    import pandas
    import statsmodels.api as sm

    # getting y
    df = pandas.read_csv(__projectdir__ / Path('me/bayes/data/gdp_fred.csv'))

    cycle, trend = sm.tsa.filters.hpfilter(df[[1]], lamb = 1600)
    stationary = df[[1]] / trend

    logy = np.log(stationary)

    # getting c
    df = pandas.read_csv(__projectdir__ / Path('me/bayes/data/pce_fred.csv'))

    cycle, trend = sm.tsa.filters.hpfilter(df[[1]], lamb = 1600)
    stationary = df[[1]] / trend

    logc = np.log(stationary)

    Y = np.concatenate((logc, logy), axis = 1)

    return(Y)
    

    
def getsimdata():
    paramssdict = getparamexogdict()
    r = allparams_solve(paramssdict)
    r = addABCD(r)

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/statespace')))
    from statespace_func import statespace_simdata
    X, Y, v = statespace_simdata(r['A'], r['B2'], r['C2'], r['D2'], 1000)

    return(Y)
    

# Bayesian Setup:{{{1
def getnumderivs_unknownparams(paramssdict, estimatevars):
    """
    paramssdict is the value of parameters which are predetermined.
    estimatevars is the name of parameters which will be estimated (so a list of strings).
    """
    import numpy as np
    import sympy

    # adjust paramssdict so doesn't include estimatevars
    for var in estimatevars:
        paramssdict[var] = sympy.Symbol(var)

    # returndict
    r = getbasicmodel(paramssdict)

    # remove unknown values for varssdict so not replacing unnecessary values:
    r['varssdict2'] = r['varssdict'].copy()
    for var in estimatevars:
        if var in r['varssdict2']:
            del r['varssdict2'][var]

    # get replacedict
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import getfullreplacedict
    r['replacedict'] = getfullreplacedict([r['varssdict2']], variables = r['states'] + r['controls'])

    # replace non-estimatevars
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import numeval_partial
    fx, fxp, fy, fyp = numeval_partial(r['fx'], r['fxp'], r['fy'], r['fyp'], r['replacedict'])

    # convert to function
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgediff_func import numeval_convertfunc
    r['fx_f'], r['fxp_f'], r['fy_f'], r['fyp_f'] = numeval_convertfunc(fx, fxp, fy, fyp, estimatevars)

    return(r)


def getloglfunc(estimatevars, y):
    import numpy as np
    import sympy

    paramssdict = getparamexogdict()
    r = getnumderivs_unknownparams(paramssdict, estimatevars)

    def loglfunc(params, r = r):
        
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from dsge_bkdiscrete_func import gxhx
        r['C'], r['A'] = gxhx(r['fx_f'](*params), r['fxp_f'](*params), r['fy_f'](*params), r['fyp_f'](*params))

        # add to varssdict for addABCD function
        for i in range(0, len(estimatevars)):
            r['varssdict'][estimatevars[i]] = params[i]
        
        r = addABCD(r)

        # get kalman filter
        sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/statespace')))
        from statespace_func import kalmanfilter
        x_t_tm1, P_t_tm1, x_t_t, P_t_t, y_t_tm1, Q_t_tm1, R_t_tm1 = kalmanfilter(y, r['A'], r['B2'], r['C2'], r['D2'])

        # get log likelihood
        sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/statespace')))
        from statespace_func import logl_prop_kalmanfilter
        ll = logl_prop_kalmanfilter(y, y_t_tm1, Q_t_tm1)

        return(ll)

    return(loglfunc)


# MLE Analysis:{{{1
def getmax(printdetails = False):
    """
    I used this when trying to solve an Uribe problem set.
    I've included it here for reference as to how it can be applied but I don't actually apply it.
    """
    y = getrealdata()
    estimatevars = getestimatevars()

    logl_func = getloglfunc(estimatevars, y)

    lowerbounddict, upperbounddict = getbounddicts(estimatevars)
    lowerboundlist = [lowerbounddict[var] for var in estimatevars]
    upperboundlist = [upperbounddict[var] for var in estimatevars]

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import boundedrandommle
    boundedrandommle(logl_func, lowerboundlist, upperboundlist, outputfolder = 'temp/max/', printdetails = printdetails, continuefile = True)


# Bayesian Analysis:{{{1
def getdists(printdetails = False, numiterations = 1e5, savefile = None, realdata = True):
    if realdata is True:
        y = getrealdata()
    else:
        y = getsimdata()

    estimatevars = getestimatevars()

    logl_func = getloglfunc(estimatevars, y)

    scaledict = {}
    startvaldict = {}
    lowerbounddict, upperbounddict = getbounddicts(estimatevars)

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import metropolis_bounds_getdicts
    lowerboundlist, upperboundlist, scalelist, startvallist = metropolis_bounds_getdicts(estimatevars, lowerbounddict, upperbounddict, scaledict, startvaldict)

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import metropolis_bounds_do
    metropolis_bounds_do(logl_func, lowerboundlist, upperboundlist, scalelist, startvallist, numiterations = numiterations, printdetails = printdetails, logposterior = True, savefile = savefile)


def getdists_poolf_real(savefile):
    getdists(savefile = savefile, numiterations = 500, printdetails = True)


def getdists_poolf_sim(savefile):
    getdists(savefile = savefile, numiterations = 500, printdetails = True, realdata = False)


def getdists_multiprocessing(numprocesses = None, deleteoldresults = True, realdata = True):
    """
    Run getdists function using multiprocessing.
    """
    if realdata is True:
        poolf = getdists_poolf_real
        savefolder = __projectdir__ / Path('me/bayes/temp/dist_real/')
    else:
        poolf = getdists_poolf_sim
        savefolder = __projectdir__ / Path('me/bayes/temp/dist_sim/')

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import getdists_pool
    getdists_pool(poolf, savefolder, numprocesses = numprocesses, deleteoldresults = deleteoldresults)


# Analysis Post Parameter Estimation:{{{1
def analysebayes(realdata = True):
    """
    If realdata is True, use mean from real data distributions.
    If realdata is False, use mean from sim data distributions.
    """
    import numpy as np

    if realdata is True:
        savefolder = __projectdir__ / Path('me/bayes/temp/dist_real/')
    else:
        savefolder = __projectdir__ / Path('me/bayes/temp/dist_sim/')

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/')))
    from bayesian_func import getdistfromfolder
    data = getdistfromfolder(savefolder)
    means = np.mean(data, axis = 0)

    print('Mean values:')
    print(means)

    estimatevars = getestimatevars()
    paramssdict = getparamexogdict()
    for i in range(0, len(estimatevars)):
        paramssdict[estimatevars[i]] = means[i]

    r = allparams_solve(paramssdict)
    r = addABCD(r)

    sys.path.append(str(__projectdir__ / Path('submodules/python-math-func/statespace')))
    from statespace_func import ABCD_convert
    bigA, bigB = ABCD_convert(r['A'], r['B'], r['C'], r['D'])
    # print(bigA)
    # print(bigB)






# Test:{{{1
def testfullmodel():
    # Basic model:
    r = allparams_solve(getparamexogdict())
    print(r['A'])
    



def testlogl():
    # Log Likelihood for specific parameters
    estimatevars = getestimatevars()
    y = getsimdata()
    
    # log likelihood for several values
    logl_f = getloglfunc(estimatevars, y)
    ll = logl_f([0.3, 0.1, 0.01, 0.01])
    print(ll)
    ll = logl_f([0.31, 0.1, 0.01, 0.01])
    print(ll)


def testdists():
    # General distribution simulation
    getdists(printdetails = True, numiterations = 5)
    
def testquick():
    
    # print(getrealdata())
    print(getsimdata())



