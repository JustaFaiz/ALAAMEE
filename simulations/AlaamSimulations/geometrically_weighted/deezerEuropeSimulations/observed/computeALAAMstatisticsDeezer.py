#!/usr/bin/env python3
#
# File:    run computeALAAMstatisticsDeezer.py
# Author:  Alex Stivala
# Created: August 2023
#
"""Compute the observed statistics of specified ALAAM outcome vector
   and network and node attributes.
"""
from  math import log
from functools import partial
import numpy as np         # used for matrix & vector data types and functions

from computeObservedStatistics import get_observed_stats_from_network_attr
from changeStatisticsALAAM import *




##
## main
##
param_func_list = [changeDensity, changeActivity, changeTwoStar, changeThreeStar, changePartnerActivityTwoPath, changeContagion, changeIndirectPartnerAttribute, changePartnerAttributeActivity, changePartnerPartnerAttribute, changeTriangleT1, changeTriangleT2, changeTriangleT3, partial(changeGWActivity, log(2.0)), partial(changeGWContagion, log(2.0)), changeLogContagion]

get_observed_stats_from_network_attr(
        '../../../deezerEuropeSimulations/data//deezer_europe.net',
        param_func_list,
        [param_func_to_label(f) for f in param_func_list],
        '../../../deezerEuropeSimulations/data//deezer_europe_target.txt'  # use gender as outcome variable
)
