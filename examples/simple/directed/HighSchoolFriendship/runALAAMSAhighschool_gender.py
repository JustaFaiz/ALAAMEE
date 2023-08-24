#!/usr/bin/env python3
#
# File:    runALAAMSAhighschool_gender.py
# Author:  Alex Stivala
# Created: May 2023
#
"""Run the python implementation of the Stochastic
 Approximation algorithm for estimation of Autologistic Actor Attribute
 Model (ALAAM) parameters on the SocioPatterns high school frienship network
 with gender as "outcome" variable.

 See ../../../data/directed/HighSchoolFriendship/README.txt 
 for more details.
"""
import estimateALAAMSA
from changeStatisticsALAAMdirected import *
from changeStatisticsALAAM import changeDensity, param_func_to_label

param_func_list =  [changeDensity, changeSender, changeReceiver, changeEgoInTwoStar, changeEgoOutTwoStar, changeContagion]

estimateALAAMSA.run_on_network_attr(
        '../../../data/directed/HighSchoolFriendship/highschool_friendship_arclist.net',
        param_func_list,
        [param_func_to_label(f) for f in param_func_list],
        outcome_bin_filename = '../../../data/directed/HighSchoolFriendship/highschool_friendship_binattr.txt', # 1 means male
        catattr_filename = '../../../data/directed/HighSchoolFriendship/highschool_friendship_catattr.txt',
        directed = True
    )
