#!/bin/bash

#SBATCH --job-name="R_Covariance_Github"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=0-00:10:00
#SBATCH --output=alaamee_covariance_Github-%j.out
#SBATCH --error=alaamee_covariance_Github-%j.err
#SBATCH --mem=8GB

echo -n "started at: "; date

#RSCRIPTSDIR=${HOME}/ALAAMEE/R
RSCRIPTSDIR=../../../../R

uname -a

module load gcc/11.3.0 # needed by r/4.2.1
module load openmpi/4.1.4 # needed by r/4.2.1
module load r/4.2.1

time Rscript ${RSCRIPTSDIR}/plotALAAMEEResults.R theta_values_musae_git dzA_values_musae_git


time Rscript ${RSCRIPTSDIR}/computeALAMEEcovariance.R theta_values_musae_git dzA_values_musae_git | tee estimation.txt

times
echo -n "ended at: "; date
