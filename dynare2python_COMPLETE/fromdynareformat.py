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

def main():
    """
    Direct shocks.
    """
    inputdict = {}
    inputdict['dynareequations'] = [
    '1/c - BETA * 1/c(+1)*(ALPHA*a(+1)*k(0)**(ALPHA-1) + (1-DELTA))'
    ,
    'c + k - a*k(-1)**ALPHA - (1-DELTA)*k(-1)'
    ,
    'log(a)-RHO*log(a(-1)) - epsilon_a'
    ]

    inputdict['paramssdict'] = {'ALPHA': 0.3, 'BETA': 0.95, 'DELTA': 0.1, 'RHO': 0.9}

    p = inputdict['paramssdict']
    v = {}
    v['am1'] = 1
    v['a'] = 1
    v['k'] = ((p['ALPHA'] * v['a'])/(1/p['BETA'] - 1 + p['DELTA']))**(1/(1-p['ALPHA']))
    v['c'] = v['a'] * v['k'] ** p['ALPHA'] - p['DELTA'] * v['k']

    inputdict['dynarevariables'] = ['a', 'k', 'c']
    inputdict['shocks'] = ['epsilon_a']
    inputdict['savefolder'] = __projectdir__ / Path('me/basic/short/temp/')
    inputdict['dynarevarssdict'] = v

    inputdict['dynarelogvars'] = ['a', 'k', 'c']

    importattr(__projectdir__ / Path('submodules/dsge-perturbation/dsge_bkdiscrete_func.py'), 'discretelineardsgefull')(inputdict)

# Run:{{{1
main()
