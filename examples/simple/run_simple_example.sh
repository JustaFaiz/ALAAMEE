#!/bin/sh


time python2 ../../python/runALAAMEESimpleDemo.py

Rscript ../../R/plotALAAMEESimpleDemoResults.R  theta_values_n500_kstar_simulate12750000.txt  dzA_values_n500_kstar_simulate12750000.txt

