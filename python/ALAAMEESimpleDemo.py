#
# File:    ALAAMEESimpleDemo.py
# Author:  Alex Stivala
# Created: Februrary 2020
#
"""Simple demonstration implementation of the Equilibrium Expectation algorithm
 for estimation of Autologistic Actor Attribute Model (ALAAM) parameters.

 The EE algorithm is described in:

    Byshkin M, Stivala A, Mira A, Robins G, Lomi A 2018 "Fast
    maximum likelihood estimation via equilibrium expectation for
    large network data". Scientific Reports 8:11509
    doi:10.1038/s41598-018-29725-8


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
from basicALAAMsampler import basicALAAMsampler,sampler_m


#
# Constants
#
THETA_PREFIX = 'theta_values_' # prefix for theta output filename
DZA_PREFIX = 'dzA_values_'     # prefix for dzA output filename



def algorithm_S(G, A, changestats_func_list, M1, theta_outfile):
    """

     Algorithm S

     Parameters:
        G                   - Graph object for graph to estimate
        A                   - vector of 0/1 outcome variables for ALAAM
        changestat_func_v   - vector of change statistics funcions
        M1                  - number of iterations of Algorithm S
        theta_outfile       - open for write file to write theta values

     Returns:
       tuple with:
         theta               - numpy vector of theta values at end
         Dmean               - derivative estimate value at end

    """
    ACA = 0.1 # multiplier of da to get K1A step size multiplier
    n = len(changestats_func_list)
    theta = np.zeros(n)
    D0 = np.zeros(n)
    for t in xrange(M1):
        accepted = 0
        (acceptance_rate,
         changeTo1ChangeStats,
         changeTo0ChangeStats) = basicALAAMsampler(G, A,
                                              changestats_func_list, theta,
                                              performMove = False)
        dzA = changeTo0ChangeStats - changeTo1ChangeStats
        dzAmean = dzA / sampler_m
        sumChangeStats = changeTo1ChangeStats + changeTo0ChangeStats
        D0 += dzA**2 # 1/D0 is squared derivative
        da = np.zeros(n)
        for l in xrange(n):
            if (sumChangeStats[l] != 0):
                da[l] = ACA  / sumChangeStats[l]**2
        theta_step = np.sign(dzAmean) * da * dzA**2
        MAXSTEP = 0.1 # limit maximum step size
        theta_step = np.where(theta_step > MAXSTEP, MAXSTEP, theta_step)
        theta += theta_step
        theta_outfile.write(str(t-M1) + ' ' + ' '.join([str(x) for x in theta])
                            + ' ' + str(acceptance_rate) + '\n')
    Dmean = sampler_m / D0
    return(theta, Dmean)
        

def algorithm_EE(G, A, changestats_func_list, theta, D0,
                 Mouter, M, theta_outfile, dzA_outfile):
    """
    Algorithm EE

    Parameters:
       G                   - Graph object for graph to estimate
       A                   - vector of 0/1 outcome variables for ALAAM
       changestats_func_list-list of change statistics funcions
       theta               - corresponding vector of initial theta values
       D0                  - corresponding vector of inital D0 from Algorithm S
       Mouter              - iterations of Algorithm EE (outer loop)
       M                   - iterations of Algorithm EE (inner loop)
       theta_outfile       - open for write file to write theta values
       dzA_outfile         - open for write file to write dzA values

     Returns:
         numpy vector of theta values at end

    """
    ACA = 1e-09    # multiplier of D0 to get step size multiplier da (K_A)
    compC = 1e-02  # multiplier of sd(theta)/mean(theta) to limit theta variance
    n = len(changestats_func_list)
    dzA = np.zeros(n)  # zero outside loop, dzA accumulates in loop
    t = 0
    for touter in xrange(Mouter):
        thetamatrix = np.empty((M, n)) # rows theta vectors, 1 per inner iter
        for tinner in xrange(M):
            accepted = 0
            (acceptance_rate,
             changeTo1ChangeStats,
             changeTo0ChangeStats) = basicALAAMsampler(G, A,
                                                  changestats_func_list, theta,
                                                  performMove = True)
            dzA += changeTo1ChangeStats - changeTo0ChangeStats  # dzA accumulates here
            da = D0 * ACA
            theta_step = -np.sign(dzA) * da * dzA**2
            theta += theta_step
            thetamatrix[tinner,] = theta
            t += 1
        theta_outfile.write(str(t) + ' ' + ' '.join([str(x) for x in theta]) + 
                                ' ' + str(acceptance_rate) + '\n')
        dzA_outfile.write(str(t) + ' ' + ' '.join([str(x) for x in dzA]) + '\n')
        thetamean = np.mean(thetamatrix, axis = 0) # mean theta over inner loop
        thetasd   = np.std(thetamatrix, axis = 0)  # standard deviation
        thetamean = np.where(np.abs(thetamean) < 1, np.ones(n), thetamean) # enforce minimum magnitude 1 to stop sticking at zero
        DD = thetasd / np.abs(thetamean)
        D0 *= compC / DD # to limit size of fluctuations in theta (see S.I.)
        
    return theta

#-------------------------------------------------------------------------------


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
    Write output to ifd_theta_values_<basename>.txt and
                    ifd_dzA_values_<basename>.txt
    where <basename> is the baesname of edgelist filename e..g
    if edgelist_filename is edges.txt then ifd_theta_values_edges.txt
    and ifd_dzA_values_edges.txt
    WARNING: these files are overwritten.
    """
    assert(len(param_func_list) == len(labels))
    basename = os.path.splitext(os.path.basename(edgelist_filename))[0]
    THETA_OUTFILENAME = THETA_PREFIX + basename + os.extsep + 'txt'
    DZA_OUTFILENAME = DZA_PREFIX + basename  + os.extsep + 'txt'

    G = Graph(edgelist_filename, binattr_filename, catattr_filename)

    outcome_binvar = map(int, open(outcome_bin_filename).read().split()[1:])
    assert(len(outcome_binvar) == G.numNodes())
    A = outcome_binvar

    assert( all([x in [0,1] for x in A]) )
    
    print 'graph density = ', G.density()
    print 'positive outcome attribute = ', (float(sum(A))/len(A))*100.0, '%'
    
    # steps of Alg 1    
    M1 = 20

    Mouter = 500 # outer iterations of Algorithm EE
    Msteps = 100 # number of inner steps of Algorithm EE

    print 'M1 = ', M1, ' Mouter = ', Mouter, ' Mstesp = ', Msteps
    
    theta_outfile = open(THETA_OUTFILENAME, 'w',1) # 1 means line buffering
    theta_outfile.write('t ' + ' '.join(labels) + ' ' + 'AcceptanceRate' + '\n')
    print 'Running Algorithm S...',
    start = time.time()
    (theta, Dmean) = algorithm_S(G, A, param_func_list, M1, theta_outfile)
    print time.time() - start, 's'
    print 'after Algorithm S:'
    print 'theta = ', theta
    print 'Dmean = ', Dmean
    dzA_outfile = open(DZA_OUTFILENAME, 'w',1)
    dzA_outfile.write('t ' + ' '.join(labels) + '\n')
    print 'Running Algorithm EE...',
    start = time.time()
    theta = algorithm_EE(G, A, param_func_list, theta, Dmean,
                         Mouter, Msteps, theta_outfile, dzA_outfile)
    print time.time() - start, 's'
    theta_outfile.close()
    dzA_outfile.close()
    print 'at end theta = ', theta

    

def run_example():
    """
    example run on simulated 500 node network
    """
    run_on_network_attr(
        '../examples/simulated_n500_bin_cont2/n500_kstar_simulate12750000.txt',
        [changeDensity, changeActivity, changeContagion, changeoOb, changeoOc],
        ["Density", "Activity", "Contagion", "Binary", "Continuous"],
        '../examples/simulated_n500_bin_cont2/sample-n500_bin_cont6700000.txt',
        '../examples/simulated_n500_bin_cont2/binaryAttribute_50_50_n500.txt',
        '../examples/simulated_n500_bin_cont2/continuousAttributes_n500.txt'
    )
