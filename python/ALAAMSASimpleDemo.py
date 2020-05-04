#
# File:    ALAAMSASimpleDemo.py
# Author:  Alex Stivala
# Created: May 2020
#
"""Simple demonstration implementation of the Robbins-Monro Stochastic
 Approximation algorithm for estimation of Autologistic Actor
 Attribute Model (ALAAM) parameters.

 The Robbins-Monro algorithm for ERGM (rather than ALAAM) is described in:

  Snijders, T. A. (2002). Markov chain Monte Carlo estimation of
  exponential random graph models. Journal of Social Structure, 3(2),
  1-40.

 The ALAAM is described in:

  G. Daraganova and G. Robins. Autologistic actor attribute models. In
  D. Lusher, J. Koskinen, and G. Robins, editors, Exponential Random
  Graph Models for Social Networks, chapter 9, pages 102-114. Cambridge
  University Press, New York, 2013.

  G. Robins, P. Pattison, and P. Elliott. Network models for social
  influence processes. Psychometrika, 66(2):161-189, 2001.


 The example data is described in:

  Stivala, A. D., Gallagher, H. C., Rolls, D. A., Wang, P., & Robins,
  G. L. (2020). Using Sampled Network Data With The Autologistic Actor
  Attribute Model. arXiv preprint arXiv:2002.00849.

"""

import time
import os
import random
import math
import numpy as np         # used for matrix & vector data types and functions

from Graph import Graph
from changeStatisticsALAAM import *
from stochasticApproximation import stochasticApproximation



def run_on_network_attr(edgelist_filename, param_func_list, labels,
                        outcome_bin_filename,
                        binattr_filename=None,
                        catattr_filename=None):
    """
    Run on specified network with binary and/or categorical attributes.
    
    Parameters:
         edgelist_filename - filename of Pajek format edgelist 
         param_func_list   - list of change statistic functions corresponding
                             to parameters to estimate
         labels            - list of strings corresponding to param_func_list
                             to label output (header line)
         outcome_bin_filename - filename of binary attribute (node per line)
                                of outcome variable for ALAAM
         binattr_filename - filename of binary attributes (node per line)
                            Default None, in which case no binary attr.
         catattr_filename - filename of categorical attributes (node per line)
                            Default None, in which case no categorical attr.

    Write output to stdout.
    """
    assert(len(param_func_list) == len(labels))

    G = Graph(edgelist_filename, binattr_filename, catattr_filename)

    outcome_binvar = map(int, open(outcome_bin_filename).read().split()[1:])
    assert(len(outcome_binvar) == G.numNodes())
    A = outcome_binvar

    assert( all([x in [0,1] for x in A]) )
    
    print 'graph density = ', G.density()
    print 'positive outcome attribute = ', (float(sum(A))/len(A))*100.0, '%'

    theta = np.zeros(len(param_func_list))
    
    print 'Running stochastic approximation...',
    start = time.time()
    theta = stochasticApproximation(G, A, param_func_list, theta) 

    print time.time() - start, 's'
    print 'at end theta = ', theta

    

def run_example():
    """
    example run on simulated 500 node network
    """
    run_on_network_attr(
        '../data/simulated_n500_bin_cont2/n500_kstar_simulate12750000.txt',
        [changeDensity, changeActivity, changeContagion, changeoOb, changeoOc],
        ["Density", "Activity", "Contagion", "Binary", "Continuous"],
        '../data/simulated_n500_bin_cont2/sample-n500_bin_cont6700000.txt',
        '../data/simulated_n500_bin_cont2/binaryAttribute_50_50_n500.txt',
        '../data/simulated_n500_bin_cont2/continuousAttributes_n500.txt'
    )
