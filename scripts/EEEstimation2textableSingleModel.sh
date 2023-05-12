  #!/bin/sh
  #
# File:    EEEstimation2textableSingleModel.sh
# Author:  Alex Stivala
# Created: May 2023
#
# (Copied from estimnetdirectedEstimation2texttableSingleModel.sh March 2019)
#
# Read output of computeALAAMEECovariance.R with the estimate,
# estimated std. error and t-ratio computed from ALAAMEE results
# and build LaTeX table for one model (not using underset etc. for CI, 
# simpler format)
# 
# Usage: EEEstimation2textableSingleModel.sh estimationoutputfile
#
# E.g.:
#   EEEstimation2textableSingleModel.sh  estimation.out
#
# Output is to stdout
#
# Uses various GNU utils options on echo, etc.


zSigma=2 # multiplier of estimated standard error for nominal 95% C.I.
tratioThreshold=0.3 # t-ratio must be <= this for significance

if [ $# -ne 1 ]; then
    echo "usage: $0 estimation.out" >&2
    exit 1
fi

estimationresults=$1

estimnet_tmpfile=`mktemp`

echo "% Generated by: $0 $*"
echo "% At: " `date`
echo "% On: " `uname -a`

echo  '\begin{tabular}{lrrc}'
# echo '\toprule'
echo '\hline'
echo 'Effect & Estimate & Std. error \\'
echo '\hline'
#echo '\midrule'

# new version has results starting at line following "Pooled" at start
# of line (pooling the individual run estimates values printed earlier) and
# 5 columns:
# Effect   estimate   sd(theta)   est.std.err  t.ratio
# (and maybe *) plus
# TotalRuns and ConvergedRuns e.g.:
#Diff_completion_percentage -0.002270358 0.005812427 0.01295886 0.021386
#TotalRuns 2
#ConvergedRuns 2
# (see computeALAAMEECovariance.R)
# https://unix.stackexchange.com/questions/78472/print-lines-between-start-and-end-using-sed
cat ${estimationresults} | sed -n -e '/^Pooled/,${//!p}'  | tr -d '*' | fgrep -vw AcceptanceRate |  awk '{print $1,$2,$4,$5}'  |  tr ' ' '\t' >> ${estimnet_tmpfile}

effectlist=`cat ${estimnet_tmpfile} | grep -wv ConvergedRuns | grep -wv TotalRuns |  awk '{print $1}' | sort | uniq`

for effect in ${effectlist} ConvergedRuns TotalRuns
do
  if [ ${effect} = "ConvergedRuns" ]; then
     echo '\hline'                
  fi
  echo -n "${effect} " | tr '_' ' '
  if [ ${effect} = "ConvergedRuns" -o ${effect} = "TotalRuns" ]; then
        runs=`grep -w ${effect} ${estimnet_tmpfile} | awk '{print $2}'`
        echo -n " & ${runs} & &  "
  else
        estimnet_point=`grep -w ${effect} ${estimnet_tmpfile} | awk '{print $2}'`
        estimnet_stderr=`grep -w ${effect} ${estimnet_tmpfile} | awk '{print $3}'`
        estimnet_tratio=`grep -w ${effect} ${estimnet_tmpfile} | awk '{print $4}'`
        if [ "${estimnet_point}" == "" ];  then
            echo -n " & ---"
        else 
            # bc cannot handle scientific notation so use sed to convert it 
            estimnet_lower=`echo "${estimnet_point} - ${zSigma} * ${estimnet_stderr}" | sed -e 's/[eE]+*/*10^/' | bc -l`
            estimnet_upper=`echo "${estimnet_point} + ${zSigma} * ${estimnet_stderr}" | sed -e 's/[eE]+*/*10^/' | bc -l`
            estimnet_point=`echo "${estimnet_point}" | sed -e 's/[eE]+*/*10^/'`
            estimnet_tratio=`echo "${estimnet_tratio}" | sed -e 's/[eE]+*/*10^/'`
            estimnet_stderr=`echo "${estimnet_stderr}" | sed -e 's/[eE]+*/*10^/'`
            echo AAA "${estimnet_point}">&2
            abs_estimate=`echo "if (${estimnet_point} < 0) -(${estimnet_point}) else ${estimnet_point}" | bc -l`
            abs_tratio=`echo "if (${estimnet_tratio} < 0) -(${estimnet_tratio}) else ${estimnet_tratio}" | bc -l`
            echo YYY ${abs_estimate} >&2
            echo QQQ ${abs_tratio} >&2
            echo XXX "${abs_tratio} <= ${tratioThreshold} && ${abs_estimate} > ${zSigma} * ${estimnet_stderr}" >&2
            signif=`echo "${abs_tratio} <= ${tratioThreshold} && ${abs_estimate} > ${zSigma} * ${estimnet_stderr}" | bc -l`
            echo ZZZ ${signif} >&2
            printf ' & %.3f & %.3f & ' ${estimnet_point} ${estimnet_stderr}
            if [ ${signif} -ne 0 ]; then
      	  echo -n '*'
            fi
        fi
  fi
        echo '\\\\'
done

echo '\hline'
#echo '\bottomrule'
echo '\end{tabular}'

##rm ${estimnet_tmpfile}
