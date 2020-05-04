#
# File:    stochasticApproximation.py
# Author:  Alex Stivala
# Created: May 2020
#
"""Simple demonstration implementation of the Robbins-Monro stochastic
 approximatino algorithm for estimation of Autologistic Actor
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

"""
import sys
import numpy as np         # used for matrix & vector data types and functions

from Graph import Graph
from changeStatisticsALAAM import *
from basicALAAMsampler import basicALAAMsampler



def stochasticApproximation(G, A, changestats_func_list, theta):
    """
    Robbins-Monro stochastic approximation to estimate ALAAM parameers.

    The Robbins-Monro algorithm for ERGM (rather than ALAAM) is described in:

     Snijders, T. A. (2002). Markov chain Monte Carlo estimation of
     exponential random graph models. Journal of Social Structure, 3(2),
     1-40.

    Parameters:
       G                   - Graph object for graph to estimate
       A                   - vector of 0/1 outcome variables for ALAAM
       changestats_func_list-list of change statistics funcions
       theta               - corresponding vector of initial theta values

     Returns:
         numpy vector of theta values at end (or None if degenerate model)

    """
    epsilon = np.finfo(float).eps
    
    n = len(changestats_func_list)

    # constants used in multiple phases
    #iterationInStep = 10 * G.numNodes()
    iterationInStep =  100

    # phase 1 constants
    phase1steps     = 7 + 3*n

    # phase 2 constants
    numSubphases  = 4
    a_initial     = 0.01

    # phase 3 constants
    phase3steps = 1000

    # Calculate observed statistics by summing change stats for each 1 variable
    Zobs = np.zeros(n)
    Acopy = np.zeros(len(A))
    for i in xrange(len(A)):
        if A[i] == 1:
            for l in xrange(n):
                Zobs[l] += changestats_func_list[l](G, Acopy, i)
            Acopy[i] = 1
    assert(np.all(Acopy == A))
    print 'Zobs = ', Zobs
    
    #
    # Phase 1: estimate covariance matrix
    #
    Zmatrix = np.empty((phase1steps, n)) # rows statistics Z vectors, 1 per step
    for i in xrange(phase1steps):
        accepted = 0
        (acceptance_rate,
         changeTo1ChangeStats,
         changeTo0ChangeStats) = basicALAAMsampler(G, A,
                                                   changestats_func_list,
                                                   theta,
                                                   performMove = True,
                                                   sampler_m = iterationInStep)
        Z = Zobs + changeTo1ChangeStats - changeTo0ChangeStats
        Zmatrix[i, ] = Z

    Zmean = np.mean(Zmatrix, axis=0)
    Zmean = np.reshape(Zmean, (1, len(Zmean))) # make it a row vector
    theta = np.reshape(theta, (1, len(theta)))
    print 'Zmean = ', Zmean
        
    #D = (1.0/phase1steps) * np.cov(np.transpose(Zmatrix))
    D = (1.0/phase1steps) * np.matmul(np.transpose(Zmatrix), Zmatrix) - np.matmul(Zmean, np.transpose(Zmean))

    if 1.0/np.linalg.cond(D) < epsilon:
        sys.stdout.write("Covariance matrix is singular: degenerate model\n")
        return None
    D0 = np.diag(D)
    Dinv = np.linalg.inv(D)
    D0inv = 1.0 / D0

    print D #XXX
    print D0 #XXX
    print D0inv #XXX

    theta -= np.transpose(a_initial * np.matmul(Dinv, np.transpose(Zmean - Zobs)))
    
    #
    # Phase 2 (main phase): In each subphase, generate simulated
    # networks according to current parameter (theta) value, and
    # update theta according to Robbins-Monro formula.
    # Terminate when sum within subphase of successive
    # products of statistics is non-negative (or iteration limit).
    # At end of each subphase average theta over subphase is used as
    # new theta value. Value of Robbins-Monro multiplier a is halved
    # between each subphase.
    #
    a = a_initial
    for k in xrange(numSubphases):
        NkMin  = 2**(4 * k / 3) * (7 + n)
        NkMax  = NkMin + 200
        print 'subphase', k, 'a = ', a, 'NkMin = ',NkMin,'NkMax = ',NkMax, 'theta = ', theta
        i = 0
        Z = np.zeros(n)
        sumSuccessiveProducts = np.zeros(n)
        thetaSum = np.zeros((1,n))
        while i < NkMax and (i < NkMax or np.all(sumSuccessiveProducts < 0)):
            print '  subphase', k, 'iteration', i, 'a = ', a, 'theta = ', theta
            oldZ = np.copy(Z)
            Z = np.zeros(n)
            for j in xrange(iterationInStep):
                (acceptance_rate,
                 changeTo1ChangeStats,
                 changeTo0ChangeStats) = basicALAAMsampler(G, A,
                                                           changestats_func_list,
                                                           theta,
                                                           performMove = True,
                                                           sampler_m = iterationInStep)
                Z += changeTo1ChangeStats - changeTo0ChangeStats
            print 'XXX Z = ',Z, 'acceptance rate=',acceptance_rate
            theta -= a * np.matmul(D0inv, Z - Zobs)
            thetaSum += theta
            oldSumSuccessiveProducts = np.copy(sumSuccessiveProducts)
            sumSuccessiveProducts += (Z * oldZ)
            i += 1
        a /= 2.0
        theta = thetaSum / i # average theta

    #
    # Phase 3: Used only to estimate covariance matrix of estimator and
    # check for approximate validity of solution of moment equation.
    # 

    return theta


