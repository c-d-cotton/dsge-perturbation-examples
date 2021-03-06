#!/usr/bin/env python3
"""
Simple examples of different methods of how to solve DSGE models with an occasionally binding constraint (the constraint here is the ZLB).
"""
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/../')

import copy
import numpy as np

# Defaults:{{{1
shocksddict_default = {'e_rn': 0.1}
shockpath_default = np.array([[-0.1, -0.1] + [0] * 29]).transpose()
shocks_default = ['e_rn']
simperiods_default = len(shockpath_default)

# Inputdict:{{{1
def getp_default():
    """
    Get default paramssdict.
    """
    # basic parameters
    p = {'BETA': 0.98, 'KAPPA': 1, 'GAMMA': 1, 'PHIpi': 1.5, 'PHIy': 0}

    # parameters for natural rate process
    p['RHO_Rn'] = 0

    # steady state nominal rate
    # note that this approximation only makes sense when Pistar = 1
    p['I_ss'] = 1/p['BETA'] * 1

    # monetary rule
    p['monetary'] = 'taylor' # alternative is zlb

    return(p)


def getinputdict(p = None, simshock = False, mainvars = None):
    if p is None:
        p = getp_default()
    
    inputdict = {}
    inputdict['equations'] = [
    'Pihat = KAPPA * Xhat + BETA * Pihat_p'
    ,
    'Xhat = Xhat_p - 1/GAMMA*(Ihat - Pihat_p - Rnhat_tm1_p)'
    ,
    'Rnhat_tm1_p = RHO_Rn * Rnhat_tm1 + e_rn'
    ]

    if p['monetary'] == 'taylor':
        inputdict['equations'].append('Ihat = PHIpi * Pihat + PHIy * Xhat')
    elif p['monetary'] == 'zlb':
        inputdict['equations'].append('Ihat = -log(I_ss)')
    elif p['monetary'] == 'taylor-zlb':
        inputdict['equations'].append('Ihat = max(PHIpi * Pihat + PHIy * Xhat, -log(I_ss))')
    else:
        raise ValueError('Monetary rule not specified correctly.')
        

    inputdict['paramssdict'] = p

    inputdict['controls'] = ['Xhat', 'Pihat', 'Ihat']
    inputdict['states'] = ['Rnhat_tm1']
    inputdict['shocks'] = shocks_default

    inputdict['loglineareqs'] = True

    if mainvars is not None:
        inputdict['mainvars'] = mainvars

    return(inputdict)


def test_dsgenormal():
    """
    Run basic model to verify working.
    """
    inputdict = getinputdict()

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsge_bkdiscrete_func import discretelineardsgefull
    discretelineardsgefull(inputdict)


# Regime without Shock:{{{1
def tryregimenoshock_regime(p = None):
    """
    Model a regime change using the standard regime change method
    """
    if p is None:
        p = getp_default()

    mainvars = ['Xhat', 'Pihat', 'Ihat']

    p_nozlb = copy.deepcopy(p)
    p_nozlb['monetary'] = 'taylor'
    inputdict_nozlb = getinputdict(p_nozlb, mainvars = mainvars)

    p_zlb = copy.deepcopy(p)
    p_zlb['monetary'] = 'zlb'
    inputdict_zlb = getinputdict(p_zlb, mainvars = mainvars)

    # try out regimes
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from regime_func import regimechange
    regimechange([inputdict_nozlb, inputdict_zlb], [1] * 10 + [0] * 10, irf = True)


# Try Regime Change and a Shock:{{{1
def tryregimeshock(p = None):
    """
    In this method, I actually specify the periods in which the zlb binds and when it does not.
    This function is a little limited since, due to the solution method I use, I can only specify a shock in the initial period.
    """
    if p is None:
        p = getp_default()

    p_nozlb = copy.deepcopy(p)
    p_nozlb['monetary'] = 'taylor'
    inputdict_nozlb = getinputdict(p_nozlb)

    p_zlb = copy.deepcopy(p)
    p_zlb['monetary'] = 'zlb'
    inputdict_zlb = getinputdict(p_zlb)

    # try out regimes
    epsilon0 = np.array([[-0.2]])
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from regime_func import regimechange
    regimechange([inputdict_nozlb, inputdict_zlb], [1,1,1,1,0,0,0,0], irf = True, epsilon0 = epsilon0)


# Dynare Perfect Foresight:{{{1
def dynare_simul(p = None, run = False):
    """
    Use the Dynare simul method to solve given the constraint.
    This method implies that at time t, agents anticipate the values of future shocks.
    Thus, this method does not produce the same results as occbin which assumes that agents only know the values of shocks today.
    """
    if p is None:
        p = getp_default()

    p['monetary'] = 'taylor-zlb'
    inputdict = getinputdict(p)

    inputdict['savefolder'] = os.path.join(__projectdir__, 'regimes/temp/perfect_foresight/')

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    # add shock path
    inputdict['shockpath'] = shockpath_default

    # generate python2dynare
    inputdict['python2dynare_simulation'] = 'simul(periods = 20);'
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from python2dynare_func import python2dynare_inputdict
    python2dynare_inputdict(inputdict)

    # run dynare
    if run is True:
        # run dynare
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from python2dynare_func import rundynare_inputdict
        rundynare_inputdict(inputdict)
        # get irfs
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from python2dynare_func import getirfs_dynare_inputdict
        getirfs_dynare_inputdict(inputdict)


def dynare_extendedpath(p = None, run = False):
    """
    Solve model by extended path.
    The extended path method in Dynare assumes agents at t only know shocks at t.

    If I could input the shockpath, this should yield the same as occbin/myoccbin.
    But I don't see to be able to do that - I have to specify the shock s.d. instead.
    """
    if p is None:
        p = getp_default()

    p['monetary'] = 'taylor-zlb'
    inputdict = getinputdict(p)

    inputdict['savefolder'] = os.path.join(__projectdir__, 'regimes/temp/extendedpath/')

    # add model
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from dsgesetup_func import getmodel_inputdict
    inputdict = getmodel_inputdict(inputdict) 

    # add shock path
    inputdict['shocksddict'] = copy.deepcopy(shocksddict_default)

    # generate python2dynare
    inputdict['python2dynare_simulation'] = 'extended_path(periods = 20,solver_periods=100);'
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from python2dynare_func import python2dynare_inputdict
    python2dynare_inputdict(inputdict)

    # run dynare
    if run is True:
        # run dynare
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from python2dynare_func import rundynare_inputdict
        rundynare_inputdict(inputdict)
        # get irfs
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from python2dynare_func import getirfs_dynare_inputdict
        getirfs_dynare_inputdict(inputdict)

# dynare_extendedpath(run = True)
# Occbin:{{{1
def occbin_test(p = None):
    """
    Call Guerrieri Iacoviello Occbin Matlab code
    Need to specify dsge-perturbation/paths/occbin.txt
    """
    if p is None:
        p = getp_default()

    p_nozlb = copy.deepcopy(p)
    p_nozlb['monetary'] = 'taylor'
    inputdict_nozlb = getinputdict(p_nozlb)

    p_zlb = copy.deepcopy(p)
    p_zlb['monetary'] = 'zlb'
    inputdict_zlb = getinputdict(p_zlb)

    shocks = shockpath_default

    # simperiods determines how many periods simulate forward and also length of IRF
    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from calloccbin_func import calloccbin_oneconstraint
    calloccbin_oneconstraint(inputdict_nozlb, inputdict_zlb, 'Ihat < -log(I_ss)', 'Ihat > -log(I_ss)', shocks, os.path.join(__projectdir__, 'regimes/temp/occbin/'), run = True, irf = True, simperiods = simperiods_default)

# Occbin-Like Functions:{{{1
def myoccbin_test(p = None, simshock = False):
    """
    Example of my code to run Occbin.
    This yields the same as Occbin in simple models (like this one).
    In more complex models, the regime updating can work differently so the results might not be identical.
    """
    if p is None:
        p = getp_default()

    p_nozlb = copy.deepcopy(p)
    p_nozlb['monetary'] = 'taylor'
    inputdict_nozlb = getinputdict(p_nozlb, simshock = simshock)

    p_zlb = copy.deepcopy(p)
    p_zlb['monetary'] = 'zlb'
    inputdict_zlb = getinputdict(p_zlb, simshock = simshock)

    if simshock is True:
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from getshocks_func import getshocksddict
        shocksddict = getshocksddict(shocks_default, shocksddict = copy.deepcopy(shocksddict_default))
        sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
        from getshocks_func import getshockpath
        shockpath = getshockpath(simperiods_default, shocks_default, shocksddict)
    else:
        shockpath = shockpath_default

    sys.path.append(str(__projectdir__ / Path('submodules/dsge-perturbation/')))
    from myoccbin_func import myoccbin
    myoccbin(inputdict_nozlb, inputdict_zlb, 'Ihat > -log(I_ss)', shockpath, savefolder = os.path.join(__projectdir__, 'regimes/temp/occbin2/'), printdetails = True, printvars = ['Ihat'], irf = True, printprobbind = True, regimeupdatefunc = 'occbin')
myoccbin_test()
